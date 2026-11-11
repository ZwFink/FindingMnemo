import hashlib
import json

import pytest
from mneme.recorded_execution import RecordedExecution

from findingmnemo.export import (_assign_paths, _Function, _prepare_output, _body, _dir_name, _is_constructor,
                                 _is_runtime_function, _lambda_lines, _launch_totals, _recorded_copy,
                                 _short_name)
from findingmnemo.ir import BasicBlock, Function, Loop


class _NoFunctions:
    functions = {}
    runtime = set()


def test_body_nests_blocks_in_loops():
    fn = Function("f", file="k.cpp", blocks=[
        BasicBlock("entry", 3, [("k.cpp", 10)]),
        BasicBlock("outer", 2, [("k.cpp", 11)]),
        BasicBlock("inner", 4, [("k.cpp", 12), ("k.cpp", 13)], [("g", ("k.cpp", 13))]),
        BasicBlock("latch", 1),
        BasicBlock("exit", 1, [("k.cpp", 15)]),
    ], loops=[
        Loop(1, "outer", ["outer", "inner", "latch"]),
        Loop(2, "inner", ["inner"], parent=0),
    ])
    assert _body(_NoFunctions(), fn) == [
        {"block": "entry", "instructions": 3, "lines": [10, 10]},
        {"loop": "outer", "depth": 1, "body": [
            {"block": "outer", "instructions": 2, "lines": [11, 11]},
            {"loop": "inner", "depth": 2, "body": [
                {"block": "inner", "instructions": 4, "lines": [12, 13], "calls": ["g"]},
            ]},
            {"block": "latch", "instructions": 1},
        ]},
        {"block": "exit", "instructions": 1, "lines": [15, 15]},
    ]


def test_short_name_drops_parameters_and_return_type():
    assert _short_name("run(Inputs, SimulationData, int)") == "run"
    assert _short_name("void vecAdd_test<long>(long*, long*, unsigned long)") == "vecAdd_test<long>"
    assert _short_name("ns::Functor::operator()(int) const") == "ns::Functor::operator()"
    assert _short_name("main::'lambda'(double, int)::operator()(double, int) const") \
        == "main::'lambda'(double, int)::operator()"
    assert _short_name("std::ostream& operator<<(std::ostream&, Foo const&)") == "operator<<"
    assert _short_name("main::'lambda'(double, int)::operator()(double, int) const::'lambda'(int)"
                       "::operator()(int) const") \
        == "main::'lambda'(double, int)::operator()(double, int) const::'lambda'(int)::operator()"
    assert _short_name("operator()") == "operator()"
    assert _short_name("main") == "main"


def _fn(kind, display, debug=None, file="app.hip", line=None):
    return _Function(kind, display, display, debug, file, line)


def test_is_constructor():
    assert _is_constructor("RAJA::expt::ValLoc<double, long>::ValLoc(double)")
    assert _is_constructor("Box::Box()")
    assert _is_constructor("ns::Box<int>::Box<float>(float) const")
    assert not _is_constructor("ns::Box<int>::~Box()")
    assert not _is_constructor("ns::f(int)")
    assert not _is_constructor("f(int)")
    assert not _is_constructor("main::'lambda'(int)::operator()(int) const")


def test_dir_name_names_lambdas_by_line():
    outer = _fn("host", "main::'lambda'(double, int)::operator()(double, int) const", line=31)
    inner = _fn("device", "main::'lambda'(double, int)::operator()(double, int) const"
                "::'lambda'(int)::operator()(int) const", "operator()", line=33)
    lines = _lambda_lines([outer, inner])
    assert _dir_name(outer, lines) == "lambda@31"
    assert _dir_name(inner, lines) == "lambda@33"
    # Full DWARF gives host frames demangled names.
    assert _dir_name(_fn("host", "void launch<main::'lambda'(double, int)::operator()(double, int) "
                         "const::'lambda'(int)>(int, main::'lambda'(double, int)::operator()"
                         "(double, int) const::'lambda'(int))"), lines) == "launch[lambda@33]"
    # -gline-tables-only gives clang's own spelling.
    assert _dir_name(_fn("kernel", "void forall<main::'lambda'(int)>(int, main::'lambda'(int))",
                         "forall<(lambda at app.hip:28:13)>"), {}) == "forall[lambda@28]"
    assert _dir_name(_fn("host", "launch<(lambda at other.hip:7:3)>"), {}) \
        == "launch[lambda@other.hip-7]"
    # Without a known body, the lambda keeps its scope.
    assert _dir_name(_fn("kernel", "void forall<main::'lambda'(int)>(int, main::'lambda'(int))"),
                     {}) == "forall[main.lambda]"


