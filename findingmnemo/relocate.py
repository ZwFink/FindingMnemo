"""Copy a database to another directory, optionally with its Mneme recordings.

A database refers to files outside itself by absolute path: each program's
run directory (``run_dir``), its Mneme recordings (``mneme_record`` and the
``prologue``/``epilogue`` snapshots of each instance), the executable and the
source files. Paths inside the database are relative, so the database
directory itself can be copied as is; this module copies it and rewrites the
absolute paths that point to files that moved.
"""

import json
import os
import re
import shutil
from typing import Dict, List, Tuple

# The parts of a run directory that the database refers to. A run directory
# can also hold a database exported into it, which is not copied.
_RUN_PARTS = ("run.json", "stacks", "record-db")


def _programs(db: str) -> List[Tuple[str, str]]:
    """(program directory, run directory) of each program in ``db``."""
    with open(os.path.join(db, "index.json")) as f:
        index = json.load(f)
    programs = []
    for prog in index["programs"]:
        with open(os.path.join(db, prog["dir"], "program.json")) as f:
            programs.append((prog["dir"], os.path.normpath(json.load(f)["run_dir"])))
    return programs


def _inside(path: str, directory: str) -> bool:
    return path == directory or path.startswith(directory.rstrip("/") + "/")


def _rewrite(path: str, pattern: "re.Pattern", new_for: Dict[str, str]) -> None:
    """Replace old path prefixes with new ones in the strings of a JSON file.

    The file is edited as text so that its formatting stays the same.
    """
    with open(path) as f:
        text = f.read()
    new_text = pattern.sub(lambda m: '"' + new_for[m.group(1)], text)
    if new_text != text:
        with open(path, "w") as f:
            f.write(new_text)


def _copy(db: str, dest: str, programs: List[Tuple[str, str]], recordings: bool,
          prefixes: List[Tuple[str, str]]) -> None:
    shutil.copytree(db, dest)
    if recordings:
        for prog_dir, run_dir in programs:
            # A recording inside the database, as in a copy, was copied with it.
            if _inside(run_dir, db):
                continue
            target = os.path.join(dest, prog_dir, "recording")
            os.makedirs(target)
            for part in _RUN_PARTS:
                src = os.path.join(run_dir, part)
                if os.path.isdir(src):
                    shutil.copytree(src, os.path.join(target, part))
                elif os.path.isfile(src):
                    shutil.copy2(src, target)
            prefixes.append((run_dir, target))
    # A prefix matches a whole JSON string or one that continues with "/". The
    # longest prefix wins, so a run directory inside a mapped directory goes
    # to its own copy, and each string is rewritten once.
    new_for = {json.dumps(old)[1:-1]: json.dumps(new)[1:-1] for old, new in prefixes}
    pattern = re.compile(r'(?<!\\)"(' + "|".join(re.escape(o) for o in sorted(new_for, key=len, reverse=True))
                         + ')(?=["/])')
    for root, _, files in os.walk(dest):
        for name in files:
            if name.endswith(".json"):
                _rewrite(os.path.join(root, name), pattern, new_for)


def copy(db: str, dest: str, recordings: bool = False,
         path_map: Dict[str, str] = None) -> None:
    """Copy database ``db`` to ``dest``, which must not exist.

    With ``recordings``, each program's run directory is copied to
    ``dest/<program>/recording/`` and the database points there. ``path_map``
    rewrites other path prefixes, for files moved by hand (sources, an
    executable, recordings already copied elsewhere). Paths into ``db`` itself
    always point to the copy. Nothing is left at ``dest`` if the copy fails.
    """
    db, dest = os.path.abspath(db), os.path.abspath(dest)
    if not os.path.isfile(os.path.join(db, "index.json")):
        raise SystemExit(f"findingmnemo copy: {db} is not a database (no index.json)")
    if os.path.exists(dest):
        raise SystemExit(f"findingmnemo copy: {dest} already exists")
    if _inside(dest, db):
        raise SystemExit(f"findingmnemo copy: {dest} is inside the database")

    programs = _programs(db)
    if recordings:
        for prog_dir, run_dir in programs:
            if not os.path.isfile(os.path.join(run_dir, "run.json")):
                raise SystemExit(f"findingmnemo copy: recording of {prog_dir} not found at {run_dir}")
            if any(_inside(dest, os.path.join(run_dir, part)) for part in _RUN_PARTS):
                raise SystemExit(f"findingmnemo copy: {dest} is inside the recording it would copy")

    prefixes = [(os.path.normpath(old), os.path.normpath(new))
                for old, new in (path_map or {}).items()]
    prefixes.append((db, dest))
    try:
        _copy(db, dest, programs, recordings, prefixes)
    except BaseException:
        shutil.rmtree(dest, ignore_errors=True)
        raise
