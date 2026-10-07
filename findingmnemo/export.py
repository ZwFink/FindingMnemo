"""Build the hierarchical program database from FindingMnemo run directories.

A run directory holds ``run.json`` (what was executed), ``record-db/`` (the
Mneme recording) and ``stacks/`` (launch stacks from the shim). The database is
a directory tree that mirrors the program hierarchy, so it can be browsed with
``ls``, ``tree`` and ``jq``::

    <db>/index.json, graph.json
    <db>/<program>/program.json, launches.json
    <db>/<program>/files/<source file>/<function>/function.json, ir.ll, ...

HIP runtime helpers (``__ockl_*``, ``__hip_get_*``, ...) are left out.
"""

import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

from mneme.recorded_execution import KernelSource, RecordedExecution

from . import ir, isa, stacks

FORMAT = "findingmnemo-db/1"


@dataclass
class _Kernel:
    code: isa.KernelCode
    record: Optional[dict] = None
    record_path: Optional[str] = None
    module_ir: Optional[str] = None
    # Read from Mneme's copy of the file.
    source: Optional[KernelSource] = None


@dataclass
class _Function:
    # host, kernel or device.
    kind: str
    # Linkage name for device code; host functions only have the name the
    # symbolizer reports.
    name: str
    display_name: str
    # Name from the debug info, which clang writes the same way for host and
    # device code, e.g. ``forall<(lambda at app.cpp:28:13)>``.
    debug_name: Optional[str]
    file: Optional[str]
    line: Optional[int]
    end_line: Optional[int] = None
    ir_fn: Optional[ir.Function] = None
    kernel: Optional[_Kernel] = None
    # Directory relative to the program directory, assigned before writing.
    path: str = ""


@dataclass
class _Edge:
    caller: _Function
    callee: _Function
    # 'stack' for host calls observed on the way to a launch, 'launch' for a
    # host function launching a kernel, and 'ir' for static device calls.
    origin: str
    file: Optional[str]
    line: Optional[int]
    # Kernel launches that went through a dynamic edge; None for static edges.
    launches: Optional[int]


_RUNTIME_PREFIXES = ("__ockl_", "__ocml_", "__hip_", "_ZN24__hip_builtin", "_ZN25__hip_builtin",
                     "_ZL21__hip_", "_ZL22__hip_")


def _is_runtime_function(name: str, file: Optional[str]) -> bool:
    if name.startswith(_RUNTIME_PREFIXES):
        return True
    return bool(file) and "/include/hip/" in file


def _demangle(symbols: List[str], llvm_bin: str) -> Dict[str, str]:
    out = subprocess.run([f"{llvm_bin}/llvm-cxxfilt"], input="\n".join(symbols),
                         capture_output=True, text=True, check=True).stdout.splitlines()
    return dict(zip(symbols, out))


def _load_records(record_dir: str) -> List[Tuple[str, dict]]:
    records = []
    for path in sorted(glob.glob(os.path.join(record_dir, "*.json"))):
        with open(path) as f:
            record = json.load(f)
        if "KernelName" in record:
            records.append((path, record))
    return records


