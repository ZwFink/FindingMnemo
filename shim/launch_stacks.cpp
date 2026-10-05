// LD_PRELOAD shim that records the host call stack of every HIP kernel launch.
//
// Launches are aggregated by (kernel, grid, block, shared memory, stack) and
// written as JSON when the process exits. Return addresses are stored as
// (module, file-relative address) pairs so they can be symbolized offline with
// llvm-symbolizer against the binaries that were actually loaded.

#include <hip/hip_runtime_api.h>

#include <dlfcn.h>
#include <execinfo.h>
#include <limits.h>
#include <link.h>
#include <unistd.h>

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <map>
#include <mutex>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>

namespace {

constexpr int MaxFrames = 128;

struct LaunchKey {
  std::string Kernel;
  dim3 Grid;
  dim3 Block;
  size_t SharedMem;
  std::vector<uintptr_t> Stack;

  bool operator<(const LaunchKey &Other) const {
    auto Tie = [](const LaunchKey &K) {
      return std::tie(K.Kernel, K.Grid.x, K.Grid.y, K.Grid.z, K.Block.x,
                      K.Block.y, K.Block.z, K.SharedMem, K.Stack);
    };
    return Tie(*this) < Tie(Other);
  }
};

struct State {
  std::mutex Lock;
  std::unordered_map<const void *, std::string> KernelNames;
  std::map<LaunchKey, uint64_t> Launches;
};

// Leaked on purpose so it outlives every other static destructor that might
// still launch kernels during teardown.
State &state() {
  static State *S = new State();
  return *S;
}

template <typename Fn> Fn next(const char *Name) {
  void *Sym = dlsym(RTLD_NEXT, Name);
  if (!Sym) {
    std::fprintf(stderr, "[findingmnemo] cannot resolve %s: %s\n", Name,
                 dlerror());
    std::abort();
  }
  return reinterpret_cast<Fn>(Sym);
}

std::string kernelName(const void *Handle) {
  auto &S = state();
  std::lock_guard<std::mutex> Guard(S.Lock);
  auto It = S.KernelNames.find(Handle);
  if (It != S.KernelNames.end())
    return It->second;
  std::ostringstream OS;
  OS << "<unknown:" << Handle << ">";
  return OS.str();
}

// Set while a launch is being forwarded so launches issued by interposers
// further down the chain, such as Mneme's recorder, are not counted twice.
thread_local bool InLaunch = false;

class LaunchScope {
public:
  LaunchScope() : Outermost(!InLaunch) { InLaunch = true; }
  ~LaunchScope() {
    if (Outermost)
      InLaunch = false;
  }
  bool outermost() const { return Outermost; }

private:
  bool Outermost;
};

__attribute__((noinline)) void recordLaunch(const void *Handle, dim3 Grid, dim3 Block, size_t SharedMem) {
  void *Frames[MaxFrames];
  int Depth = backtrace(Frames, MaxFrames);
  // Skip this function and the intercepted HIP entry point.
  std::vector<uintptr_t> Stack;
  for (int I = 2; I < Depth; ++I)
    Stack.push_back(reinterpret_cast<uintptr_t>(Frames[I]));

  LaunchKey Key{kernelName(Handle), Grid, Block, SharedMem, std::move(Stack)};
  auto &S = state();
  std::lock_guard<std::mutex> Guard(S.Lock);
  ++S.Launches[Key];
}

struct Module {
  std::string Path;
  uintptr_t Bias;
  std::vector<std::pair<uintptr_t, uintptr_t>> Ranges;
};

int collectModule(struct dl_phdr_info *Info, size_t, void *Data) {
  auto *Modules = static_cast<std::vector<Module> *>(Data);
  Module M;
  M.Bias = Info->dlpi_addr;
  if (Info->dlpi_name && Info->dlpi_name[0]) {
    M.Path = Info->dlpi_name;
  } else {
    char Exe[PATH_MAX];
    ssize_t Len = readlink("/proc/self/exe", Exe, sizeof(Exe) - 1);
    M.Path = Len > 0 ? std::string(Exe, Len) : "<main>";
  }
  for (int I = 0; I < Info->dlpi_phnum; ++I) {
    const auto &Ph = Info->dlpi_phdr[I];
    if (Ph.p_type != PT_LOAD)
      continue;
    uintptr_t Begin = Info->dlpi_addr + Ph.p_vaddr;
    M.Ranges.emplace_back(Begin, Begin + Ph.p_memsz);
  }
  Modules->push_back(std::move(M));
  return 0;
}

std::string jsonEscape(const std::string &In) {
  std::string Out;
  for (char C : In) {
    switch (C) {
    case '"':
      Out += "\\\"";
      break;
    case '\\':
      Out += "\\\\";
      break;
    case '\n':
      Out += "\\n";
      break;
    default:
      if (static_cast<unsigned char>(C) < 0x20) {
        char Buf[8];
        std::snprintf(Buf, sizeof(Buf), "\\u%04x", C);
        Out += Buf;
      } else {
        Out += C;
      }
    }
  }
  return Out;
}

std::string readCmdline() {
  std::ifstream In("/proc/self/cmdline", std::ios::binary);
  std::string Raw((std::istreambuf_iterator<char>(In)),
                  std::istreambuf_iterator<char>());
  std::string Out = "[";
  size_t Start = 0;
  bool First = true;
  while (Start < Raw.size()) {
    size_t End = Raw.find('\0', Start);
    if (End == std::string::npos)
      End = Raw.size();
    Out += First ? "" : ",";
    Out += "\"" + jsonEscape(Raw.substr(Start, End - Start)) + "\"";
    First = false;
    Start = End + 1;
  }
  return Out + "]";
}

void writeLog() {
  auto &S = state();
  std::lock_guard<std::mutex> Guard(S.Lock);
  if (S.Launches.empty())
    return;

  std::vector<Module> Modules;
  dl_iterate_phdr(collectModule, &Modules);

  auto Locate = [&](uintptr_t Addr) -> std::pair<int, uintptr_t> {
    for (size_t I = 0; I < Modules.size(); ++I)
      for (const auto &R : Modules[I].Ranges)
        if (Addr >= R.first && Addr < R.second)
          return {static_cast<int>(I), Addr - Modules[I].Bias};
    return {-1, Addr};
  };

  const char *Dir = std::getenv("FINDINGMNEMO_OUT");
  std::ostringstream Path;
  Path << (Dir ? Dir : ".") << "/launches." << getpid() << ".json";
  std::ofstream Out(Path.str());
  if (!Out) {
    std::fprintf(stderr, "[findingmnemo] cannot write %s\n",
                 Path.str().c_str());
    return;
  }

  Out << "{\"pid\":" << getpid() << ",\"cmdline\":" << readCmdline()
      << ",\"modules\":[";
  for (size_t I = 0; I < Modules.size(); ++I)
    Out << (I ? "," : "") << "\"" << jsonEscape(Modules[I].Path) << "\"";
  Out << "],\"launches\":[";
  bool First = true;
  for (const auto &[Key, Count] : S.Launches) {
    Out << (First ? "" : ",") << "{\"kernel\":\"" << jsonEscape(Key.Kernel)
        << "\",\"grid\":[" << Key.Grid.x << "," << Key.Grid.y << ","
        << Key.Grid.z << "],\"block\":[" << Key.Block.x << "," << Key.Block.y
        << "," << Key.Block.z << "],\"shared_mem\":" << Key.SharedMem
        << ",\"count\":" << Count << ",\"stack\":[";
    for (size_t I = 0; I < Key.Stack.size(); ++I) {
      auto [Mod, Offset] = Locate(Key.Stack[I]);
      Out << (I ? "," : "") << "[" << Mod << "," << Offset << "]";
    }
    Out << "]}";
    First = false;
  }
  Out << "]}\n";
}

__attribute__((destructor)) void onUnload() { writeLog(); }

} // namespace

