"""Build the hierarchical program database from a FindingMnemo run directory.

A run directory holds ``run.json`` (what was executed), ``record-db/`` (the
Mneme recording) and ``stacks/`` (launch stacks from the shim).
"""

import glob
import hashlib
import json
import os
import socket
import sqlite3
from typing import Dict, List, Optional, Tuple

from . import ir, isa, stacks

SCHEMA = """
CREATE TABLE programs (
  id INTEGER PRIMARY KEY,
  name TEXT, executable TEXT, arguments TEXT, hostname TEXT, gpu_arch TEXT,
  run_dir TEXT, recorded_at TEXT
);
CREATE TABLE source_files (
  id INTEGER PRIMARY KEY,
  program_id INTEGER REFERENCES programs(id),
  path TEXT,
  UNIQUE(program_id, path)
);
-- kind is 'host', 'kernel' or 'device'. Host functions come from the launch
-- stacks; kernels and device functions come from the recorded LLVM IR.
CREATE TABLE functions (
  id INTEGER PRIMARY KEY,
  program_id INTEGER REFERENCES programs(id),
  kind TEXT, name TEXT, display_name TEXT,
  file_id INTEGER REFERENCES source_files(id), line INTEGER,
  -- 1 for HIP/ROCm runtime helpers such as __ockl_get_local_id.
  is_runtime INTEGER,
  UNIQUE(program_id, kind, name)
);
-- origin is 'stack' for host calls observed on the way to a launch, 'launch'
-- for a host function launching a kernel, and 'ir' for static device calls.
-- launches counts the kernel launches that went through a stack or launch
-- edge; it is NULL for static edges.
CREATE TABLE call_edges (
  id INTEGER PRIMARY KEY,
  program_id INTEGER REFERENCES programs(id),
  caller_id INTEGER REFERENCES functions(id),
  callee_id INTEGER REFERENCES functions(id),
  origin TEXT, call_file TEXT, call_line INTEGER, launches INTEGER,
  UNIQUE(caller_id, callee_id, origin, call_file, call_line)
);
CREATE TABLE kernels (
  id INTEGER PRIMARY KEY,
  function_id INTEGER REFERENCES functions(id),
  mangled_name TEXT, demangled_name TEXT, static_hash TEXT,
  source_file TEXT, source_line INTEGER, source_end_line INTEGER,
  source_md5 TEXT, source_text TEXT,
  ir_files TEXT, ir_text TEXT,
  isa_text TEXT, isa_instructions INTEGER,
  mneme_record TEXT
);
-- One row per launch configuration Mneme recorded (capped per kernel by
-- mneme record's --per-kernel-max-recordings).
CREATE TABLE kernel_instances (
  id INTEGER PRIMARY KEY,
  kernel_id INTEGER REFERENCES kernels(id),
  dynamic_hash TEXT,
  grid_x INTEGER, grid_y INTEGER, grid_z INTEGER,
  block_x INTEGER, block_y INTEGER, block_z INTEGER,
  shared_mem INTEGER, occurrences INTEGER,
  prologue TEXT, epilogue TEXT
);
-- Every launch, aggregated by host call path and launch configuration.
CREATE TABLE launch_paths (
  id INTEGER PRIMARY KEY,
  kernel_id INTEGER REFERENCES kernels(id),
  frames TEXT,
  grid_x INTEGER, grid_y INTEGER, grid_z INTEGER,
  block_x INTEGER, block_y INTEGER, block_z INTEGER,
  shared_mem INTEGER, count INTEGER
);
CREATE TABLE loops (
  id INTEGER PRIMARY KEY,
  function_id INTEGER REFERENCES functions(id),
  parent_id INTEGER REFERENCES loops(id),
  depth INTEGER, header TEXT
);
CREATE TABLE basic_blocks (
  id INTEGER PRIMARY KEY,
  function_id INTEGER REFERENCES functions(id),
  loop_id INTEGER REFERENCES loops(id),
  position INTEGER, label TEXT, instructions INTEGER,
  first_line INTEGER, last_line INTEGER,
  source_lines TEXT, callees TEXT
);
"""


