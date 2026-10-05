"""Command-line entry point: ``findingmnemo record`` and ``findingmnemo export``."""

import argparse
import datetime
import json
import os
import shutil
import socket
import subprocess
import sys

from . import export

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SHIM = os.path.join(REPO_ROOT, "lib", "libfindingmnemo_stacks.so")

# Prepends the shim to whatever LD_PRELOAD `mneme record` set, then runs the
# application. `mneme record` overwrites LD_PRELOAD, so the shim cannot be
# passed in from outside.
_PRELOAD_WRAPPER = 'LD_PRELOAD="$FINDINGMNEMO_SHIM${LD_PRELOAD:+:$LD_PRELOAD}" exec "$@"'


def _mneme_config(key: str) -> str:
    return subprocess.run(["mneme", "config", key], check=True,
                          capture_output=True, text=True).stdout.strip()


def _default_llvm_bin() -> str:
    if os.environ.get("FINDINGMNEMO_LLVM_BIN"):
        return os.environ["FINDINGMNEMO_LLVM_BIN"]
    rocm = os.environ.get("ROCM_PATH", "/opt/rocm")
    return os.path.join(rocm, "llvm", "bin")


def record(args) -> int:
    cmd = args.cmd[1:] if args.cmd[:1] == ["--"] else args.cmd
    if not cmd:
        sys.exit("findingmnemo record: missing application command after --")
    shim = os.path.abspath(args.shim)
    if not os.path.exists(shim):
        sys.exit(f"findingmnemo record: shim not found at {shim}; run `make` first")

    out = os.path.abspath(args.output)
    stack_dir = os.path.join(out, "stacks")
    os.makedirs(stack_dir, exist_ok=True)
    executable = shutil.which(cmd[0]) or cmd[0]
    with open(os.path.join(out, "run.json"), "w") as f:
        json.dump({
            "name": args.name or os.path.basename(executable),
            "executable": os.path.abspath(executable),
            "arguments": cmd[1:],
            "cwd": os.getcwd(),
            "hostname": socket.gethostname(),
            "recorded_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "mneme": not args.no_mneme,
        }, f, indent=2)

    env = os.environ.copy()
    env["FINDINGMNEMO_OUT"] = stack_dir
    env["FINDINGMNEMO_SHIM"] = shim
    if args.no_mneme:
        env["LD_PRELOAD"] = shim + (":" + env["LD_PRELOAD"] if env.get("LD_PRELOAD") else "")
        return subprocess.run(cmd, env=env).returncode

    # The preload wrapper shell also gets Mneme's record library preloaded,
    # and that library needs Mneme's runtime library on the search path.
    libdir = _mneme_config("libdir")
    env["LD_LIBRARY_PATH"] = libdir + (":" + env["LD_LIBRARY_PATH"] if env.get("LD_LIBRARY_PATH") else "")
    mneme = ["mneme", "record", "-rdb", os.path.join(out, "record-db"), "--copy-source",
             *args.mneme_args, "--", "/bin/sh", "-c", _PRELOAD_WRAPPER, "sh", *cmd]
    return subprocess.run(mneme, env=env).returncode


def export_cmd(args) -> int:
    if len(args.run_dirs) > 1 and not args.db:
        sys.exit("findingmnemo export: pass --db when exporting several run directories")
    db = args.db or os.path.join(args.run_dirs[0], "findingmnemo.sqlite")
    export.build(args.run_dirs, db, args.llvm_bin)
    graph = export.export_graph(db, args.graph or os.path.splitext(db)[0] + ".graph.json",
                                args.include_runtime)
    print(f"database: {db}\ngraph:    {graph}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="findingmnemo", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    rec = sub.add_parser("record", help="run an application under Mneme and capture launch stacks")
    rec.add_argument("-o", "--output", required=True, help="run directory to create")
    rec.add_argument("--name", help="program name stored in the database (default: executable name)")
    rec.add_argument("--shim", default=DEFAULT_SHIM, help="path to libfindingmnemo_stacks.so")
    rec.add_argument("--no-mneme", action="store_true",
                     help="capture launch stacks only, without recording kernels")
    rec.add_argument("--mneme-arg", dest="mneme_args", action="append", default=[],
                     help="extra argument for `mneme record` (repeatable)")
    rec.add_argument("cmd", nargs=argparse.REMAINDER, help="-- application [arguments]")
    rec.set_defaults(func=record)

    exp = sub.add_parser("export", help="build the SQLite database and graph JSON from a run directory")
    exp.add_argument("run_dirs", nargs="+", metavar="run_dir",
                     help="run directories; each becomes one program in the database")
    exp.add_argument("--db", help="SQLite output (default: <run_dir>/findingmnemo.sqlite)")
    exp.add_argument("--graph", help="graph JSON output (default: next to the database, *.graph.json)")
    exp.add_argument("--include-runtime", action="store_true",
                     help="keep HIP runtime helper functions in the graph")
    exp.add_argument("--llvm-bin", default=_default_llvm_bin(),
                     help="directory with llvm-dis, opt, llvm-symbolizer, llvm-objdump, "
                          "clang-offload-bundler (default: $ROCM_PATH/llvm/bin)")
    exp.set_defaults(func=export_cmd)

    args = parser.parse_args(argv)
    return args.func(args)
