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
   line range that define it, a copy of that source file, and how many times
   the kernel was launched and for how long. `findingmnemo record` sets
   `MNEME_KERNEL_TIMING=profiler` for the GPU durations unless it is already
   set; set it to `off` to record under another profiler such as `rocprofv3`,
   which Mneme cannot share the vendor profiler with.
3. **`findingmnemo export`** symbolizes the stacks with `llvm-symbolizer`,
   parses the recorded IR (functions, calls, loops via `opt print<loops>`,
   basic blocks with source lines), reruns each recorded compile unit's
   preprocessor to cut each kernel's and device function's source as the
   device compiled it (see [Device source](#device-source)), disassembles each
   kernel from the application's embedded code objects (one per translation
   unit without `-fgpu-rdc`), and writes a database directory that mirrors the
   hierarchy, plus a nodes/edges JSON graph.

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

### Copying a database

Paths in a database are relative to it, so it can be copied or moved as is.
Source files are named by their directory in the database (`files/<file>`),
which holds a copy of the file; Mneme records and snapshots (`mneme_record`,
and `prologue`/`epilogue` in `instances.json`) are relative to the program's
`run_dir`. The only absolute paths are where things came from: `run_dir` and
`executable` in `program.json`, and `original_path` in each `file.json`.

`run_dir` is the Mneme recording and launch stacks, which stay where they were
recorded. To take them along, for example to share the database:

```bash
findingmnemo copy app-db /shared/app-db --recordings
```

`--recordings` copies each program's run directory (`run.json`, `stacks/`,
`record-db/`) into `<program>/recording/` of the new database and sets
`run_dir` to `recording`; a relative `run_dir` is relative to the program
directory. The instances then stay replayable from the copy alone. Other files
in the run directory, such as the application's inputs, are not copied.
Recordings can be large (tens of GB for a run that snapshots a big memory
pool). The original database is not changed. Exporting a copied recording
again still needs the application's source and build directories, and its
compiler, at their recorded paths, because export reruns the compile commands
recorded in the device code.

## Examples

- `examples/mneme-hip-vec-add.sh <mneme-src> <work>` builds and records Mneme's
  `examples/hip_vec_add`.
- `examples/ice4hpc-xsbench.sh <work> [sizes]` builds XSBench (HIP) at the
  commit used by the [ICE4HPC dataset](https://github.com/llnl/ice4hpc_data)
  and records it with `-m event -G unionized`.
- `examples/xsbench-db/` is the database that script produced for the `small`
  size on Tuolumne (MI300A). It includes `Simulation.cpp`, which
  Mneme copied when it recorded the kernel. Its `run_dir` points to where it
  was recorded; the Mneme recordings themselves are not in the repository.

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
│   ├── graph.json              this program's part of the top-level graph.json
│   ├── files/                  application source files
│   │   ├── Main.cpp/
│   │   │   ├── file.json       original path, "source_copied": "export-unchecked"
│   │   │   ├── source.cpp      the file as the export read it
│   │   │   └── main/function.json
│   │   └── Simulation.cpp/
│   │       ├── file.json       original path, "source_copied": "record"
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

Every source file the database names (where functions are defined, and the
files of call sites and launch call paths) has a directory under `files/`, and
`file`, in `function.json`, call sites and `launches.json`, is that directory,
relative to the program directory. Its `file.json` has the file's
`original_path`, and the whole file is in `source.<ext>`, with `source_copied`
saying where it came from: `record` for a file Mneme copied when it recorded a
kernel defined there, `export` for one the export read from its original path
and checked against the device compile (see below), such as an application
file whose device lambdas a RAJA or MFEM kernel template in a library header
runs, and `export-unchecked` for one read from its original path with nothing
to check it against, such as a file with only host code; that one also has
`"modified_after_recording": true` if the file changed after the recording. A
file the export could not read has no `source.<ext>` or `source_copied`.

Every function directory has a `function.json`:

| key | meaning |
| --- | --- |
| `kind` | `host`, `kernel` or `device` |
| `name`, `symbol` | demangled name and linkage name (device code only; host frames have no linkage name) |
| `file`, `line`, `end_line` | definition: the file's directory, such as `files/app.hip`, and lines; `end_line` (the closing brace) for kernels and device functions recorded by Mneme |
| `source_arch` | the GPU architecture whose compile `source.<ext>` shows |
| `compiler_generated` | `true` for device code the compiler wrote, such as a copy constructor the class does not declare; it has no `source.<ext>` or `end_line`, and `line` is where the debug info puts it, a line naming the class |
| `calls`, `called_by` | call sites: `function`, `at` (its directory), `line`, `file` if the call is in another file, and `launch_count` for host calls seen on the way to a launch |
| `launches`, `launched_by` | host function ↔ kernel launch sites with `launch_count` |
| `body` | basic blocks nested in loops, in IR order: `{"block", "instructions", "lines": [first, last], "calls"}` and `{"loop", "depth", "body"}` |
| `isa_instructions`, `static_hash`, `mneme_record` | kernels only; `mneme_record` is relative to the program's `run_dir` |
| `launch_count`, `gpu_time_ns` | kernels Mneme recorded: how many times the kernel was launched during the run and the summed GPU duration of those launches in nanoseconds, from Mneme's `TotalLaunches` and `TotalTimeNs` |

Host call edges are *dynamic* (observed on the way to a kernel launch);
device call edges are *static* (from the recorded IR). `at` paths are relative
to the program directory. HIP runtime helpers that device code calls
(`__ockl_*`, `__hip_get_*`, functions from `include/hip/`) and functions from
clang's own headers (`__clang_hip_math.h`, `__clang_hip_cmath.h`, ... in
`lib/clang/<version>/include/`) are left out.

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