class _Program:
    """One run directory, joined into functions and call edges."""

    def __init__(self, run_dir: str, llvm_bin: str):
        self.run_dir = run_dir
        with open(os.path.join(run_dir, "run.json")) as f:
            self.run = json.load(f)
        self.functions: Dict[Tuple[str, str], _Function] = {}
        self.edges: Dict[tuple, _Edge] = {}
        # Source file -> the copy that `mneme record --copy-source` made of it.
        self.source_copies: Dict[str, str] = {}
        self.dir = ""

        record_dir = os.path.join(run_dir, "record-db")
        records = _load_records(record_dir)
        self.launch_paths = stacks.load_launch_paths(os.path.join(run_dir, "stacks"), llvm_bin)
        kernel_names = sorted({r["KernelName"] for _, r in records}
                              | {p.kernel for p in self.launch_paths})
        self.gpu_arch, self.code = isa.disassemble_kernels(self.run["executable"], kernel_names,
                                                           llvm_bin)
        self.demangled = _demangle(kernel_names, llvm_bin)

        for path, record in records:
            self._add_recorded_kernel(record, path, record_dir, llvm_bin)
        for launch in self.launch_paths:
            self._add_launch(launch)

        self.runtime = {fn.name for fn in self.functions.values()
                        if _is_runtime_function(fn.name, fn.file)}
        self.functions = {key: fn for key, fn in self.functions.items() if key[1] not in self.runtime}
        self.edges = {key: e for key, e in self.edges.items()
                      if e.caller.name not in self.runtime and e.callee.name not in self.runtime}

    @property
    def name(self) -> str:
        return self.run.get("name") or os.path.basename(self.run["executable"])

    def function(self, kind: str, name: str, display_name=None, debug_name=None,
                 file=None, line=None) -> _Function:
        key = (kind, name)
        if key not in self.functions:
            self.functions[key] = _Function(kind, name, display_name or name, debug_name,
                                            os.path.normpath(file) if file else None, line)
        return self.functions[key]

    def add_edge(self, caller: _Function, callee: _Function, origin: str,
                 file=None, line=None, launches=None):
        key = (caller.kind, caller.name, callee.kind, callee.name, origin, file, line)
        edge = self.edges.get(key)
        if edge is None:
            self.edges[key] = _Edge(caller, callee, origin, file, line, launches)
        elif launches is not None:
            edge.launches += launches

    def kernel_code(self, kernel: str, units: Iterable[str] = ()) -> isa.KernelCode:
        """The kernel's code, from the code object of one of ``units`` if its
        translation units compiled it differently."""
        codes = self.code.get(kernel, [])
        code = isa.choose(codes, units)
        if code is None:
            print(f"findingmnemo export: no ISA for {self.demangled.get(kernel, kernel)}: "
                  f"{len(codes)} translation units compiled it differently, and none is the "
                  f"one Mneme recorded", file=sys.stderr)
            return isa.KernelCode(None, codes[0].name, codes[0].file, codes[0].line)
        return code

    def _add_recorded_kernel(self, record: dict, record_path: str, record_dir: str,
                             llvm_bin: str):
        ir_texts, parsed, units = [], {}, []
        for module in record["Modules"]:
            text, functions = ir.analyze_bitcode(os.path.join(record_dir, module), llvm_bin)
            ir_texts.append(text)
            parsed.update(functions)
            units += ir.compile_unit_files(text)

        name = record["KernelName"]
        self.demangled.update(_demangle([f for f in parsed if f not in self.demangled], llvm_bin))
        for fn in parsed.values():
            kind = "kernel" if fn.name == name else "device"
            node = self.function(kind, fn.name, self.demangled[fn.name], fn.display_name,
                                 fn.file, fn.line)
            # Device functions shared by several kernels appear in each module.
            if node.ir_fn is None:
                node.ir_fn = fn
                if kind == "device":
                    node.end_line = _last_line(fn)
        for fn in parsed.values():
            caller = self.functions[("kernel" if fn.name == name else "device", fn.name)]
            for callee_name, site in fn.calls:
                callee = (self.functions.get(("device", callee_name))
                          or self.functions.get(("kernel", callee_name)))
                if callee:
                    self.add_edge(caller, callee, "ir", *(site or (None, None)))

        code = self.kernel_code(name, units)
        kernel = self.function("kernel", name, record["DemangledName"], code.name,
                               record.get("SourceFile") or code.file, record.get("SourceLine"))
        if record.get("SourceLine"):
            kernel.line, kernel.end_line = record["SourceLine"], record.get("SourceEndLine")
        source = RecordedExecution.from_json(record_path).kernel_source()
        if source:
            self.source_copies[kernel.file] = source.file
        kernel.kernel = _Kernel(code, record, record_path, "\n".join(ir_texts), source)

    def _add_launch(self, launch: stacks.LaunchPath):
        known = self.functions.get(("kernel", launch.kernel))
        code = known.kernel.code if known and known.kernel else self.kernel_code(launch.kernel)
        kernel = self.function("kernel", launch.kernel, self.demangled[launch.kernel], code.name,
                               code.file)
        if kernel.kernel is None:
            # Launched but not recorded by Mneme, e.g. from a library not built for Mneme.
            kernel.kernel = _Kernel(code)
        frames = [self.function("host", f.function, f.function, f.function, f.file, f.start_line)
                  for f in launch.frames]
        for i in range(len(frames) - 1):
            site = launch.frames[i]
            self.add_edge(frames[i], frames[i + 1], "stack", site.file, site.line, launch.count)
        if frames:
            site = launch.frames[-1]
            self.add_edge(frames[-1], kernel, "launch", site.file, site.line, launch.count)


