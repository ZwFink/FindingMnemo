import json
import os
import shutil

import pytest

from findingmnemo.relocate import copy, run_dir


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)


_FUNCTION = {"file": "files/k.cpp", "mneme_record": "record-db/1.json"}


def _make(tmp_path):
    run = tmp_path / "runs" / "app"
    _write(str(run / "run.json"), {"name": "app"})
    _write(str(run / "record-db" / "1.json"), {"Modules": ["RecordedIR_1.bc"]})
    (run / "record-db" / "snap.mneme").write_text("x")
    _write(str(run / "findingmnemo-db" / "index.json"), {})
    db = tmp_path / "db"
    _write(str(db / "index.json"), {"programs": [{"dir": "app"}]})
    _write(str(db / "app" / "program.json"), {"run_dir": str(run), "executable": "/src/app/app.exe"})
    _write(str(db / "app" / "files" / "k.cpp" / "k" / "function.json"), _FUNCTION)
    return run, db


def _function(db):
    return json.loads((db / "app" / "files" / "k.cpp" / "k" / "function.json").read_text())


def test_copy_with_recordings(tmp_path):
    run, db = _make(tmp_path)
    dest = tmp_path / "shared" / "db"
    copy(str(db), str(dest), recordings=True)

    rec = dest / "app" / "recording"
    assert (rec / "record-db" / "snap.mneme").exists()
    assert not (rec / "findingmnemo-db").exists()
    prog = json.loads((dest / "app" / "program.json").read_text())
    assert prog == {"run_dir": "recording", "executable": "/src/app/app.exe"}
    assert run_dir(str(dest), "app") == str(rec)
    # Paths relative to the database and the run directory are unchanged.
    assert _function(dest) == _FUNCTION
    # The original is unchanged.
    assert json.loads((db / "app" / "program.json").read_text())["run_dir"] == str(run)


def test_copy_without_recordings_keeps_paths(tmp_path):
    run, db = _make(tmp_path)
    dest = tmp_path / "db2"
    copy(str(db), str(dest))
    assert (dest / "app" / "program.json").read_text() == (db / "app" / "program.json").read_text()
    assert not (dest / "app" / "recording").exists()


def test_copy_of_a_copy_points_to_its_own_recording(tmp_path):
    _, db = _make(tmp_path)
    first, second, third = tmp_path / "c1", tmp_path / "c2", tmp_path / "c3"
    copy(str(db), str(first), recordings=True)
    copy(str(first), str(second), recordings=True)
    copy(str(first), str(third))
    for dest in (second, third):
        rec = dest / "app" / "recording"
        assert (rec / "record-db" / "snap.mneme").exists()
        assert json.loads((dest / "app" / "program.json").read_text())["run_dir"] == "recording"
        assert run_dir(str(dest), "app") == str(rec)


def test_absolute_run_dir_inside_the_database_becomes_relative(tmp_path):
    run, db = _make(tmp_path)
    shutil.copytree(str(run), str(db / "app" / "rec"))
    _write(str(db / "app" / "program.json"), {"run_dir": str(db / "app" / "rec")})
    dest = tmp_path / "out"
    copy(str(db), str(dest))
    assert json.loads((dest / "app" / "program.json").read_text())["run_dir"] == "rec"


def test_copy_of_database_exported_into_its_run_dir(tmp_path):
    run, db = _make(tmp_path)
    inner = run / "findingmnemo-db"
    shutil.rmtree(str(inner))
    os.rename(str(db), str(inner))
    dest = tmp_path / "out"
    copy(str(inner), str(dest), recordings=True)
    rec = dest / "app" / "recording"
    assert sorted(os.listdir(str(rec))) == ["record-db", "run.json"]
    assert json.loads((dest / "app" / "program.json").read_text())["run_dir"] == "recording"


def test_copy_leaves_other_fields_alone(tmp_path):
    run, db = _make(tmp_path)
    _write(str(db / "app" / "program.json"),
           {"arguments": [f'-D"run_dir": "{run}"', str(run / "in.txt")], "run_dir": str(run)})
    dest = tmp_path / "out"
    copy(str(db), str(dest), recordings=True)
    prog = json.loads((dest / "app" / "program.json").read_text())
    assert prog == {"arguments": [f'-D"run_dir": "{run}"', str(run / "in.txt")],
                    "run_dir": "recording"}


def test_copy_of_a_copy_through_a_symlink(tmp_path):
    _, db = _make(tmp_path)
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real)
    # The first copy is written through the symlink, the second reads it
    # through the real path, as with /usr/workspace and /usr/WS2 on LC.
    copy(str(db), str(link / "c1"), recordings=True)
    second = tmp_path / "c2"
    copy(str(real / "c1"), str(second))
    assert (second / "app" / "recording" / "record-db" / "snap.mneme").exists()
    assert json.loads((second / "app" / "program.json").read_text())["run_dir"] == "recording"


def test_copy_refuses_dest_inside_db(tmp_path):
    _, db = _make(tmp_path)
    with pytest.raises(SystemExit):
        copy(str(db), str(db / "copy"))
    assert not (db / "copy").exists()


def test_copy_refuses_dest_inside_db_through_a_symlink(tmp_path):
    _, db = _make(tmp_path)
    (tmp_path / "link").symlink_to(db)
    with pytest.raises(SystemExit):
        copy(str(db), str(tmp_path / "link" / "copy"))
    assert not (db / "copy").exists()


def test_failed_copy_leaves_nothing(tmp_path, monkeypatch):
    _, db = _make(tmp_path)

    def fail(*args, **kwargs):
        raise OSError("disk full")
    monkeypatch.setattr(shutil, "copy2", fail)
    dest = tmp_path / "out"
    with pytest.raises(OSError):
        copy(str(db), str(dest), recordings=True)
    assert not dest.exists()


def test_copy_refuses_a_newer_format(tmp_path):
    _, db = _make(tmp_path)
    _write(str(db / "index.json"), {"format": "findingmnemo-db", "version": 99,
                                    "programs": [{"dir": "app"}]})
    with pytest.raises(SystemExit, match="format version 99"):
        copy(str(db), str(tmp_path / "copy"))
    assert not (tmp_path / "copy").exists()
