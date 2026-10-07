"""Extract device code objects from HIP binaries and disassemble kernels."""

import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple

_INSTRUCTION = re.compile(r"^\t\S")
_BUNDLE_MAGIC = b"__CLANG_OFFLOAD_BUNDLE__"


@dataclass
class KernelCode:
    isa: Optional[str] = None
    # Demangled name and source location of the kernel's first instruction,
    # outside any function inlined there.
    name: Optional[str] = None
    file: Optional[str] = None
    line: Optional[int] = None
    # The main file of the compile unit of the code object it is in.
    unit: Optional[str] = None

    @property
    def instructions(self) -> Optional[int]:
        return instruction_count(self.isa) if self.isa else None


def bundles(fatbin: bytes) -> List[bytes]:
    """Split a .hip_fatbin into its offload bundles.

    Without relocatable device code, each translation unit has its own bundle,
    and the linker places them one after another in the section.
    """
    starts = []
    i = fatbin.find(_BUNDLE_MAGIC)
    while i >= 0:
        starts.append(i)
        i = fatbin.find(_BUNDLE_MAGIC, i + 1)
    if not starts:
        return [fatbin]
    return [fatbin[s:e] for s, e in zip(starts, starts[1:] + [len(fatbin)])]


class CodeObject:
    """The AMDGPU code object in one offload bundle of a host binary's .hip_fatbin."""

    def __init__(self, bundle: str, llvm_bin: str, path: str):
        self.llvm_bin = llvm_bin
        self.path: Optional[str] = None
        self.target: Optional[str] = None
        targets = subprocess.run(
            [f"{llvm_bin}/clang-offload-bundler", "--list", "--type=o",
             f"--input={bundle}"],
            capture_output=True, text=True,
        ).stdout.split()
        device = [t for t in targets if "amdgcn" in t]
        if not device:
            return
        self.target = device[0]
        unbundle = subprocess.run(
            [f"{llvm_bin}/clang-offload-bundler", "--unbundle", "--type=o",
             f"--input={bundle}", f"--targets={self.target}", f"--output={path}"],
            capture_output=True,
        )
        if unbundle.returncode == 0:
            self.path = path

    @property
    def arch(self) -> Optional[str]:
        return self.target.rsplit("-", 1)[-1] if self.target else None

    def unit(self) -> Optional[str]:
        """The main file of the code object's compile unit, as an absolute path."""
        out = subprocess.run(
            [f"{self.llvm_bin}/llvm-dwarfdump", "--debug-info", "--recurse-depth=0", self.path],
            capture_output=True, text=True,
        ).stdout
        name = re.search(r'DW_AT_name\s+\("([^"]*)"\)', out)
        directory = re.search(r'DW_AT_comp_dir\s+\("([^"]*)"\)', out)
        if not name:
            return None
        return os.path.normpath(os.path.join(directory.group(1) if directory else "", name.group(1)))

    def kernels(self) -> Set[str]:
        if not self.path:
            return set()
        symbols = subprocess.run(
            [f"{self.llvm_bin}/llvm-nm", "--defined-only", self.path],
            capture_output=True, text=True,
        ).stdout.split("\n")
        return {parts[2] for parts in map(str.split, symbols)
                if len(parts) == 3 and parts[1] in "Tt"}

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


def _instructions(isa: Optional[str]) -> List[str]:
    """The instructions without the addresses and encodings in their comments."""
    return [re.sub(r"\s*//.*$", "", line) for line in (isa or "").splitlines()
            if _INSTRUCTION.match(line)]


def choose(codes: List[KernelCode], units: Iterable[str] = ()) -> Optional[KernelCode]:
    """The code of a kernel from the code objects that have it, or None if it
    can't be told which one ran.

    A kernel with internal linkage, such as a template instantiated from a
    header, can be in several translation units under one name. Copies with the
    same instructions are interchangeable; otherwise the copy from one of
    ``units``, the main files of the kernel's recorded compile units, is used.
    """
    if not codes:
        return KernelCode()
    if all(_instructions(c.isa) == _instructions(codes[0].isa) for c in codes[1:]):
        return codes[0]
    units = set(units)
    matches = [c for c in codes if c.unit in units]
    return matches[0] if len(matches) == 1 else None


def disassemble_kernels(binary: str, kernels, llvm_bin: str
                        ) -> Tuple[Optional[str], Dict[str, List[KernelCode]]]:
    """Return the device architecture and each kernel's disassembly and location
    in every code object that has it."""
    found: Dict[str, List[KernelCode]] = {k: [] for k in kernels}
    arch = None
    with tempfile.TemporaryDirectory() as workdir:
        fatbin = os.path.join(workdir, "fatbin.bin")
        dump = subprocess.run(
            [f"{llvm_bin}/llvm-objcopy", f"--dump-section=.hip_fatbin={fatbin}",
             binary, os.devnull],
            capture_output=True, text=True,
        )
        if dump.returncode != 0:
            return None, found
        with open(fatbin, "rb") as f:
            parts = bundles(f.read())
        for n, data in enumerate(parts):
            bundle = os.path.join(workdir, f"bundle{n}.bin")
            with open(bundle, "wb") as f:
                f.write(data)
            co = CodeObject(bundle, llvm_bin, os.path.join(workdir, f"device{n}.co"))
            arch = arch or co.arch
            wanted = co.kernels() & found.keys()
            if not wanted:
                continue
            unit = co.unit()
            locations = co.entry_locations(wanted)
            for k in sorted(wanted):
                found[k].append(KernelCode(co.disassemble(k), *locations.get(k, (None, None, None)),
                                           unit=unit))
    return arch, found