A file's `source.<ext>` is the file as written; one the export read
(`"source_copied": "export"`) is the text its functions' sources were cut
from, after the MD5 check below. A kernel's or device function's
`source.<ext>` is the function as the device compiled it: the
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
device compiled, with macros expanded by a second, ordinary `-E`. A function
in a macro argument, such as the lambda body in
`MFEM_FORALL_2D(e, NE, Q1D, Q1D, 1, { ... });`, ends with the macro call, at
its closing `)`. Before
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
`calls`, `launches` and `has_instance`. A function's `file` and a call edge's
`call_file` are the id of a `source_file` node, whose `source` is its copy of
the file. Each program directory also has a `graph.json` with only that
program's nodes and edges, under the same ids:

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
  paths and IR but no ISA. A kernel with internal linkage, such as a template
  from a header, can be in the code object of several translation units.
  Copies whose instructions differ only in the offsets from the PC to the
  functions and variables they use are the same code; if they compiled it
  differently, the ISA is the one from the translation unit
  Mneme recorded, and a kernel Mneme did not record gets none. If Mneme
  recorded the kernel from more than one of them, the export still shows one
  kernel, from the record it reads last, and its launches from all of them.
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
- **Host source is not checked against the build.** A file with only host
  code is copied from its original path when the database is exported, so it
  can differ from what was built if it changed since; `file.json` then says
  `"modified_after_recording": true` (from the file's modification time).
- **Function ends come from brace matching.** The debug info records where a
  function starts, not where it ends, and only by line. The export finds the
  function on its start line, at its name or, for a lambda, at the `[` of the
  only lambda that starts there, and scans from there to the closing brace
  (skipping comments, literals, default-argument initializers and member
  initializers). If either step fails, or the end would come before the
  function's last line of code, the export fails.
- **Code in a macro argument has the macro call's line.** Clang gives
  everything in a macro's expansion, arguments included, the line of the
  macro's name, so a device function written in a macro argument, such as
  the lambda body passed to `MFEM_FORALL_2D`, has its line, blocks, loops and
  calls all on the macro call's line. Its `source.<ext>` holds the whole macro
  call, but its code cannot be mapped to lines within it, and two lambdas in
  one macro call cannot be told apart, so the export fails on them. Fixing
  that needs either a compiler change that keeps the lines where the code is
  written, or source written without the macro (for example `mfem::forall`).
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