_OPERATOR = re.compile(r"operator(\(\)|<<=?|>>=?|<=>|<=?|>=?|->\*?)")
_BRACKETS = {"<": 1, "(": 1, "{": 1, ">": -1, ")": -1, "}": -1}
# A device lambda's call operator, as demangled: main::'lambda'(int)::operator().
_LAMBDA_CALL = re.compile(r"'lambda\d*'\([^()]*\)::operator\(\)$")
# A lambda in a debug-info name: forall<(lambda at app.cpp:28:13)>.
_DEBUG_LAMBDA = re.compile(r"\(lambda at ([^():]+):(\d+):\d+\)")
_DEMANGLED_LAMBDA = re.compile(r"'lambda(\d*)'\([^()]*\)")
_LONG_NAME = 80


def _depths(name: str) -> List[int]:
    """Bracket depth before each character, ignoring brackets in operator names."""
    masked = _OPERATOR.sub(lambda m: "x" * len(m.group(0)), name)
    depths, depth = [], 0
    for c in masked:
        depths.append(depth)
        depth += _BRACKETS.get(c, 0)
    return depths


def _short_name(name: str) -> str:
    """Drop the parameter list and return type from a demangled name."""
    name = re.sub(r"(\s+(const|volatile|&|&&))+$", "", name)
    depths = _depths(name)
    if name.endswith(")") and not name.endswith("operator()"):
        start = max((i for i, c in enumerate(name) if c == "(" and depths[i] == 0), default=0)
        name = name[:start] or name
        depths = depths[:len(name)]
    # The space before a qualifier inside a nested name, as in
    # main::'lambda'(int)::operator()(int) const::'lambda'(), is not the end of
    # a return type.
    start = max((i + 1 for i, c in enumerate(name) if c == " " and depths[i] == 0
                 and not name.startswith(("const", "volatile"), i + 1)), default=0)
    return name[start:] or name


def _abbreviate_templates(name: str) -> str:
    """Replace template arguments with the lambdas among them, or "..."."""
    depths = _depths(name)
    out, start = [], None
    for i, c in enumerate(name):
        if c == "<" and depths[i] == 0:
            start = i
        elif c == ">" and depths[i] == 1 and start is not None:
            lambdas = re.findall(r"lambda@[\w.+-]+", name[start:i])
            out.append("<" + (",".join(lambdas) or "...") + ">")
            start = None
        elif start is None:
            out.append(c)
    return "".join(out)


def _lambda_lines(functions) -> Dict[str, int]:
    """Map each lambda's demangled closure type to the line of its body."""
    lines = {}
    for fn in functions:
        short = _short_name(fn.display_name)
        if fn.line and _LAMBDA_CALL.search(short):
            lines[short[:-len("::operator()")]] = fn.line
    return lines


def _dir_name(fn: _Function, lambda_lines: Dict[str, int]) -> str:
    """A readable directory name; lambdas become lambda@<line>."""
    if fn.line and _LAMBDA_CALL.search(_short_name(fn.display_name)):
        return f"lambda@{fn.line}"
    own_file = os.path.basename(fn.file or "")

    def lambda_at(m):
        file = os.path.basename(m.group(1))
        return f"lambda@{m.group(2)}" if file == own_file else f"lambda@{file}-{m.group(2)}"

    name = _short_name(fn.debug_name or fn.display_name)
    # Nested lambdas' closure types contain their parents', so replace them first.
    for closure in sorted(lambda_lines, key=len, reverse=True):
        name = name.replace(closure, f"lambda@{lambda_lines[closure]}")
    name = _DEMANGLED_LAMBDA.sub(r"lambda\1", _DEBUG_LAMBDA.sub(lambda_at, name))
    if len(name) > _LONG_NAME:
        name = _abbreviate_templates(name)
    return _safe_name(name)


def _safe_name(name: str) -> str:
    """Make a name usable as a directory name on any file system."""
    name = name.replace("::", ".").replace("<", "[").replace(">", "]").replace(", ", ",")
    name = re.sub(r"[^A-Za-z0-9._+@,()\[\]-]+", "_", name).rstrip("_")[:120]
    return name if name and not name.startswith(".") else "_" + name


def _unique(path: str, used: set) -> str:
    candidate, n = path, 1
    while candidate in used:
        n += 1
        candidate = f"{path}~{n}"
    used.add(candidate)
    return candidate


