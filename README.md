# FindingMnemo

FindingMnemo builds a hierarchical database of GPU program executions. It runs
an application under [Mneme](https://github.com/LLNL/Mneme), records which host
call path launched each kernel, and joins the two with the kernel's source,
LLVM IR and GPU assembly:

```
program
 └─ source file
     ├─ host function ── calls ──▶ host function ── launches ──▶ kernel
     └─ kernel / device function ── calls ──▶ device function
         ├─ kernel instance (recorded launch configuration, replayable by Mneme)
         └─ loop
             └─ loop / basic block (instructions, source line range)
```

Containment edges (`contains`) give the tree program → file → function → loop →
basic block. Call edges cross it: host edges are *dynamic* (observed on the way
to a kernel launch), device edges are *static* (from the recorded IR).

## How it works

1. **`shim/launch_stacks.cpp`** is an `LD_PRELOAD` library. It intercepts HIP
   kernel launches (`hipLaunchKernel`, `hipModuleLaunchKernel`,
   `hipExtLaunchKernel`, and Proteus's `__proteus_launch_kernel`, which is how
   Mneme-built applications launch) and aggregates the host stack of every
   launch by kernel and launch configuration. It writes
   `stacks/launches.<pid>.json` at exit.
2. **`mneme record --copy-source`** runs in the same process and records each
   kernel: its LLVM IR, launch instances, memory snapshots, the source file and
   line range that define it, and a copy of that source file.
3. **`findingmnemo export`** symbolizes the stacks with `llvm-symbolizer`,
   parses the recorded IR (functions, calls, loops via `opt print<loops>`,
   basic blocks with source lines), reruns each recorded compile unit's
   preprocessor to cut each kernel's and device function's source as the
   device compiled it (see [Device source](#device-source)), disassembles each
   kernel from the application's embedded code object, and writes a database
   directory that mirrors the hierarchy, plus a nodes/edges JSON graph.

## Requirements

- AMD GPU with ROCm (tested on Tuolumne, MI300A/gfx942, ROCm 6.4.0).
- An up-to-date Mneme install (`develop`) with Python support
  (`MNEME_ENABLE_PYTHON=On`). See `examples/env-tuolumne.sh`.
- The application built for Mneme (`add_mneme()` in CMake, or the flags from
  `mneme config cflags` / `ldflags` for Makefiles), with debug info. Prefer
  `-g`: it gives host functions their definition line and host lambdas a name,
  and leaves the device ISA and the recorded IR unchanged (checked on
  XSBench). `-gline-tables-only`, which `add_mneme()` uses, also works.
- `-grecord-command-line`, which stores the compile command in the debug
  info so the export can resolve `#if`s the way the device compile did. It
  adds a few hundred bytes per module. Without it, the export fails.
- Python 3.8+ with Mneme's Python package (`mneme.recorded_execution`) on
  `PYTHONPATH`; everything else is the standard library.

## Quick start

```bash
make ROCM_PATH=/opt/rocm-6.4.0            # builds lib/libfindingmnemo_stacks.so
export MNEME_PREFIX=/path/to/mneme/install
source examples/env-tuolumne.sh

findingmnemo record -o runs/myapp -- ./myapp args...
findingmnemo export runs/myapp            # writes runs/myapp/findingmnemo-db/
```

Several runs, for example one application with different inputs, can go into
one database; each becomes a separate program directory:

```bash
findingmnemo export runs/app-small runs/app-large -o app-db
```

`--mneme-arg=<arg>` passes arguments to `mneme record`, for example
`--mneme-arg=-vass --mneme-arg=16` for a 16 GB virtual address space.

## Examples

- `examples/mneme-hip-vec-add.sh <mneme-src> <work>` builds and records Mneme's
  `examples/hip_vec_add`.
- `examples/ice4hpc-xsbench.sh <work> [sizes]` builds XSBench (HIP) at the
  commit used by the [ICE4HPC dataset](https://github.com/llnl/ice4hpc_data)
  and records it with `-m event -G unionized`.
- `examples/xsbench-db/` is the database that script produced for the `small`
  size on Tuolumne (MI300A). It includes `Simulation.cpp`, which
  Mneme copied when it recorded the kernel. Its absolute paths (sources, Mneme
  records, snapshots) point to where it was recorded; the Mneme recordings
  themselves are not in the repository.

## Database layout

The database is a directory tree that follows the hierarchy, so `ls`, `tree`,
an editor or `jq` show what is in it. For the XSBench example
(`examples/xsbench-db`):

```
xsbench-db/
├── index.json                  format version and the list of programs
├── graph.json                  nodes/edges graph of every program
├── xsbench-small-unionized/    one directory per recorded run
│   ├── program.json            executable, arguments, host, GPU architecture, kernels
│   ├── launches.json           every launch: kernel, host call path, grid, block, count
│   ├── files/                  application source files
│   │   ├── Main.cpp/
│   │   │   ├── file.json       full path of the source file
│   │   │   └── main/function.json
│   │   └── Simulation.cpp/
│   │       ├── source.cpp      the file as Mneme recorded it
│   │       ├── run_event_based_simulation_baseline/function.json
│   │       ├── xs_lookup_kernel_baseline/
│   │       │   ├── function.json   lines 50-105, calls, launched_by, loop/block tree
│   │       │   ├── source.cpp      the kernel's lines of that file
│   │       │   ├── ir.ll           the kernel's LLVM IR
│   │       │   ├── module.ll       the whole recorded module
│   │       │   ├── isa.s           gfx942 disassembly
│   │       │   └── instances.json  launch configurations Mneme recorded
│   │       ├── calculate_macro_xs/{function.json, source.cpp, ir.ll}
│   │       └── pick_mat/{function.json, source.cpp, ir.ll}
```

Every function directory has a `function.json`:

| key | meaning |
| --- | --- |
| `kind` | `host`, `kernel` or `device` |
| `name`, `symbol` | demangled name and linkage name (device code only; host frames have no linkage name) |
| `file`, `line`, `end_line` | definition; `end_line` (the closing brace) for kernels and device functions recorded by Mneme |
| `source_arch` | the GPU architecture whose compile `source.<ext>` shows |
| `compiler_generated` | `true` for device code the compiler wrote, such as a copy constructor the class does not declare; it has no `source.<ext>` or `end_line`, and `line` is where the debug info puts it, a line naming the class |
| `calls`, `called_by` | call sites: `function`, `at` (its directory), `line`, and `launch_count` for host calls seen on the way to a launch |
| `launches`, `launched_by` | host function ↔ kernel launch sites with `launch_count` |
| `body` | basic blocks nested in loops, in IR order: `{"block", "instructions", "lines": [first, last], "calls"}` and `{"loop", "depth", "body"}` |
| `isa_instructions`, `static_hash`, `mneme_record` | kernels only |

Host call edges are *dynamic* (observed on the way to a kernel launch);
device call edges are *static* (from the recorded IR). `at` paths are relative
to the program directory. HIP runtime helpers that device code calls
(`__ockl_*`, `__hip_get_*`, functions from `include/hip/`) are left out.

### Function directory names

A function's directory is named after its debug-info name, which clang writes
the same way for host and device code, without parameters or return type. A
few rules keep the names short and usable on any file system:

| source | debug-info name | directory |
| --- | --- | --- |
| `ns::run(int)` | `run` | `run` |
| `template <class B> __global__ void forall(int, B)` with the lambda on line 28 | `forall<(lambda at app.hip:28:13)>` | `forall[lambda@28]` |
| the same with a lambda from `other.hip` | `forall<(lambda at other.hip:7:3)>` | `forall[lambda@other.hip-7]` |
| a device lambda's body, `[=] __device__ (int i) {...}` on line 28 | `operator()` | `lambda@28` |
| a host lambda's body on line 31, built with `-g` | `main::'lambda'(double, int)::operator()` | `lambda@31` |
| the same with `-gline-tables-only` | `operator()` | `operator()` |

- Template brackets become `[]`, `::` becomes `.`, and other characters that
  are awkward in paths become `_`.
- Names longer than 80 characters (RAJA kernels, for example) keep only the
  lambdas among their template arguments: `forall_hip_kernel[lambda@41]`, or
  `[...]` when there are none.
- If two functions in a file still get the same name (overloads), the
  directory falls back to the mangled symbol.

With `-g`, host frames carry demangled names (`launch<main::'lambda'(int)>`)
instead of clang's `(lambda at ...)` spelling; a lambda whose body is in the
database is still written `lambda@<line>` wherever it appears. The full
demangled name is always in `function.json`. A kernel's `forall[lambda@28]` and
the device function `lambda@28` that it calls are the same lambda, so its body
is easy to find from the kernel.

### Device source

A file's `source.<ext>` is the file as written. A kernel's or device
function's `source.<ext>` is the function as the device compiled it: the
export reads the command of the compile the function came from in the
recorded module's debug info (a module linked from several files, as in a HIP
`-fgpu-rdc` build, has one for each file), reruns it with
`-E -fdirectives-only` for the module's GPU architecture, which handles
directives but leaves macros alone, and uses the preprocessor's line markers to
line its output up with the original file. In the function's source,

- branches of `#if`, `#ifdef` and friends that the device compile did not take
  (because of `-D` flags, `__HIP_DEVICE_COMPILE__`, `__gfx942__`, ...) and the
  directives themselves are blank lines,
- everything else, `#pragma` lines included, is as written, macros too,

so line numbers from the debug info (`line`, `end_line`, block `lines`) still
apply. The text comes from the file, since clang prints code with its
whitespace changed. For example, as written and as the device compiled it:

```
__device__ double helper(double a) {          __device__ double helper(double a) {
#if defined(__HIP_DEVICE_COMPILE__)
  return transform(a);                  -->     return transform(a);
#else
  return 0.0;
#endif
}                                             }
```

The function ends at the brace that closes it, counting only the code the
device compiled, with macros expanded by a second, ordinary `-E`. Before
preprocessing, the export checks each file against the MD5 in the debug info
and fails if one changed since the build. It needs the recorded compiler,
headers and compile directory at their recorded paths.

The recorded command is rerun as it was, with `-E`, `-o -` and the module's
architecture appended; the driver lets these win over the build's own `-c`,
`-o` and `--offload-arch`. Only options that would still change what is
printed or write a file (`-M`, `-MD`, `-P`, `-dM`, ...), frontend plugins
(Proteus's `-fplugin=`) and `-mllvm` options, and the device-only `-mcpu=` are
removed. After preprocessing, the export checks the view against the debug
info: if any line the IR attributes code to is one the view says was not
compiled, the view is wrong (the file was preprocessed differently from the
build) and the export fails. The export also fails, naming the function or
file and the reason, whenever a kernel's or device function's source cannot be
cut this way: the debug info has no command line or no source location for
it, preprocessing fails, its file is not part of the recorded compile, or
where it begins or its closing brace is not found. It never falls back to the source as written.
Device code the compiler wrote, such as a copy constructor the class does not
declare, has no text to cut; it has `"compiler_generated": true` instead of a
source.

Example queries:

```bash
cd xsbench-db
# Which host call paths launch each kernel, and how often.
jq -r '.[] | "\(.kernel) x\(.count): " + ([.call_path[].function] | join(" -> "))' \
  xsbench-small-unionized/launches.json

# Call graph of one program.
jq -r '.name as $f | .calls[]? | "\($f) -> \(.function) @\(.line)"' \
  xsbench-small-unionized/files/*/*/function.json

# Loop nests and IR size per function.
jq -r 'select(.body) | "\(.name): depth \([.. | objects | select(.loop) | .depth] | max // 0), "
  + "\([.. | objects | select(.block) | .instructions] | add) IR instructions"' \
  xsbench-small-unionized/files/*/*/function.json
```

`graph.json` (`{"nodes": [...], "edges": [...]}`) holds the same hierarchy for
graph tools. Node ids are paths in the database (`#loop:`, `#block:` and
`#instance:` name the parts of a function), and edge kinds are `contains`,
`calls`, `launches` and `has_instance`:

```python
import json, networkx as nx
g = json.load(open("xsbench-db/graph.json"))
G = nx.MultiDiGraph()
G.add_nodes_from((n["id"], n) for n in g["nodes"])
G.add_edges_from((e["source"], e["target"], e) for e in g["edges"])
```

## Limitations

- **Host call graph is partial.** Only host functions on a path to a kernel
  launch appear. Tail calls can hide frames (the compiler-generated device
  stub is one), and frames need debug line info to get file and line.
- **HIP only.** A CUDA port needs the same shim for `cudaLaunchKernel` /
  `__cudaRegisterFunction` and `cuobjdump` instead of `clang-offload-bundler`.
- **ISA comes from the main executable.** Kernels in shared libraries get call
  paths and IR but no ISA.
- **Kernels that Mneme did not record**, such as those from libraries not
  built for Mneme, have no IR, source span or loops. Their file comes from the
  code object's line table, and `entry_line` is the line of their first
  instruction.
- **Host lambdas have no scope or line** with `-gline-tables-only`: the
  debug info names their body `operator()`, and several host lambdas in one
  file end up as `operator()`, `operator()~2`, and so on. Build with `-g`.
- **Kernel templates live where they are defined.** A RAJA or Kokkos kernel
  instantiated with an application lambda is filed under the library header
  that defines the kernel template, and its lambda body under the
  application file.
- **Only files that define recorded kernels are copied.** Mneme copies the
  translation unit of each kernel it records; other files, such as those with
  only host code, are referenced by path in `file.json`.
- **Function ends come from brace matching.** The debug info records where a
  function starts, not where it ends, and only by line. The export finds the
  function on its start line, at its name or, for a lambda, at the `[` of the
  only lambda that starts there, and scans from there to the closing brace
  (skipping comments, literals, default-argument initializers and member
  initializers). If either step fails, or the end would come before the
  function's last line of code, the export fails.
- **Device views need the build environment.** Preprocessing again needs the
  compiler, headers and compile directory at their recorded paths, and
  environment variables that affected the build are not recorded. The check
  against the debug info catches a wrong view only where a branch with code
  in it differs; a macro with another value but the same branches taken goes
  unnoticed. Files with `#line` directives, whose debug-info line numbers do
  not refer to the file itself, commands that compile several sources at
  once, and builds with `-save-temps` (whose debug info checksums the
  temporary preprocessed file) make the export fail.
- **Recorded IR is pre-codegen.** Device functions are still separate in the
  IR but usually inlined in the ISA; the ISA's line annotations map
  instructions back to source.
