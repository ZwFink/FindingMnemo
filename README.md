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
   application's embedded code object, and writes SQLite plus a nodes/edges
   JSON graph.

## Requirements

- AMD GPU with ROCm (tested on Tuolumne, MI300A/gfx942, ROCm 6.4.0).
- A Mneme install with Python support, from a branch that records kernel source
  (`record-source-file` or later). See `examples/env-tuolumne.sh`.
- The application built for Mneme (`add_mneme()` in CMake, or the flags from
  `mneme config cflags` / `ldflags` plus `-gline-tables-only` for Makefiles).
- Python 3.8+ with only the standard library.

## Quick start

```bash
make ROCM_PATH=/opt/rocm-6.4.0            # builds lib/libfindingmnemo_stacks.so
export MNEME_PREFIX=/path/to/mneme/install
source examples/env-tuolumne.sh

findingmnemo record -o runs/myapp -- ./myapp args...
findingmnemo export runs/myapp            # runs/myapp/findingmnemo.sqlite + .graph.json
```

Several runs, for example one application with different inputs, can go into
one database; each becomes a separate program:

```bash
findingmnemo export runs/app-small runs/app-large --db app.sqlite
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

For XSBench `-m event -s small -G unionized` the graph contains:

```
program: XSBench
  source_file: Main.cpp
    host_function: main  -calls-> run_event_based_simulation_baseline @ Main.cpp:65
  source_file: Simulation.cpp
    host_function: run_event_based_simulation_baseline  -launches-> xs_lookup_kernel_baseline @ :26
    kernel_function: xs_lookup_kernel_baseline  (lines 50-105, 814 gfx942 instructions)
      -calls-> fast_forward_LCG @62, LCG_random_double @65, pick_mat @66, calculate_macro_xs @71
      loop: for.cond [4 blocks]
    device_function: calculate_macro_xs  -calls-> grid_search @214, calculate_micro_xs @236
      loop: for.cond7 ...
```

## Database

| table | one row per |
| --- | --- |
| `programs` | recorded run: executable, arguments, host, GPU architecture |
| `source_files` | file that defines a function |
| `functions` | host, kernel or device function (`kind`); `is_runtime` marks HIP helpers |
| `call_edges` | caller → callee; `origin` is `stack`, `launch` or `ir`; `launches` counts kernel launches through dynamic edges |
| `kernels` | kernel: source span and text, IR, ISA, instruction count, raw Mneme record |
| `kernel_instances` | launch configuration Mneme recorded (at most `--per-kernel-max-recordings`, default 4) |
| `launch_paths` | every launch, aggregated by host call path and configuration |
| `loops` | loop in a function, with its parent loop |
| `basic_blocks` | basic block: instruction count, innermost loop, source lines, callees |

Example queries:

```sql
-- Which host call paths launch each kernel, and how often.
SELECT k.demangled_name, lp.frames, lp.grid_x, lp.block_x, lp.count
FROM launch_paths lp JOIN kernels k ON k.id = lp.kernel_id;

-- Device call graph of one program, without HIP runtime helpers.
SELECT a.display_name AS caller, b.display_name AS callee, e.call_line
FROM call_edges e
JOIN functions a ON a.id = e.caller_id
JOIN functions b ON b.id = e.callee_id
WHERE e.origin = 'ir' AND NOT b.is_runtime AND a.program_id = 1;

-- Loop nests and their size, per function.
SELECT f.display_name, l.depth, l.header, COUNT(bb.id) AS blocks, SUM(bb.instructions) AS instructions
FROM loops l JOIN functions f ON f.id = l.function_id
LEFT JOIN basic_blocks bb ON bb.loop_id = l.id
GROUP BY l.id;

-- Match recorded (replayable) instances to the call paths that produced them.
SELECT k.demangled_name, i.dynamic_hash, i.prologue, lp.frames
FROM kernel_instances i
JOIN kernels k ON k.id = i.kernel_id
JOIN launch_paths lp ON lp.kernel_id = k.id
  AND (lp.grid_x, lp.grid_y, lp.grid_z, lp.block_x, lp.block_y, lp.block_z, lp.shared_mem)
    = (i.grid_x, i.grid_y, i.grid_z, i.block_x, i.block_y, i.block_z, i.shared_mem);
```

The graph JSON (`{"nodes": [...], "edges": [...]}`) loads directly into
NetworkX or a graph database:

```python
import json, networkx as nx
g = json.load(open("xsbench.graph.json"))
G = nx.MultiDiGraph()
G.add_nodes_from((n["id"], n) for n in g["nodes"])
G.add_edges_from((e["source"], e["target"], e) for e in g["edges"])
```

`export --include-runtime` keeps HIP runtime helpers (`__ockl_*`,
`__hip_get_*`) in the graph; they are always in the database.

## Limitations

- **Host call graph is partial.** Only host functions on a path to a kernel
  launch appear. Tail calls can hide frames (the compiler-generated device
  stub is one), and frames need debug line info to get file and line.
- **HIP only.** A CUDA port needs the same shim for `cudaLaunchKernel` /
  `__cudaRegisterFunction` and `cuobjdump` instead of `clang-offload-bundler`.
- **ISA comes from the main executable.** Kernels in shared libraries get call
  paths and IR but no ISA.
- **Mneme aborts on zero-byte `hipMalloc`** ("Destroying memory descriptor
  without releasing device memory ... size=0"). XSBench's `hash` and `nuclide`
  grid types hit this, so the example records them with `--no-mneme`.
- **Recorded IR is pre-codegen.** Device functions are still separate in the
  IR but usually inlined in the ISA; the ISA's line annotations map
  instructions back to source.
