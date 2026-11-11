"""Copy a database to another directory, optionally with its Mneme recordings.

Paths in a database are relative to it, except each program's ``run_dir``
(its Mneme recording and launch stacks, which ``mneme_record`` and the
``prologue``/``epilogue`` snapshots are relative to) and the provenance fields
``executable`` and ``original_path``. A relative ``run_dir`` is relative to
the program directory. So a database can be copied as is; with
``recordings``, each program's run directory is copied into the new database
as well and ``run_dir`` points to it there.
"""

import json
import os
import re
import shutil
from typing import List, Tuple

from . import dbformat

# The parts of a run directory that the database refers to. A run directory
# can also hold a database exported into it, which is not copied.
_RUN_PARTS = ("run.json", "stacks", "record-db")
RECORDING = "recording"


def run_dir(db: str, prog_dir: str) -> str:
    """The absolute run directory of a program in ``db``."""
    with open(os.path.join(db, prog_dir, "program.json")) as f:
        path = json.load(f)["run_dir"]
    return os.path.normpath(os.path.join(db, prog_dir, path))


def _programs(db: str) -> List[Tuple[str, str]]:
    """(program directory, absolute run directory) of each program in ``db``."""
    with open(os.path.join(db, "index.json")) as f:
        index = json.load(f)
    return [(prog["dir"], run_dir(db, prog["dir"])) for prog in index["programs"]]


def _inside_real(path: str, directory: str) -> bool:
    """Whether ``path`` is ``directory`` or under it, after resolving symlinks."""
    path, directory = os.path.realpath(path), os.path.realpath(directory)
    return path == directory or path.startswith(directory.rstrip("/") + "/")


_RUN_DIR_FIELD = re.compile(r'("run_dir":\s*)"(?:[^"\\]|\\.)*"')


def _set_run_dir(program_json: str, value: str) -> None:
    """Set ``run_dir``, editing the file as text to keep its formatting."""
    with open(program_json) as f:
        text = f.read()
    with open(program_json, "w") as f:
        f.write(_RUN_DIR_FIELD.sub(lambda m: m.group(1) + json.dumps(value), text, count=1))


def _copy(db: str, dest: str, programs: List[Tuple[str, str]], recordings: bool) -> None:
    shutil.copytree(db, dest)
    for prog_dir, run in programs:
        program_json = os.path.join(dest, prog_dir, "program.json")
        if _inside_real(run, db):
            # A recording inside the database, as in a copy, was copied with
            # it; point to that copy relative to the program directory.
            _set_run_dir(program_json, os.path.relpath(os.path.realpath(run),
                                                       os.path.realpath(os.path.join(db, prog_dir))))
        elif recordings:
            target = os.path.join(dest, prog_dir, RECORDING)
            os.makedirs(target)
            for part in _RUN_PARTS:
                src = os.path.join(run, part)
                if os.path.isdir(src):
                    shutil.copytree(src, os.path.join(target, part))
                elif os.path.isfile(src):
                    shutil.copy2(src, target)
            _set_run_dir(program_json, RECORDING)


def copy(db: str, dest: str, recordings: bool = False) -> None:
    """Copy database ``db`` to ``dest``, which must not exist.

    With ``recordings``, each program's run directory is copied to
    ``dest/<program>/recording/`` and the database points there, so the copy
    holds everything it refers to. Nothing is left at ``dest`` if the copy
    fails.
    """
    db, dest = os.path.abspath(db), os.path.abspath(dest)
    if not os.path.isfile(os.path.join(db, "index.json")):
        raise SystemExit(f"findingmnemo copy: {db} is not a database (no index.json)")
    version = dbformat.read_version(db)
    if version is not None and version > dbformat.VERSION:
        raise SystemExit(f"findingmnemo copy: {db} has format version {version}, newer than "
                         f"this FindingMnemo's {dbformat.VERSION}; update FindingMnemo")
    if os.path.exists(dest):
        raise SystemExit(f"findingmnemo copy: {dest} already exists")
    if _inside_real(dest, db):
        raise SystemExit(f"findingmnemo copy: {dest} is inside the database")

    programs = _programs(db)
    if recordings:
        for prog_dir, run in programs:
            if not os.path.isfile(os.path.join(run, "run.json")):
                raise SystemExit(f"findingmnemo copy: recording of {prog_dir} not found at {run}")
            if any(_inside_real(dest, os.path.join(run, part)) for part in _RUN_PARTS):
                raise SystemExit(f"findingmnemo copy: {dest} is inside the recording it would copy")
    try:
        _copy(db, dest, programs, recordings)
    except BaseException:
        shutil.rmtree(dest, ignore_errors=True)
        raise
