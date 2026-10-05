"""Function, call, loop and basic-block structure of a recorded LLVM module.

The textual IR from ``llvm-dis`` is parsed directly so the exporter does not
depend on LLVM Python bindings. Loop nesting comes from ``opt``'s
``print<loops>`` analysis, which is more reliable than rediscovering loops from
``!llvm.loop`` metadata.
"""

import re
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

_DEFINE = re.compile(r"^define\b.*?@(\"[^\"]+\"|[\w.$]+)\(")
_LABEL = re.compile(r"^([\w.$-]+|\"[^\"]+\"):")
_CALL = re.compile(r"\b(?:call|invoke)\b[^@]*@(\"[^\"]+\"|[\w.$]+)\(")
_DBG_REF = re.compile(r"!dbg !(\d+)")
_METADATA = re.compile(r"^!(\d+) = (?:distinct )?!(\w+)\((.*)\)\s*$")
_FIELD = re.compile(r"(\w+): (\"(?:[^\"\\]|\\.)*\"|![0-9]+|[^,]+)")


@dataclass
class BasicBlock:
    label: str
    instructions: int = 0
    # Source lines as (file, line) pairs attributed to the block's instructions.
    lines: List[Tuple[str, int]] = field(default_factory=list)
    # Calls as (callee, call site) pairs; the call site is None without debug info.
    calls: List[Tuple[str, Optional[Tuple[str, int]]]] = field(default_factory=list)

    @property
    def callees(self) -> List[str]:
        return [callee for callee, _ in self.calls]


@dataclass
class Loop:
    depth: int
    header: str
    blocks: List[str]
    parent: Optional[int] = None


@dataclass
class Function:
    name: str
    file: Optional[str] = None
    line: Optional[int] = None
    display_name: Optional[str] = None
    blocks: List[BasicBlock] = field(default_factory=list)
    loops: List[Loop] = field(default_factory=list)

    @property
    def calls(self) -> List[Tuple[str, Optional[Tuple[str, int]]]]:
        seen = []
        for b in self.blocks:
            for call in b.calls:
                if call not in seen:
                    seen.append(call)
        return seen


def _unquote(name: str) -> str:
    return name[1:-1] if name.startswith('"') else name


def _parse_metadata(lines: List[str]) -> Dict[int, Tuple[str, Dict[str, str]]]:
    nodes = {}
    for line in lines:
        m = _METADATA.match(line)
        if m:
            fields = {k: v.strip() for k, v in _FIELD.findall(m.group(3))}
            nodes[int(m.group(1))] = (m.group(2), fields)
    return nodes


class _DebugInfo:
    def __init__(self, nodes):
        self.nodes = nodes

    def _ref(self, value: Optional[str]) -> Optional[int]:
        if value and value.startswith("!") and value[1:].isdigit():
            return int(value[1:])
        return None

    def file(self, ref: Optional[int]) -> Optional[str]:
        """Path of a DIFile, or of the file field of any scope node."""
        node = self.nodes.get(ref)
        if not node:
            return None
        kind, fields = node
        if kind == "DIFile":
            name = fields.get("filename", '""').strip('"')
            directory = fields.get("directory", '""').strip('"')
            if name.startswith("/") or not directory:
                return name
            return f"{directory}/{name}"
        return self.file(self._ref(fields.get("file")))

    def location(self, ref: int) -> Optional[Tuple[str, int]]:
        node = self.nodes.get(ref)
        if not node or node[0] != "DILocation":
            return None
        fields = node[1]
        path = self.file(self._ref(fields.get("scope")))
        line = int(fields.get("line", "0"))
        if not path or line == 0:
            return None
        return path, line

    def subprogram(self, ref: Optional[int]) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        node = self.nodes.get(ref)
        if not node or node[0] != "DISubprogram":
            return None, None, None
        fields = node[1]
        line = fields.get("line")
        name = fields.get("name", "").strip('"') or None
        return self.file(self._ref(fields.get("file"))), int(line) if line else None, name


def parse_module(ir_text: str) -> Dict[str, Function]:
    """Parse function definitions, their blocks, calls and source lines."""
    lines = ir_text.splitlines()
    debug = _DebugInfo(_parse_metadata(lines))
    functions: Dict[str, Function] = {}
    current: Optional[Function] = None
    block: Optional[BasicBlock] = None

    for line in lines:
        if current is None:
            m = _DEFINE.match(line)
            if not m:
                continue
            current = Function(_unquote(m.group(1)))
            dbg = re.search(r"!dbg !(\d+)", line)
            if dbg:
                current.file, current.line, current.display_name = debug.subprogram(int(dbg.group(1)))
            # LLVM omits the label of an unnamed entry block.
            block = BasicBlock("entry")
            continue
        if line.startswith("}"):
            if block and (block.instructions or not current.blocks):
                current.blocks.append(block)
            functions[current.name] = current
            current, block = None, None
            continue
        label = _LABEL.match(line)
        if label:
            if block.instructions:
                current.blocks.append(block)
            block = BasicBlock(_unquote(label.group(1)))
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith(";"):
            continue
        block.instructions += 1
        dbg = _DBG_REF.search(stripped)
        loc = debug.location(int(dbg.group(1))) if dbg else None
        if loc and loc not in block.lines:
            block.lines.append(loc)
        call = _CALL.search(stripped)
        if call:
            callee = _unquote(call.group(1))
            if not callee.startswith("llvm."):
                block.calls.append((callee, loc))

    return functions


_LOOP_FUNCTION = re.compile(r"^Loop info for function '(.+)':")
_LOOP = re.compile(r"^(\s*)Loop at depth (\d+) containing: (.*)$")


def parse_loops(opt_output: str) -> Dict[str, List[Loop]]:
    """Parse the output of ``opt -passes='print<loops>'``."""
    loops: Dict[str, List[Loop]] = {}
    current = None
    stack: List[int] = []
    for line in opt_output.splitlines():
        m = _LOOP_FUNCTION.match(line)
        if m:
            current = m.group(1)
            loops.setdefault(current, [])
            stack = []
            continue
        m = _LOOP.match(line)
        if not m or current is None:
            continue
        depth = int(m.group(2))
        blocks, header = [], None
        for entry in m.group(3).split(","):
            entry = entry.strip()
            name = _unquote(entry.split("<", 1)[0].lstrip("%"))
            blocks.append(name)
            if "<header>" in entry:
                header = name
        del stack[depth - 1 :]
        parent = stack[-1] if stack else None
        loops[current].append(Loop(depth, header or blocks[0], blocks, parent))
        stack.append(len(loops[current]) - 1)
    return loops


def analyze_bitcode(bitcode: str, llvm_bin: str) -> Tuple[str, Dict[str, Function]]:
    """Return the textual IR of a bitcode file and its parsed functions."""
    ir_text = subprocess.run(
        [f"{llvm_bin}/llvm-dis", bitcode, "-o", "-"],
        check=True, capture_output=True, text=True,
    ).stdout
    functions = parse_module(ir_text)
    opt = subprocess.run(
        [f"{llvm_bin}/opt", "-disable-output", "-passes=print<loops>", bitcode],
        check=True, capture_output=True, text=True,
    )
    for name, loops in parse_loops(opt.stderr).items():
        if name in functions:
            functions[name].loops = loops
    return ir_text, functions