class _Builder:
    def __init__(self, conn: sqlite3.Connection, program_id: int):
        self.conn = conn
        self.program_id = program_id
        self.files: Dict[str, int] = {}
        self.functions: Dict[Tuple[str, str], int] = {}

    def file_id(self, path: Optional[str]) -> Optional[int]:
        if not path:
            return None
        path = os.path.normpath(path)
        if path not in self.files:
            cur = self.conn.execute(
                "INSERT INTO source_files(program_id, path) VALUES (?, ?)",
                (self.program_id, path))
            self.files[path] = cur.lastrowid
        return self.files[path]

    def function_id(self, kind: str, name: str, display_name=None, file=None, line=None) -> int:
        key = (kind, name)
        if key not in self.functions:
            cur = self.conn.execute(
                "INSERT INTO functions(program_id, kind, name, display_name, file_id, line, is_runtime)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (self.program_id, kind, name, display_name or name, self.file_id(file), line,
                 int(_is_runtime_function(name, file))))
            self.functions[key] = cur.lastrowid
        return self.functions[key]

    def add_edge(self, caller: int, callee: int, origin: str, file=None, line=None, launches=None):
        self.conn.execute(
            "INSERT INTO call_edges(program_id, caller_id, callee_id, origin, call_file, call_line, launches)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)"
            " ON CONFLICT(caller_id, callee_id, origin, call_file, call_line)"
            " DO UPDATE SET launches = launches + excluded.launches",
            (self.program_id, caller, callee, origin, file, line, launches))


_RUNTIME_PREFIXES = ("__ockl_", "__ocml_", "__hip_", "_ZN24__hip_builtin", "_ZN25__hip_builtin",
                     "_ZL21__hip_", "_ZL22__hip_")


def _is_runtime_function(name: str, file: Optional[str]) -> bool:
    if name.startswith(_RUNTIME_PREFIXES):
        return True
    return bool(file) and "/include/hip/" in file


def _kernel_source(record: dict, record_dir: str) -> Optional[str]:
    """Slice the kernel's lines from the recorded copy, verified by checksum."""
    if "SourceLine" not in record:
        return None
    candidates = []
    if record.get("SourceCopy"):
        candidates.append(os.path.join(record_dir, record["SourceCopy"]))
    candidates.append(record["SourceFile"])
    for path in candidates:
        try:
            with open(path, "rb") as f:
                data = f.read()
        except OSError:
            continue
        if record.get("SourceMD5") and hashlib.md5(data).hexdigest() != record["SourceMD5"]:
            continue
        lines = data.decode(errors="replace").splitlines()
        return "\n".join(lines[record["SourceLine"] - 1:record["SourceEndLine"]])
    return None


def _load_records(record_dir: str) -> List[dict]:
    records = []
    for path in sorted(glob.glob(os.path.join(record_dir, "*.json"))):
        with open(path) as f:
            record = json.load(f)
        if "KernelName" in record:
            records.append(record)
    return records


def _add_device_code(b: _Builder, record: dict, record_dir: str, llvm_bin: str) -> Tuple[int, str]:
    """Insert the kernel's device functions, loops and blocks from its IR."""
    ir_texts, functions = [], {}
    for module in record["Modules"]:
        text, parsed = ir.analyze_bitcode(os.path.join(record_dir, module), llvm_bin)
        ir_texts.append(text)
        functions.update(parsed)

    kernel_name = record["KernelName"]
    ids = {}
    for fn in functions.values():
        kind = "kernel" if fn.name == kernel_name else "device"
        display = record["DemangledName"] if kind == "kernel" else fn.display_name
        ids[fn.name] = b.function_id(kind, fn.name, display, fn.file, fn.line)

    for fn in functions.values():
        fid = ids[fn.name]
        if b.conn.execute("SELECT 1 FROM basic_blocks WHERE function_id = ?", (fid,)).fetchone():
            continue  # Already inserted from another kernel's module.
        loop_ids = []
        for loop in fn.loops:
            parent = loop_ids[loop.parent] if loop.parent is not None else None
            cur = b.conn.execute(
                "INSERT INTO loops(function_id, parent_id, depth, header) VALUES (?, ?, ?, ?)",
                (fid, parent, loop.depth, loop.header))
            loop_ids.append(cur.lastrowid)
        for pos, block in enumerate(fn.blocks):
            # print<loops> lists outer loops before inner ones, so the last
            # loop containing the block is the innermost.
            innermost = None
            for i, loop in enumerate(fn.loops):
                if block.label in loop.blocks:
                    innermost = loop_ids[i]
            lines = [ln for _, ln in block.lines]
            b.conn.execute(
                "INSERT INTO basic_blocks(function_id, loop_id, position, label, instructions,"
                " first_line, last_line, source_lines, callees) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (fid, innermost, pos, block.label, block.instructions,
                 min(lines) if lines else None, max(lines) if lines else None,
                 json.dumps(block.lines), json.dumps(block.callees)))
        for callee in fn.callees:
            if callee in ids:
                b.add_edge(fid, ids[callee], "ir")
    return ids[kernel_name], "\n".join(ir_texts)


