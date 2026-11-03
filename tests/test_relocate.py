import json
import os
import shutil

import pytest

from findingmnemo.relocate import copy


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)


def _make(tmp_path):
    run = tmp_path / "runs" / "app"
    _write(str(run / "run.json"), {"name": "app"})
    _write(str(run / "record-db" / "1.json"), {"Modules": ["RecordedIR_1.bc"]})
    (run / "record-db" / "snap.mneme").write_text("x")
    _write(str(run / "findingmnemo-db" / "index.json"), {})
    db = tmp_path / "db"
    _write(str(db / "index.json"), {"programs": [{"dir": "app"}]})
    _write(str(db / "app" / "program.json"), {"run_dir": str(run), "executable": "/src/app/app.exe"})
    _write(str(db / "app" / "files" / "k.cpp" / "k" / "function.json"), {
        "file": "/src/app/k.cpp", "mneme_record": str(run / "record-db" / "1.json"),
        "called_by": [{"file": "/src/app-other/m.cpp"}],
    })
    return run, db


def test_copy_with_recordings_and_map(tmp_path):
    run, db = _make(tmp_path)
    dest = tmp_path / "shared" / "db"
    copy(str(db), str(dest), recordings=True,
         path_map={"/src/app": "/shared/src/app", str(tmp_path / "runs"): "/elsewhere"})

    rec = dest / "app" / "recording"
    assert (rec / "record-db" / "snap.mneme").exists()
    assert not (rec / "findingmnemo-db").exists()
    prog = json.loads((dest / "app" / "program.json").read_text())
    # The run directory goes to its copy, not to the shorter mapped prefix.
    assert prog == {"run_dir": str(rec), "executable": "/shared/src/app/app.exe"}
    fn = json.loads((dest / "app" / "files" / "k.cpp" / "k" / "function.json").read_text())
    assert fn["file"] == "/shared/src/app/k.cpp"
    assert fn["mneme_record"] == str(rec / "record-db" / "1.json")
    # A prefix matches whole path components only.
    assert fn["called_by"][0]["file"] == "/src/app-other/m.cpp"
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
        assert json.loads((dest / "app" / "program.json").read_text())["run_dir"] == str(rec)


def test_copy_of_database_exported_into_its_run_dir(tmp_path):
    run, db = _make(tmp_path)
    inner = run / "findingmnemo-db"
    shutil.rmtree(str(inner))
    os.rename(str(db), str(inner))
    dest = tmp_path / "out"
    copy(str(inner), str(dest), recordings=True)
    rec = dest / "app" / "recording"
    assert sorted(os.listdir(str(rec))) == ["record-db", "run.json"]
    assert json.loads((dest / "app" / "program.json").read_text())["run_dir"] == str(rec)


def test_copy_leaves_escaped_quotes_alone(tmp_path):
    run, db = _make(tmp_path)
    _write(str(db / "app" / "program.json"),
           {"run_dir": str(run), "arguments": [f'-DDIR="{run}"', str(run / "in.txt")]})
    dest = tmp_path / "out"
    copy(str(db), str(dest), recordings=True)
    args = json.loads((dest / "app" / "program.json").read_text())["arguments"]
    assert args == [f'-DDIR="{run}"', str(dest / "app" / "recording" / "in.txt")]


def test_copy_refuses_dest_inside_db(tmp_path):
    _, db = _make(tmp_path)
    with pytest.raises(SystemExit):
        copy(str(db), str(db / "copy"))
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
