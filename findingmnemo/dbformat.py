"""The database format's name and version, which ``index.json`` records.

Bump ``VERSION`` when a change would make a reader of an existing database
wrong: a key, file or directory renamed, moved or removed, a value whose
meaning or units change, or a change in how directories are named. Adding a
key or a file does not need a new version. Each version is described under
"Format versions" in the README.
"""

import json
import os
import subprocess
from typing import Optional

FORMAT = "findingmnemo-db"
VERSION = 2


def version_of(index: dict) -> Optional[int]:
    """The format version of a database whose ``index.json`` is ``index``.

    None if it is not a FindingMnemo database. Databases written before the
    version was a number of its own have ``"format": "findingmnemo-db/1"``.
    """
    fmt = index.get("format")
    if fmt == FORMAT and isinstance(index.get("version"), int):
        return index["version"]
    if fmt == FORMAT + "/1":
        return 1
    return None


def read_version(db: str) -> Optional[int]:
    """The format version of the database at ``db``, or None if it is not one."""
    try:
        with open(os.path.join(db, "index.json")) as f:
            index = json.load(f)
    except (OSError, ValueError):
        return None
    return version_of(index) if isinstance(index, dict) else None


def commit() -> Optional[str]:
    """The FindingMnemo commit running, or None if it cannot be told.

    In a git checkout, ``git describe`` of it, with ``-dirty`` for uncommitted
    changes. In a ``git archive`` snapshot, the commit that ``git archive``
    wrote into ``COMMIT`` (see ``.gitattributes``).
    """
    package = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(package, "COMMIT")) as f:
            archived = f.read().strip()
    except OSError:
        archived = ""
    if archived and not archived.startswith("$Format"):
        return archived
    git = lambda *args: subprocess.run(["git", *args], cwd=package, capture_output=True,
                                       text=True, timeout=10)
    try:
        top = git("rev-parse", "--show-toplevel")
        if top.returncode or os.path.realpath(top.stdout.strip()) != os.path.realpath(os.path.dirname(package)):
            return None
        out = git("describe", "--always", "--dirty", "--abbrev=12")
    except (OSError, subprocess.SubprocessError):
        return None
    return (out.stdout.strip() or None) if out.returncode == 0 else None
