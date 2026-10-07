"""Extract device code objects from HIP binaries and disassemble kernels."""

import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

_INSTRUCTION = re.compile(r"^\t\S")


@dataclass
class KernelCode:
    isa: Optional[str] = None
    # Demangled name and source location of the kernel's first instruction,
    # outside any function inlined there.
    name: Optional[str] = None
    file: Optional[str] = None
    line: Optional[int] = None

    @property
    def instructions(self) -> Optional[int]:
        return instruction_count(self.isa) if self.isa else None


class CodeObject:
    """The AMDGPU code object embedded in a host binary's .hip_fatbin."""

    def __init__(self, binary: str, llvm_bin: str, workdir: str):
        self.llvm_bin = llvm_bin
        self.path: Optional[str] = None
        self.target: Optional[str] = None
        fatbin = os.path.join(workdir, "fatbin.bin")
        dump = subprocess.run(
            [f"{llvm_bin}/llvm-objcopy", f"--dump-section=.hip_fatbin={fatbin}",
             binary, os.devnull],
            capture_output=True, text=True,
        )
        if dump.returncode != 0:
            return
        targets = subprocess.run(
            [f"{llvm_bin}/clang-offload-bundler", "--list", "--type=o",
             f"--input={fatbin}"],
            capture_output=True, text=True,
        ).stdout.split()
        device = [t for t in targets if "amdgcn" in t]
        if not device:
            return
        self.target = device[0]
        self.path = os.path.join(workdir, "device.co")
        subprocess.run(
            [f"{llvm_bin}/clang-offload-bundler", "--unbundle", "--type=o",
             f"--input={fatbin}", f"--targets={self.target}",
             f"--output={self.path}"],
            check=True, capture_output=True,
        )

    @property
    def arch(self) -> Optional[str]:
        return self.target.rsplit("-", 1)[-1] if self.target else None

    def disassemble(self, kernel: str) -> Optional[str]:
        if not self.path:
            return None
        out = subprocess.run(
            [f"{self.llvm_bin}/llvm-objdump", "-d", "--line-numbers",
             "--no-show-raw-insn", f"--disassemble-symbols={kernel}", self.path],
            capture_output=True, text=True,
        ).stdout
        body = out.split(f"<{kernel}>:", 1)
        return body[1].lstrip("\n") if len(body) == 2 else None


    def entry_locations(self, kernels: Iterable[str]) -> Dict[str, Tuple[str, str, int]]:
        if not self.path:
            return {}
        symbols = subprocess.run(
            [f"{self.llvm_bin}/llvm-nm", "--defined-only", self.path],
            capture_output=True, text=True,
        ).stdout.split("\n")
        addresses = {}
        for entry in symbols:
            parts = entry.split()
            if len(parts) == 3 and parts[1] in "Tt" and parts[2] in kernels:
                addresses[parts[2]] = "0x" + parts[0]
        if not addresses:
            return {}
        out = subprocess.run(
            [f"{self.llvm_bin}/llvm-symbolizer", f"--obj={self.path}", "--output-style=JSON",
             "--inlining", "--demangle"],
            input="\n".join(addresses.values()), capture_output=True, text=True,
        ).stdout.splitlines()
        locations = {}
        for kernel, line in zip(addresses, out):
            frames = json.loads(line).get("Symbol", [])
            if frames and frames[-1].get("FileName"):
                outer = frames[-1]
                locations[kernel] = (outer["FunctionName"], outer["FileName"], outer.get("Line") or None)
        return locations


def instruction_count(isa: str) -> int:
    return sum(1 for line in isa.splitlines() if _INSTRUCTION.match(line))


def disassemble_kernels(binary: str, kernels, llvm_bin: str
                        ) -> Tuple[Optional[str], Dict[str, KernelCode]]:
    """Return the device architecture and each kernel's disassembly and location."""
    with tempfile.TemporaryDirectory() as workdir:
        co = CodeObject(binary, llvm_bin, workdir)
        locations = co.entry_locations(kernels)
        return co.arch, {k: KernelCode(co.disassemble(k), *locations.get(k, (None, None, None)))
                         for k in kernels}
