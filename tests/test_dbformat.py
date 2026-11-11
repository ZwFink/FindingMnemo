import json
import os
import subprocess

from findingmnemo import dbformat


def test_version_of_current_and_old_databases():
    assert dbformat.version_of({"format": "findingmnemo-db", "version": 2}) == 2
    assert dbformat.version_of({"format": "findingmnemo-db/1"}) == 1
    assert dbformat.version_of({"format": "findingmnemo-db"}) is None
    assert dbformat.version_of({"format": "something-else", "version": 2}) is None
    assert dbformat.version_of({}) is None


def test_read_version(tmp_path):
    assert dbformat.read_version(str(tmp_path)) is None
    (tmp_path / "index.json").write_text("not json")
    assert dbformat.read_version(str(tmp_path)) is None
    (tmp_path / "index.json").write_text(json.dumps({"format": dbformat.FORMAT,
                                                      "version": dbformat.VERSION}))
    assert dbformat.read_version(str(tmp_path)) == dbformat.VERSION


def test_commit_names_this_checkout():
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                          cwd=os.path.dirname(dbformat.__file__)).stdout.strip()
    assert head.startswith(dbformat.commit().split("-")[0])