extern "C" {

void __hipRegisterFunction(void **Modules, const void *HostFunction,
                           char *DeviceFunction, const char *DeviceName,
                           unsigned int ThreadLimit, void *Tid, void *Bid,
                           dim3 *BlockDim, dim3 *GridDim, int *WSize) {
  using Fn = void (*)(void **, const void *, char *, const char *,
                      unsigned int, void *, void *, dim3 *, dim3 *, int *);
  static Fn Real = next<Fn>("__hipRegisterFunction");
  {
    auto &S = state();
    std::lock_guard<std::mutex> Guard(S.Lock);
    S.KernelNames[HostFunction] = DeviceName;
  }
  Real(Modules, HostFunction, DeviceFunction, DeviceName, ThreadLimit, Tid,
       Bid, BlockDim, GridDim, WSize);
}

hipError_t hipModuleGetFunction(hipFunction_t *Function, hipModule_t Module,
                                const char *Name) {
  using Fn = hipError_t (*)(hipFunction_t *, hipModule_t, const char *);
  static Fn Real = next<Fn>("hipModuleGetFunction");
  hipError_t Ret = Real(Function, Module, Name);
  if (Ret == hipSuccess) {
    auto &S = state();
    std::lock_guard<std::mutex> Guard(S.Lock);
    S.KernelNames[*Function] = Name;
  }
  return Ret;
}

// Proteus-compiled code, which includes everything built for Mneme, launches
// through this entry point instead of hipLaunchKernel.
hipError_t __proteus_launch_kernel(void *Kernel, dim3 GridDim, dim3 BlockDim,
                                   void **KernelArgs, uint64_t ShmemSize,
                                   void *Stream) {
  using Fn = hipError_t (*)(void *, dim3, dim3, void **, uint64_t, void *);
  static Fn Real = next<Fn>("__proteus_launch_kernel");
  LaunchScope Scope;
  if (Scope.outermost())
    recordLaunch(Kernel, GridDim, BlockDim, ShmemSize);
  return Real(Kernel, GridDim, BlockDim, KernelArgs, ShmemSize, Stream);
}

hipError_t hipLaunchKernel(const void *FunctionAddress, dim3 NumBlocks,
                           dim3 DimBlocks, void **Args, size_t SharedMemBytes,
                           hipStream_t Stream) {
  using Fn = hipError_t (*)(const void *, dim3, dim3, void **, size_t,
                            hipStream_t);
  static Fn Real = next<Fn>("hipLaunchKernel");
  LaunchScope Scope;
  if (Scope.outermost())
    recordLaunch(FunctionAddress, NumBlocks, DimBlocks, SharedMemBytes);
  return Real(FunctionAddress, NumBlocks, DimBlocks, Args, SharedMemBytes,
              Stream);
}

hipError_t hipExtLaunchKernel(const void *FunctionAddress, dim3 NumBlocks,
                              dim3 DimBlocks, void **Args,
                              size_t SharedMemBytes, hipStream_t Stream,
                              hipEvent_t StartEvent, hipEvent_t StopEvent,
                              int Flags) {
  using Fn = hipError_t (*)(const void *, dim3, dim3, void **, size_t,
                            hipStream_t, hipEvent_t, hipEvent_t, int);
  static Fn Real = next<Fn>("hipExtLaunchKernel");
  LaunchScope Scope;
  if (Scope.outermost())
    recordLaunch(FunctionAddress, NumBlocks, DimBlocks, SharedMemBytes);
  return Real(FunctionAddress, NumBlocks, DimBlocks, Args, SharedMemBytes,
              Stream, StartEvent, StopEvent, Flags);
}

hipError_t hipModuleLaunchKernel(hipFunction_t F, unsigned int GridX,
                                 unsigned int GridY, unsigned int GridZ,
                                 unsigned int BlockX, unsigned int BlockY,
                                 unsigned int BlockZ, unsigned int SharedMem,
                                 hipStream_t Stream, void **KernelParams,
                                 void **Extra) {
  using Fn = hipError_t (*)(hipFunction_t, unsigned int, unsigned int,
                            unsigned int, unsigned int, unsigned int,
                            unsigned int, unsigned int, hipStream_t, void **,
                            void **);
  static Fn Real = next<Fn>("hipModuleLaunchKernel");
  LaunchScope Scope;
  if (Scope.outermost())
    recordLaunch(F, dim3(GridX, GridY, GridZ), dim3(BlockX, BlockY, BlockZ),
                 SharedMem);
  return Real(F, GridX, GridY, GridZ, BlockX, BlockY, BlockZ, SharedMem,
              Stream, KernelParams, Extra);
}

} // extern "C"