def _assign_paths(prog: _Program) -> Dict[Optional[str], str]:
    file_dirs: Dict[Optional[str], str] = {}
    used: set = set()
    order = sorted(prog.functions.values(), key=lambda f: (f.file or "", f.line or 0, f.name))
    lambda_lines = _lambda_lines(order)
    for fn in order:
        if fn.file not in file_dirs:
            base = os.path.basename(fn.file) if fn.file else "_unknown"
            file_dirs[fn.file] = _unique(f"files/{_safe_name(base)}", used)
        path = f"{file_dirs[fn.file]}/{_dir_name(fn, lambda_lines)}"
        if path in used:
            # Overloads share a short name; the symbol tells them apart.
            path = f"{file_dirs[fn.file]}/{_safe_name(fn.name)}"
        fn.path = _unique(path, used)
    return file_dirs


def _last_line(fn: ir.Function) -> Optional[int]:
    """The last line of the function that generated code, as Mneme finds it
    for kernels. The recorded IR is not inlined, so every location in the
    function's file belongs to the function itself."""
    lines = [ln for b in fn.blocks for f, ln in b.lines if f == fn.file]
    return max(lines + [fn.line]) if fn.line else None


def _lines(block: ir.BasicBlock, file: Optional[str]) -> Optional[List[int]]:
    own = [ln for f, ln in block.lines if f == file] or [ln for _, ln in block.lines]
    return [min(own), max(own)] if own else None


def _body(prog: _Program, fn: ir.Function) -> list:
    """Nest the function's basic blocks in its loops, in IR order."""
    loops = [{"loop": loop.header, "depth": loop.depth, "body": []} for loop in fn.loops]
    placed, top = set(), []
    for block in fn.blocks:
        # print<loops> lists outer loops before inner ones.
        containing = [i for i, loop in enumerate(fn.loops) if block.label in loop.blocks]
        for i in containing:
            if i not in placed:
                parent = fn.loops[i].parent
                (loops[parent]["body"] if parent is not None else top).append(loops[i])
                placed.add(i)
        entry = {"block": block.label, "instructions": block.instructions}
        lines = _lines(block, fn.file)
        if lines:
            entry["lines"] = lines
        calls = [_display(prog, c) for c in dict.fromkeys(block.callees)
                 if c not in prog.runtime and not _is_runtime_function(c, None)]
        if calls:
            entry["calls"] = calls
        (loops[containing[-1]]["body"] if containing else top).append(entry)
    return top


def _display(prog: _Program, name: str) -> str:
    fn = prog.functions.get(("device", name)) or prog.functions.get(("kernel", name))
    return fn.display_name if fn else name


def _site(edge: _Edge, other: _Function, own_file: Optional[str]) -> dict:
    site = {"function": other.display_name, "at": other.path}
    if edge.file and edge.file != own_file:
        site["file"] = edge.file
    if edge.line:
        site["line"] = edge.line
    if edge.launches is not None:
        site["launch_count"] = edge.launches
    return site


def _dumps(value, indent: int = 0) -> str:
    """Indented JSON that keeps lists of scalars, such as grid sizes, on one line."""
    pad = "  " * indent
    if isinstance(value, dict) and value:
        items = [f"{pad}  {json.dumps(k)}: {_dumps(v, indent + 1)}" for k, v in value.items()]
        return "{\n" + ",\n".join(items) + f"\n{pad}}}"
    if isinstance(value, list) and any(isinstance(v, (dict, list)) for v in value):
        items = [f"{pad}  {_dumps(v, indent + 1)}" for v in value]
        return "[\n" + ",\n".join(items) + f"\n{pad}]"
    return json.dumps(value)


def _write_json(path: str, data) -> None:
    with open(path, "w") as f:
        f.write(_dumps(data) + "\n")


def _write_text(path: str, text: Optional[str]) -> None:
    if text:
        with open(path, "w") as f:
            f.write(text)