def build(run_dirs: List[str], db_path: str, llvm_bin: str) -> str:
    """Create ``db_path`` with one program per run directory."""
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    for run_dir in run_dirs:
        _add_run(conn, os.path.abspath(run_dir), llvm_bin)
    conn.commit()
    conn.close()
    return db_path


def _add_run(conn: sqlite3.Connection, run_dir: str, llvm_bin: str):
    with open(os.path.join(run_dir, "run.json")) as f:
        run = json.load(f)
    record_dir = os.path.join(run_dir, "record-db")
    records = _load_records(record_dir) if os.path.isdir(record_dir) else []
    launch_paths = stacks.load_launch_paths(os.path.join(run_dir, "stacks"), llvm_bin)

    kernel_names = sorted({r["KernelName"] for r in records} | {p.kernel for p in launch_paths})
    gpu_arch, isa_texts = isa.disassemble_kernels(run["executable"], kernel_names, llvm_bin)

    cur = conn.execute(
        "INSERT INTO programs(name, executable, arguments, hostname, gpu_arch, run_dir, recorded_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (run.get("name") or os.path.basename(run["executable"]), run["executable"],
         json.dumps(run["arguments"]), run.get("hostname", socket.gethostname()),
         gpu_arch, run_dir, run.get("recorded_at")))
    b = _Builder(conn, cur.lastrowid)

    kernel_ids: Dict[str, int] = {}
    for record in records:
        function_id, ir_text = _add_device_code(b, record, record_dir, llvm_bin)
        isa_text = isa_texts.get(record["KernelName"])
        cur = conn.execute(
            "INSERT INTO kernels(function_id, mangled_name, demangled_name, static_hash,"
            " source_file, source_line, source_end_line, source_md5, source_text,"
            " ir_files, ir_text, isa_text, isa_instructions, mneme_record)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (function_id, record["KernelName"], record["DemangledName"], str(record["StaticHash"]),
             record.get("SourceFile"), record.get("SourceLine"), record.get("SourceEndLine"),
             record.get("SourceMD5"), _kernel_source(record, record_dir),
             json.dumps([os.path.join(record_dir, m) for m in record["Modules"]]), ir_text,
             isa_text, isa.instruction_count(isa_text) if isa_text else None,
             json.dumps(record)))
        kernel_ids[record["KernelName"]] = cur.lastrowid
        for dyn_hash, inst in record.get("instances", {}).items():
            g, bl = inst["GridDims"], inst["BlockDims"]
            conn.execute(
                "INSERT INTO kernel_instances(kernel_id, dynamic_hash, grid_x, grid_y, grid_z,"
                " block_x, block_y, block_z, shared_mem, occurrences, prologue, epilogue)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (kernel_ids[record["KernelName"]], dyn_hash, g["x"], g["y"], g["z"],
                 bl["x"], bl["y"], bl["z"], inst["SharedMem"], inst["Occurrences"],
                 os.path.join(record_dir, inst["Prologue"]),
                 os.path.join(record_dir, inst["Epilogue"])))

    for path in launch_paths:
        if path.kernel not in kernel_ids:
            # Launched but not recorded by Mneme, e.g. a library kernel.
            fid = b.function_id("kernel", path.kernel)
            cur = conn.execute(
                "INSERT INTO kernels(function_id, mangled_name, isa_text, isa_instructions)"
                " VALUES (?, ?, ?, ?)",
                (fid, path.kernel, isa_texts.get(path.kernel),
                 isa.instruction_count(isa_texts[path.kernel]) if isa_texts.get(path.kernel) else None))
            kernel_ids[path.kernel] = cur.lastrowid
        kernel_fid = conn.execute("SELECT function_id FROM kernels WHERE id = ?",
                                  (kernel_ids[path.kernel],)).fetchone()[0]
        conn.execute(
            "INSERT INTO launch_paths(kernel_id, frames, grid_x, grid_y, grid_z,"
            " block_x, block_y, block_z, shared_mem, count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (kernel_ids[path.kernel],
             json.dumps([{"function": f.function, "file": f.file, "line": f.line} for f in path.frames]),
             *path.grid, *path.block, path.shared_mem, path.count))

        frame_ids = [b.function_id("host", f.function, f.function, f.file, f.start_line)
                     for f in path.frames]
        for i in range(len(frame_ids) - 1):
            site = path.frames[i]
            b.add_edge(frame_ids[i], frame_ids[i + 1], "stack", site.file, site.line, path.count)
        if frame_ids:
            site = path.frames[-1]
            b.add_edge(frame_ids[-1], kernel_fid, "launch", site.file, site.line, path.count)


