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


def _inside_real(path: str, directory: str) -> bool:
    """Whether ``path`` is ``directory`` or under it, after resolving symlinks."""
    return _inside(os.path.realpath(path), os.path.realpath(directory))


def _spellings(path: str) -> List[str]:
    """``path`` and, if a symlink leads to it, the path it resolves to.

    A database stores paths as they were spelled when it was written, which
    can go through a symlink (``/usr/workspace`` on LC) or not, so a prefix is
    matched in both forms.
    """
    real = os.path.realpath(path)
    return [path] if real == path else [path, real]


def _db_spellings(db: str, programs: List[Tuple[str, str]]) -> List[str]:
    """The ways paths into ``db`` may be spelled in it.

    Besides ``db`` and its real path, a recording inside ``db`` (as in a copy)
    gives the spelling the database was written with: its ``run_dir`` less
    its path inside ``db``.
    """
    real_db = os.path.realpath(db)
    found = _spellings(db)
    for _, run_dir in programs:
        real_run = os.path.realpath(run_dir)
        if not _inside(real_run, real_db):
            continue
        rel = os.path.relpath(real_run, real_db)
        if rel == ".":
            found.append(run_dir)
        elif run_dir.endswith("/" + rel):
            found.append(run_dir[:-len(rel) - 1])
    return list(dict.fromkeys(found))


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


_RUN_DIR_FIELD = re.compile(r'("run_dir":\s*)"(?:[^"\\]|\\.)*"')


def _copy(db: str, dest: str, programs: List[Tuple[str, str]], recordings: bool,
          prefixes: List[Tuple[str, str]]) -> None:
    shutil.copytree(db, dest)
    moved = []
    if recordings:
        for prog_dir, run_dir in programs:
            # A recording inside the database, as in a copy, was copied with it.
            if _inside_real(run_dir, db):
                continue
            target = os.path.join(dest, prog_dir, "recording")
            os.makedirs(target)
            for part in _RUN_PARTS:
                src = os.path.join(run_dir, part)
                if os.path.isdir(src):
                    shutil.copytree(src, os.path.join(target, part))
                elif os.path.isfile(src):
                    shutil.copy2(src, target)
                else:
                    continue
                # Only the copied parts move. Other files in the run
                # directory, such as the application's inputs, keep their
                # paths, which still work.
                for old in _spellings(run_dir):
                    prefixes.append((os.path.join(old, part), os.path.join(target, part)))
            moved.append((prog_dir, target))
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
    # The run directory itself is named only by program.json's run_dir.
    for prog_dir, target in moved:
        path = os.path.join(dest, prog_dir, "program.json")
        with open(path) as f:
            text = f.read()
        with open(path, "w") as f:
            f.write(_RUN_DIR_FIELD.sub(lambda m: m.group(1) + json.dumps(target), text, count=1))


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
    if _inside_real(dest, db):
        raise SystemExit(f"findingmnemo copy: {dest} is inside the database")

    programs = _programs(db)
    if recordings:
        for prog_dir, run_dir in programs:
            if not os.path.isfile(os.path.join(run_dir, "run.json")):
                raise SystemExit(f"findingmnemo copy: recording of {prog_dir} not found at {run_dir}")
            if any(_inside_real(dest, os.path.join(run_dir, part)) for part in _RUN_PARTS):
                raise SystemExit(f"findingmnemo copy: {dest} is inside the recording it would copy")

    prefixes = [(spelling, os.path.normpath(new))
                for old, new in (path_map or {}).items()
                for spelling in _spellings(os.path.normpath(old))]
    prefixes += [(spelling, dest) for spelling in _db_spellings(db, programs)]
    try:
        _copy(db, dest, programs, recordings, prefixes)
    except BaseException:
        shutil.rmtree(dest, ignore_errors=True)
        raise