def _write_function(prog: _Program, fn: _Function, out: str) -> None:
    fn_dir = os.path.join(out, fn.path)
    os.makedirs(fn_dir, exist_ok=True)
    k = fn.kernel
    source = k.source.text if k and k.source else None
    if fn.kind == "device" and fn.end_line and fn.file in prog.source_copies:
        with open(prog.source_copies[fn.file]) as f:
            lines = f.readlines()
        # A function with one return statement ends there in the debug info.
        if fn.end_line < len(lines) and lines[fn.end_line].strip() == "}":
            fn.end_line += 1
        source = "".join(lines[fn.line - 1:fn.end_line])
    data = {"kind": fn.kind, "name": fn.display_name}
    if fn.name != fn.display_name:
        data["symbol"] = fn.name
    for key, value in (("file", fn.file), ("line", fn.line), ("end_line", fn.end_line)):
        if value is not None:
            data[key] = value

    if k:
        if k.code.instructions:
            data["isa_instructions"] = k.code.instructions
        if fn.line is None and k.code.line:
            data["entry_line"] = k.code.line
        if k.record:
            data["static_hash"] = str(k.record["StaticHash"])
            data["mneme_record"] = k.record_path

    out_edges = [e for e in prog.edges.values() if e.caller is fn]
    in_edges = [e for e in prog.edges.values() if e.callee is fn]
    for key, edges, other in (("calls", [e for e in out_edges if e.origin != "launch"], "callee"),
                              ("launches", [e for e in out_edges if e.origin == "launch"], "callee"),
                              ("called_by", [e for e in in_edges if e.origin != "launch"], "caller"),
                              ("launched_by", [e for e in in_edges if e.origin == "launch"], "caller")):
        if edges:
            data[key] = [_site(e, getattr(e, other), fn.file) for e in edges]
    if fn.ir_fn:
        data["body"] = _body(prog, fn.ir_fn)
    _write_json(os.path.join(fn_dir, "function.json"), data)

    if fn.ir_fn:
        _write_text(os.path.join(fn_dir, "ir.ll"), fn.ir_fn.text)
    _write_text(os.path.join(fn_dir, "source" + (os.path.splitext(fn.file or "")[1] or ".txt")), source)
    if k:
        _write_text(os.path.join(fn_dir, "module.ll"), k.module_ir)
        _write_text(os.path.join(fn_dir, "isa.s"), k.code.isa)
        if k.record and k.record.get("instances"):
            record_dir = os.path.dirname(k.record_path)
            _write_json(os.path.join(fn_dir, "instances.json"), [{
                "dynamic_hash": dyn_hash,
                "grid": [inst["GridDims"][d] for d in "xyz"],
                "block": [inst["BlockDims"][d] for d in "xyz"],
                "shared_mem": inst["SharedMem"],
                "occurrences": inst["Occurrences"],
                "prologue": os.path.join(record_dir, inst["Prologue"]),
                "epilogue": os.path.join(record_dir, inst["Epilogue"]),
            } for dyn_hash, inst in k.record["instances"].items()])


def _write_program(prog: _Program, out: str) -> None:
    file_dirs = _assign_paths(prog)
    os.makedirs(out)
    kernels = sorted((f for f in prog.functions.values() if f.kind == "kernel"), key=lambda f: f.path)
    _write_json(os.path.join(out, "program.json"), {
        "name": prog.name,
        "executable": prog.run["executable"],
        "arguments": prog.run["arguments"],
        "hostname": prog.run.get("hostname"),
        "recorded_at": prog.run.get("recorded_at"),
        "gpu_arch": prog.gpu_arch,
        "run_dir": prog.run_dir,
        "kernels": [k.path for k in kernels],
    })
    _write_json(os.path.join(out, "launches.json"), [{
        "kernel": prog.functions[("kernel", p.kernel)].display_name,
        "at": prog.functions[("kernel", p.kernel)].path,
        "grid": list(p.grid),
        "block": list(p.block),
        "shared_mem": p.shared_mem,
        "count": p.count,
        "call_path": [{"function": f.function, "at": prog.functions[("host", f.function)].path,
                       "file": f.file, "line": f.line} for f in p.frames],
    } for p in prog.launch_paths])
    for path, file_dir in file_dirs.items():
        os.makedirs(os.path.join(out, file_dir))
        _write_json(os.path.join(out, file_dir, "file.json"), {"path": path})
        if path in prog.source_copies:
            shutil.copyfile(prog.source_copies[path],
                            os.path.join(out, file_dir, "source" + os.path.splitext(path)[1]))
    for fn in prog.functions.values():
        _write_function(prog, fn, out)


