from findingmnemo.export import (_Function, _body, _dir_name, _is_runtime_function, _lambda_lines,
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
    assert not _is_runtime_function("_Z6kernelPd", "/src/app/kernel.hip")
    assert not _is_runtime_function("_Z1fv", "/src/clang/tools/include/f.h")
    assert not _is_runtime_function("_Z1fv", None)
