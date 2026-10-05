"""Read launch-stack logs written by the shim and symbolize them."""

import glob
import json
import os
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Frames from these libraries belong to the HIP runtime, the C runtime or the
# interposers themselves, not to the application.
_RUNTIME_LIBRARIES = (
    "libfindingmnemo_stacks.so",
    "librecord.so",
    "libmnemert.so",
    "libproteus.so",
    "libamdhip64.so",
    "libc.so",
    "ld-linux",
)


@dataclass(frozen=True)
class Frame:
    function: str
    file: Optional[str]
    line: Optional[int]
    # Line where the function is defined, when the debug info says so.
    start_line: Optional[int]
    module: str


@dataclass
class LaunchPath:
    kernel: str
    grid: Tuple[int, int, int]
    block: Tuple[int, int, int]
    shared_mem: int
    count: int
    # Outermost frame first, ending at the frame that launched the kernel.
    frames: List[Frame]


def _symbolize(module: str, offsets: List[int], llvm_bin: str) -> Dict[int, List[dict]]:
    if not offsets:
        return {}
    proc = subprocess.run(
        [f"{llvm_bin}/llvm-symbolizer", f"--obj={module}", "--output-style=JSON",
         "--inlining", "--demangle"],
        input="\n".join(hex(o) for o in offsets), capture_output=True, text=True,
    )
    results = {}
    for offset, line in zip(offsets, proc.stdout.splitlines()):
        results[offset] = json.loads(line).get("Symbol", [])
    return results


def _is_runtime(module: str) -> bool:
    return any(lib in os.path.basename(module) for lib in _RUNTIME_LIBRARIES)


def load_launch_paths(stack_dir: str, llvm_bin: str) -> List[LaunchPath]:
    paths = []
    for log_file in sorted(glob.glob(os.path.join(stack_dir, "launches.*.json"))):
        with open(log_file) as f:
            log = json.load(f)
        modules = log["modules"]

        # Return addresses point after the call; step back one byte so the
        # symbolizer reports the call instruction's line.
        wanted = defaultdict(set)
        for launch in log["launches"]:
            for mod, offset in launch["stack"]:
                if mod >= 0 and not _is_runtime(modules[mod]):
                    wanted[mod].add(offset - 1)
        symbols = {mod: _symbolize(modules[mod], sorted(offs), llvm_bin)
                   for mod, offs in wanted.items()}

        for launch in log["launches"]:
            frames = []
            for mod, offset in launch["stack"]:
                if mod < 0 or _is_runtime(modules[mod]):
                    continue
                for sym in symbols[mod].get(offset - 1, []):
                    name = sym.get("FunctionName") or "??"
                    if name.startswith("__device_stub__"):
                        continue
                    frames.append(Frame(
                        function=name,
                        file=sym.get("FileName") or None,
                        line=sym.get("Line") or None,
                        start_line=sym.get("StartLine") or None,
                        module=modules[mod],
                    ))
                if frames and frames[-1].function == "main":
                    break
            paths.append(LaunchPath(
                kernel=launch["kernel"],
                grid=tuple(launch["grid"]),
                block=tuple(launch["block"]),
                shared_mem=launch["shared_mem"],
                count=launch["count"],
                frames=list(reversed(frames)),
            ))
    return paths