def test_dir_name_abbreviates_long_template_arguments():
    name = ("forall_kernel<RAJA::policy::hip::hip_exec<RAJA::iteration_mapping::Direct, "
            "RAJA::hip::IndexGlobal<(RAJA::named_dim)0, 256, 0>, true>, "
            "RAJA::Iterators::numeric_iterator<long, long, long*>, (lambda at app.hip:41:5), long>")
    assert _dir_name(_fn("kernel", name, name), {}) == "forall_kernel[lambda@41]"


def test_runtime_functions_include_clang_headers():
    rocm = "/opt/rocm-6.4.0/lib/llvm/lib/clang/19/include/"
    assert _is_runtime_function("_ZL4fabsd", rocm + "__clang_hip_math.h")
    assert _is_runtime_function("_ZL3absd", rocm + "__clang_hip_cmath.h")
    assert _is_runtime_function("_ZL4sqrtf",
                                "/usr/lib/llvm-19/lib/clang/19.1.0/include/__clang_cuda_math.h")
    assert _is_runtime_function("f", "/opt/rocm/include/hip/amd_detail/amd_device_functions.h")
    assert _is_runtime_function("__ocml_fabs_f64", None)
    # OCML's internal helpers, which the device libraries build without debug info.
    assert _is_runtime_function("__ocmlpriv_epln_f64", None)
    assert not _is_runtime_function("_Z6kernelPd", "/src/app/kernel.hip")
    assert not _is_runtime_function("_Z1fv", "/src/clang/tools/include/f.h")
    assert not _is_runtime_function("_Z1fv", None)


def test_function_paths_leave_room_for_the_files_own_entries():
    class Prog:
        functions = {("host", name): _fn("host", name, file="/src/app.hip", line=n)
                     for n, name in enumerate(["source::hip(int)", "file::json()", "run()"], 1)}
    file_dirs = _assign_paths(Prog())
    assert file_dirs == {"/src/app.hip": "files/app.hip"}
    paths = sorted(fn.path for fn in Prog.functions.values())
    assert "files/app.hip/source.hip" not in paths
    assert "files/app.hip/file.json" not in paths
    assert "files/app.hip/run" in paths
    assert len(set(paths)) == 3


def test_files_named_only_by_call_sites_get_directories():
    class Prog:
        functions = {("host", "main"): _fn("host", "main", file="/src/app.hip", line=3),
                     ("host", "run"): _fn("host", "run", file="/lib/app.hip", line=9)}
    file_dirs = _assign_paths(Prog(), ["/src/util.h", "/src/app.hip"])
    # Files of functions keep the names they get without call sites.
    assert file_dirs == {"/lib/app.hip": "files/app.hip", "/src/app.hip": "files/app.hip~2",
                         "/src/util.h": "files/util.h"}


def test_recorded_copy_is_only_mnemes_copy(tmp_path):
    original, copy = tmp_path / "app.hip", tmp_path / "RecordedSource_app.hip"
    original.write_text("__global__ void k() {}\n")
    text = original.read_text()
    md5 = hashlib.md5(text.encode()).hexdigest()

    def execution(source_copy):
        # Only the source fields; kernel_source() reads nothing else.
        e = RecordedExecution.__new__(RecordedExecution)
        e.source_file, e.source_copy, e.source_md5 = str(original), source_copy, md5
        e.source_line = e.source_end_line = 1
        return e

    # Recorded without --copy-source: kernel_source() reads the original.
    assert execution(None).kernel_source().file == str(original)
    assert _recorded_copy(execution(None)) is None
    # The copy was deleted from the record directory.
    assert _recorded_copy(execution(str(copy))) is None
    copy.write_text(text)
    assert _recorded_copy(execution(str(copy))) == str(copy)


def test_launch_totals_come_from_the_mneme_record():
    assert _launch_totals({"TotalLaunches": 7, "TotalTimeNs": 31160, "TimingSource": "profiler"}) \
        == {"launch_count": 7, "gpu_time_ns": 31160}
    # Recorded without MNEME_KERNEL_TIMING, or by a Mneme that did not count launches.
    assert _launch_totals({"TotalLaunches": 7}) == {"launch_count": 7}
    assert _launch_totals({}) == {}


@pytest.mark.parametrize("index", [{"format": "findingmnemo-db/1"},
                                   {"format": "findingmnemo-db", "version": 2},
                                   {"format": "findingmnemo-db", "version": 99}])
def test_export_replaces_a_database_of_any_version(tmp_path, index):
    db = tmp_path / "db"
    db.mkdir()
    (db / "index.json").write_text(json.dumps(index))
    _prepare_output(str(db))
    assert not db.exists()


def test_export_keeps_a_directory_that_is_not_a_database(tmp_path):
    (tmp_path / "index.json").write_text(json.dumps({"format": "other"}))
    with pytest.raises(SystemExit, match="not a FindingMnemo database"):
        _prepare_output(str(tmp_path))
    assert (tmp_path / "index.json").exists()
