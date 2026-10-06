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
    """Prefer the LLVM that Mneme was built with, which matches the recorded IR."""
    if os.environ.get("FINDINGMNEMO_LLVM_BIN"):
        return os.environ["FINDINGMNEMO_LLVM_BIN"]
    try:
        return os.path.join(_mneme_config("llvmdir"), "bin")
    except (OSError, subprocess.CalledProcessError):
        return os.path.join(os.environ.get("ROCM_PATH", "/opt/rocm"), "llvm", "bin")


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
        }, f, indent=2)

    env = os.environ.copy()
    env["FINDINGMNEMO_OUT"] = stack_dir
    env["FINDINGMNEMO_SHIM"] = shim
    # The preload wrapper shell also gets Mneme's record library preloaded,
    # and that library needs Mneme's runtime library on the search path.
    libdir = _mneme_config("libdir")
    env["LD_LIBRARY_PATH"] = libdir + (":" + env["LD_LIBRARY_PATH"] if env.get("LD_LIBRARY_PATH") else "")
    mneme = ["mneme", "record", "-rdb", os.path.join(out, "record-db"), "--copy-source",
             *args.mneme_args, "--", "/bin/sh", "-c", _PRELOAD_WRAPPER, "sh", *cmd]
    return subprocess.run(mneme, env=env).returncode


def export_cmd(args) -> int:
    if len(args.run_dirs) > 1 and not args.output:
        sys.exit("findingmnemo export: pass -o when exporting several run directories")
    out = args.output or os.path.join(args.run_dirs[0], "findingmnemo-db")
    export.build(args.run_dirs, out, args.llvm_bin)
    print(f"database: {out}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="findingmnemo", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    rec = sub.add_parser("record", help="run an application under Mneme and capture launch stacks")
    rec.add_argument("-o", "--output", required=True, help="run directory to create")
    rec.add_argument("--name", help="program name stored in the database (default: executable name)")
    rec.add_argument("--shim", default=DEFAULT_SHIM, help="path to libfindingmnemo_stacks.so")
    rec.add_argument("--mneme-arg", dest="mneme_args", action="append", default=[],
                     help="extra argument for `mneme record` (repeatable)")
    rec.add_argument("cmd", nargs=argparse.REMAINDER, help="-- application [arguments]")
    rec.set_defaults(func=record)

    exp = sub.add_parser("export", help="build the database directory from run directories")
    exp.add_argument("run_dirs", nargs="+", metavar="run_dir",
                     help="run directories; each becomes one program in the database")
    exp.add_argument("-o", "--output",
                     help="database directory to create (default: <run_dir>/findingmnemo-db)")
    exp.add_argument("--llvm-bin", default=_default_llvm_bin(),
                     help="directory with llvm-dis, opt, llvm-symbolizer, llvm-cxxfilt, llvm-objdump and "
                          "clang-offload-bundler (default: Mneme's LLVM)")
    exp.set_defaults(func=export_cmd)

    args = parser.parse_args(argv)
    return args.func(args)
