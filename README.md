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
2. **`mneme record`** runs in the same process and records each kernel: its
   LLVM IR, launch instances, memory snapshots, and the source file and line
   range that define it.
3. **`findingmnemo export`** symbolizes the stacks with `llvm-symbolizer`,
   parses the recorded IR (functions, calls, loops via `opt print<loops>`,
   basic blocks with source lines), disassembles each kernel from the
   application's embedded code object, and writes a database directory that
   mirrors the hierarchy, plus a nodes/edges JSON graph.

## Requirements

- AMD GPU with ROCm (tested on Tuolumne, MI300A/gfx942, ROCm 6.4.0).
- A Mneme install with Python support, from a branch that records kernel source
  (`record-source-file` or later). See `examples/env-tuolumne.sh`.
- The application built for Mneme (`add_mneme()` in CMake, or the flags from
  `mneme config cflags` / `ldflags` for Makefiles), with debug info. Prefer
  `-g`: it gives host functions their definition line and host lambdas a name,
  and leaves the device ISA and the recorded IR unchanged (checked on
  XSBench). `-gline-tables-only`, which `add_mneme()` uses, also works.
- Python 3.8+ with only the standard library.

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

Useful `record` options:

- `--no-mneme` captures launch stacks only, for applications Mneme cannot
  record. Kernels then have ISA and call paths but no IR or source span.
- `--mneme-arg=<arg>` passes arguments to `mneme record`, for example
  `--mneme-arg=-vass --mneme-arg=16` for a 16 GB virtual address space.

## Examples

- `examples/mneme-hip-vec-add.sh <mneme-src> <work>` builds and records Mneme's
  `examples/hip_vec_add`.
- `examples/ice4hpc-xsbench.sh <work> [sizes]` builds XSBench (HIP) at the
  commit used by the [ICE4HPC dataset](https://github.com/llnl/ice4hpc_data)
  and records the dataset's GPU configurations (`-m event`, grid types
  `unionized`, `hash`, `nuclide`).
- `examples/xsbench-db/` is the database that script produced for the `small`
  and `large` sizes on Tuolumne (MI300A). Its absolute paths (sources, Mneme
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
│   │       ├── run_event_based_simulation_baseline/function.json
│   │       ├── xs_lookup_kernel_baseline/
│   │       │   ├── function.json   lines 50-105, calls, launched_by, loop/block tree
│   │       │   ├── source.cpp      the kernel's source lines
│   │       │   ├── ir.ll           the kernel's LLVM IR
│   │       │   ├── module.ll       the whole recorded module
│   │       │   ├── isa.s           gfx942 disassembly
│   │       │   └── instances.json  launch configurations Mneme recorded
│   │       ├── calculate_macro_xs/{function.json, ir.ll}
│   │       └── pick_mat/{function.json, ir.ll}
└── xsbench-small-hash/ ...
```

Every function directory has a `function.json`:

| key | meaning |
| --- | --- |
| `kind` | `host`, `kernel` or `device` |
| `name`, `symbol` | demangled name and linkage name (device code only; host frames have no linkage name) |
| `file`, `line`, `end_line` | definition; `end_line` for kernels recorded by Mneme |
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

# The same kernel across inputs.
jq -r '"\(input_filename | split("/")[0]): \(.isa_instructions) instructions"' \
  */files/*/xs_lookup_kernel_baseline/function.json
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
- **Kernels recorded with `--no-mneme`** have no IR, source span or loops. Their
  file comes from the code object's line table, and `entry_line` is the line
  of their first instruction.
- **Mneme aborts on zero-byte `hipMalloc`** ("Destroying memory descriptor
  without releasing device memory ... size=0"). XSBench's `hash` and `nuclide`
  grid types hit this, so the example records them with `--no-mneme`.
- **Host lambdas have no scope or line** with `-gline-tables-only`: the
  debug info names their body `operator()`, and several host lambdas in one
  file end up as `operator()`, `operator()~2`, and so on. Build with `-g`.
- **Kernel templates live where they are defined.** A RAJA or Kokkos kernel
  instantiated with an application lambda is filed under the library header
  that defines the kernel template, and its lambda body under the
  application file.
- **Recorded IR is pre-codegen.** Device functions are still separate in the
  IR but usually inlined in the ISA; the ISA's line annotations map
  instructions back to source.