def _graph(prog: _Program, nodes: list, edges: list) -> None:
    """Add the program's hierarchy and call edges to a nodes/edges graph.

    Node ids are paths in the database directory, with ``#`` for loops, blocks
    and instances inside a function directory.
    """
    def node(node_id, kind, label, **attrs):
        nodes.append({"id": node_id, "kind": kind, "label": label, **attrs})

    def edge(source, target, kind, **attrs):
        edges.append({"source": source, "target": target, "kind": kind, **attrs})

    def fn_id(fn):
        return f"{prog.dir}/{fn.path}"

    node(prog.dir, "program", prog.name, executable=prog.run["executable"],
         arguments=prog.run["arguments"], gpu_arch=prog.gpu_arch, hostname=prog.run.get("hostname"))
    functions = list(prog.functions.values())
    for file_dir, path in sorted({(os.path.dirname(f.path), f.file or "") for f in functions}):
        node(f"{prog.dir}/{file_dir}", "source_file", os.path.basename(file_dir), path=path or None)
        edge(prog.dir, f"{prog.dir}/{file_dir}", "contains")

    for fn in functions:
        attrs = {"name": fn.name, "file": fn.file, "line": fn.line}
        if fn.end_line:
            attrs["end_line"] = fn.end_line
        if fn.kernel and fn.kernel.code.instructions:
            attrs["isa_instructions"] = fn.kernel.code.instructions
        node(fn_id(fn), f"{fn.kind}_function", fn.display_name, **attrs)
        edge(f"{prog.dir}/{os.path.dirname(fn.path)}", fn_id(fn), "contains")

        if fn.kernel and fn.kernel.record:
            for dyn_hash, inst in fn.kernel.record.get("instances", {}).items():
                inst_id = f"{fn_id(fn)}#instance:{dyn_hash}"
                node(inst_id, "kernel_instance", dyn_hash,
                     grid=[inst["GridDims"][d] for d in "xyz"],
                     block=[inst["BlockDims"][d] for d in "xyz"],
                     shared_mem=inst["SharedMem"], occurrences=inst["Occurrences"])
                edge(fn_id(fn), inst_id, "has_instance")

        if not fn.ir_fn:
            continue
        loop_ids = [f"{fn_id(fn)}#loop:{loop.header}" for loop in fn.ir_fn.loops]
        for loop, loop_id in zip(fn.ir_fn.loops, loop_ids):
            node(loop_id, "loop", loop.header, depth=loop.depth)
            edge(loop_ids[loop.parent] if loop.parent is not None else fn_id(fn), loop_id, "contains")
        for block in fn.ir_fn.blocks:
            containing = [i for i, loop in enumerate(fn.ir_fn.loops) if block.label in loop.blocks]
            block_id = f"{fn_id(fn)}#block:{block.label}"
            lines = _lines(block, fn.file) or [None, None]
            node(block_id, "basic_block", block.label, instructions=block.instructions,
                 first_line=lines[0], last_line=lines[1])
            edge(loop_ids[containing[-1]] if containing else fn_id(fn), block_id, "contains")

    for e in prog.edges.values():
        edge(fn_id(e.caller), fn_id(e.callee), "launches" if e.origin == "launch" else "calls",
             origin=e.origin, call_file=e.file, call_line=e.line, launches=e.launches)


def _prepare_output(out_dir: str) -> None:
    """Replace a previous database, but never a directory that is not one."""
    if not os.path.exists(out_dir):
        return
    index = os.path.join(out_dir, "index.json")
    try:
        with open(index) as f:
            ours = json.load(f).get("format") == FORMAT
    except (OSError, ValueError):
        ours = False
    if ours:
        shutil.rmtree(out_dir)
    elif os.listdir(out_dir):
        raise SystemExit(f"findingmnemo export: {out_dir} exists and is not a FindingMnemo database")


def build(run_dirs: List[str], out_dir: str, llvm_bin: str) -> str:
    """Write the database for ``run_dirs`` to ``out_dir``, one program per run."""
    for run_dir in run_dirs:
        if not os.path.isfile(os.path.join(run_dir, "run.json")):
            raise SystemExit(f"findingmnemo export: {run_dir} is not a run directory (no run.json)")
    _prepare_output(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    used: set = set()
    nodes, edges, index = [], [], []
    for run_dir in run_dirs:
        prog = _Program(os.path.abspath(run_dir), llvm_bin)
        prog.dir = _unique(_safe_name(os.path.basename(os.path.normpath(prog.run_dir))), used)
        _write_program(prog, os.path.join(out_dir, prog.dir))
        _graph(prog, nodes, edges)
        index.append({"dir": prog.dir, "name": prog.name, "arguments": prog.run["arguments"],
                      "gpu_arch": prog.gpu_arch})
    with open(os.path.join(out_dir, "graph.json"), "w") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, indent=1)
    _write_json(os.path.join(out_dir, "index.json"), {
        "format": FORMAT,
        "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "programs": index,
    })
    return out_dir