def export_graph(db_path: str, graph_path: str, include_runtime: bool = False) -> str:
    """Write the database as a nodes/edges JSON graph.

    Containment edges form the hierarchy program -> file -> function -> loop ->
    basic block; call and launch edges cross it. HIP runtime helpers are left
    out unless ``include_runtime`` is set.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    nodes, edges = [], []

    def node(node_id, kind, label, **attrs):
        nodes.append({"id": node_id, "kind": kind, "label": label, **attrs})

    def edge(source, target, kind, **attrs):
        edges.append({"source": source, "target": target, "kind": kind, **attrs})

    for p in conn.execute("SELECT * FROM programs"):
        node(f"program:{p['id']}", "program", p["name"], executable=p["executable"],
             arguments=json.loads(p["arguments"]), gpu_arch=p["gpu_arch"], hostname=p["hostname"])
    visible_files = {row[0] for row in conn.execute(
        "SELECT DISTINCT file_id FROM functions WHERE file_id IS NOT NULL"
        + ("" if include_runtime else " AND NOT is_runtime"))}
    for f in conn.execute("SELECT * FROM source_files"):
        if f["id"] not in visible_files:
            continue
        node(f"file:{f['id']}", "source_file", os.path.basename(f["path"]), path=f["path"])
        edge(f"program:{f['program_id']}", f"file:{f['id']}", "contains")
    hidden = set()
    for fn in conn.execute("SELECT * FROM functions"):
        if fn["is_runtime"] and not include_runtime:
            hidden.add(fn["id"])
            continue
        node(f"function:{fn['id']}", f"{fn['kind']}_function", fn["display_name"],
             name=fn["name"], line=fn["line"])
        parent = f"file:{fn['file_id']}" if fn["file_id"] else f"program:{fn['program_id']}"
        edge(parent, f"function:{fn['id']}", "contains")
    for k in conn.execute("SELECT * FROM kernels"):
        node(f"function:{k['function_id']}", "kernel_function", k["demangled_name"] or k["mangled_name"],
             name=k["mangled_name"], source_line=k["source_line"],
             source_end_line=k["source_end_line"], isa_instructions=k["isa_instructions"])
    for inst in conn.execute("SELECT i.*, k.function_id FROM kernel_instances i JOIN kernels k ON k.id = i.kernel_id"):
        node(f"instance:{inst['id']}", "kernel_instance", inst["dynamic_hash"],
             grid=[inst["grid_x"], inst["grid_y"], inst["grid_z"]],
             block=[inst["block_x"], inst["block_y"], inst["block_z"]],
             shared_mem=inst["shared_mem"], occurrences=inst["occurrences"])
        edge(f"function:{inst['function_id']}", f"instance:{inst['id']}", "has_instance")
    for loop in conn.execute("SELECT * FROM loops"):
        if loop["function_id"] in hidden:
            continue
        node(f"loop:{loop['id']}", "loop", loop["header"], depth=loop["depth"])
        parent = f"loop:{loop['parent_id']}" if loop["parent_id"] else f"function:{loop['function_id']}"
        edge(parent, f"loop:{loop['id']}", "contains")
    for bb in conn.execute("SELECT * FROM basic_blocks"):
        if bb["function_id"] in hidden:
            continue
        node(f"block:{bb['id']}", "basic_block", bb["label"], instructions=bb["instructions"],
             first_line=bb["first_line"], last_line=bb["last_line"])
        parent = f"loop:{bb['loop_id']}" if bb["loop_id"] else f"function:{bb['function_id']}"
        edge(parent, f"block:{bb['id']}", "contains")
    for e in conn.execute("SELECT * FROM call_edges"):
        if e["caller_id"] in hidden or e["callee_id"] in hidden:
            continue
        edge(f"function:{e['caller_id']}", f"function:{e['callee_id']}",
             "launches" if e["origin"] == "launch" else "calls", origin=e["origin"],
             call_file=e["call_file"], call_line=e["call_line"], launches=e["launches"])

    # Kernel rows re-describe their function node; keep the richer, later one.
    unique = {}
    for n in nodes:
        unique[n["id"]] = {**unique.get(n["id"], {}), **n}
    with open(graph_path, "w") as f:
        json.dump({"nodes": list(unique.values()), "edges": edges}, f, indent=1)
    conn.close()
    return graph_path
