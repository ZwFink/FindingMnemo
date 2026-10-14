import os
import shutil
import subprocess
import textwrap

import pytest

from findingmnemo import ir
from findingmnemo.export import _Function, _function_source, _Program
from findingmnemo.preprocess import (CompileUnit, PreprocessError, build_view, compile_units,
                                     function_end, parse_output, preprocess, preprocess_argv,
                                     split_command)


def _src(text: str) -> str:
    return textwrap.dedent(text).lstrip("\n")


# Recorded commands and compile units


def test_split_command_undoes_record_command_line_escapes():
    assert split_command(r"clang -I/a\ b -DX=\"y\" -DP=C:\\dir  in.hip") \
        == ["clang", "-I/a b", '-DX="y"', r"-DP=C:\dir", "in.hip"]


MODULE = r"""
define void @k() #0 !dbg !5 {
  ret void
}
attributes #0 = { "target-cpu"="gfx90a" }
!llvm.dbg.cu = !{!0}
!0 = distinct !DICompileUnit(language: DW_LANG_C_plus_plus_14, file: !1, producer: "clang", isOptimized: true, flags: "/rocm/bin/clang-19 -DMSG=\5C\22hi\5C\22 -I/src/my\\ dir -c k.hip -o k.o", runtimeVersion: 0, emissionKind: LineTablesOnly)
!1 = !DIFile(filename: "k.hip", directory: "/src/my dir", checksumkind: CSK_MD5, checksum: "0123456789abcdef0123456789abcdef")
!2 = !DIFile(filename: "/src/my dir/inc/../h.h", directory: "", checksumkind: CSK_MD5, checksum: "fedcba9876543210fedcba9876543210")
!5 = distinct !DISubprogram(name: "k", scope: !1, file: !1, line: 3, unit: !0)
"""


def test_compile_units_reads_command_file_and_checksums():
    unit, = compile_units(MODULE)
    assert unit.argv == ["/rocm/bin/clang-19", '-DMSG="hi"', "-I/src/my dir", "-c", "k.hip",
                         "-o", "k.o"]
    assert (unit.directory, unit.file) == ("/src/my dir", "/src/my dir/k.hip")
    # Without -mcpu on the command line, the module's target-cpu says.
    assert unit.arch == "gfx90a"
    assert unit.checksums == {"/src/my dir/k.hip": "0123456789abcdef0123456789abcdef",
                              "/src/my dir/h.h": "fedcba9876543210fedcba9876543210"}


def test_compile_units_needs_a_recorded_command():
    assert compile_units(MODULE.replace(r'flags: "', 'x: "')) == []


def _unit(argv, arch="gfx942"):
    return CompileUnit(argv, "/src", "/src/k.hip", arch)


TAIL = ["--no-offload-arch=all", "--offload-arch=gfx942", "-E", "-C", "-fdirectives-only",
        "--offload-device-only", "-Wno-unused-command-line-argument", "-o", "-"]


def test_preprocess_argv_removes_only_what_breaks_preprocessing():
    kept = [
        "--driver-mode=g++", "--offload-arch=gfx90a", "--offload-arch=gfx942", "-std=c++17",
        "-O3", "-DA=1", "-D", "B", "-UC", "-I", "inc", "-Iinc2", "-isystem", "sys",
        "-include", "pre.h", "-Werror",
        # Overridden by what is appended: -E, the last -o, --no-offload-arch=all.
        "-c", "-o", "k.o", "-save-temps=obj", "-ftime-trace", "--offload-host-only",
        # Values the -X options pass on stay with them, even ones that look
        # like options to remove.
        "-Xclang", "-fno-validate-pch", "-Xlinker", "-M", "-Xarch_device", "-DDEVICE",
        # Harmless once the dependency options are removed, or ignored by -E.
        "-MF", "k.d", "-MT", "k.o", "-MQk.o", "-MP", "-MV", "-dD", "-dI", "-CC",
        "-fpass-plugin=/p/libProteusPass.so",
        # An option the code knows nothing about keeps its value.
        "-unknown-separate", "value", "-Wl,--as-needed", "-lm", "other.o",
        "-x", "hip", "k.hip", "-x", "none", "lib.a",
    ]
    removed = [
        # Dependency files and lists, and output that is not the source.
        "-MD", "-MJcdb.json", "-MJ", "cdb.json", "-M", "-MM", "-MMD", "-MG",
        "-P", "-dM", "-###",
        # Frontend plugins and LLVM options.
        "-fplugin=/p/libProteusPass.so",
        "-Xclang", "-mllvm", "-Xclang", "-force-proteus-jit-annotate-all",
        "-Xclang", "-load", "-Xclang", "x.so", "-mllvm", "-some-option", "-mllvm=-other",
        # Recorded for the device compile; the host compile rejects it.
        "-mcpu=gfx942",
    ]
    argv = preprocess_argv(_unit(["/rocm/clang-19", *kept[:20], *removed, *kept[20:]]))
    assert argv == ["/rocm/clang-19", *kept, *TAIL]


def test_preprocess_argv_expands_macros_on_request():
    argv = preprocess_argv(_unit(["clang", "-x", "hip", "./k.hip", "-c"]))
    assert argv == ["clang", "-x", "hip", "./k.hip", "-c", *TAIL]
    # The second run expands macros and drops comments.
    expanded = preprocess_argv(_unit(["clang", "k.hip"]), expand_macros=True)
    assert expanded == ["clang", "k.hip", *[a for a in TAIL if a not in ("-C", "-fdirectives-only")]]


def test_preprocess_argv_adds_a_main_file_the_command_does_not_name():
    assert preprocess_argv(_unit(["clang", "@args.rsp"])) == ["clang", "@args.rsp", *TAIL,
                                                               "/src/k.hip"]


# Preprocessed output


# With macros expanded.
OUTPUT = _src("""
    # 1 "k.hip"
    # 1 "<built-in>" 1
    #define __clang__ 1
    # 1 "<built-in>" 2
    # 1 "/rocm/include/hip.h" 1 3
    #define __device__ __attribute__((device))
    # 2 "k.hip" 2
    # 1 "./inc/defs.h" 1
    #define SQUARE(x) ((x) * (x))
    # 3 "k.hip" 2
    __attribute__((device)) int f(int a) {

      return ((a) * (a));
    # 9 "k.hip"
    }
""")


def test_parse_output_follows_markers():
    files = parse_output(OUTPUT, "/src")
    assert files["/src/k.hip"] == {3: "__attribute__((device)) int f(int a) {",
                                   5: "  return ((a) * (a));", 9: "}"}
    assert files["/src/inc/defs.h"] == {1: "#define SQUARE(x) ((x) * (x))"}
    assert files["<built-in>"] == {1: "#define __clang__ 1"}


def _view(source: str, printed: str, expanded: str = None, path="/src/k.hip"):
    return build_view(path, source, parse_output(printed, "/src")[path],
                      parse_output(expanded or printed, "/src")[path])


SOURCE = _src("""
    #include <hip.h>
    #include "inc/defs.h"
    __device__ int f(int a) {
    #if FAST
      return SQUARE(a);
    #else
      return a;
    #endif
    }
""")

# SOURCE with only directives processed, and FAST defined.
PRINTED = _src("""
    # 1 "k.hip"
    # 1 "/rocm/include/hip.h" 1 3
    #define __device__ __attribute__((device))
    # 2 "k.hip" 2
    # 1 "./inc/defs.h" 1
    #define SQUARE(x) ((x) * (x))
    # 3 "k.hip" 2
    __device__ int f(int a) {

      return SQUARE(a);
    # 9 "k.hip"
    }
""")


def test_view_keeps_what_the_device_compiled():
    view = _view(SOURCE, PRINTED, OUTPUT)
    assert view.kept == [False, False, True, False, True, False, False, False, True]
    assert view.text(3, 9) == _src("""
        __device__ int f(int a) {

          return SQUARE(a);



        }
    """)
    assert view.function_end(3) == 9


def test_view_contradicts_code_on_lines_it_does_not_compile():
    view = _view(SOURCE, PRINTED, OUTPUT)
    # Line 0 is code the compiler made up.
    assert view.contradiction([0, 3, 5, 9]) is None
    assert view.contradiction([9, 7, 5]) == 7       # skipped
    assert view.contradiction([3, 4]) == 4          # a directive
    assert view.contradiction([12]) == 12           # past the end of the file


def _marked(lines):
    """Preprocessor output for k.hip with the given text on each line."""
    out = ['# 1 "k.hip"']
    for n, text in sorted(lines.items()):
        out += [f'# {n} "k.hip"', text]
    return "\n".join(out) + "\n"


def test_view_keeps_lines_whose_macros_expand_to_nothing():
    source = _src("""
        #define CHECK(x)
        #ifdef DEBUG
          trace();
        #else
          CHECK(a)
          // checked
        #endif
        #if 0
          CHECK(b)
        #endif
          use(a);
    """)
    view = _view(source, _marked({1: "#define CHECK(x)", 5: "  CHECK(a)", 6: "  // checked",
                                  11: "  use(a);"}))
    assert view.kept == [False, False, False, False, True, True, False, False, False, False, True]


def test_view_keeps_multi_line_macro_calls_and_pragmas():
    source = _src("""
        x = MAX(a,
                b);
        #pragma unroll
        for (;;) {}
        /* a comment
        #if not a directive
        */
    """)
    view = _view(source, _marked({1: "x = MAX(a,", 2: "        b);", 3: "#pragma unroll",
                                  4: "for (;;) {}", 5: "/* a comment", 6: "#if not a directive",
                                  7: "*/"}),
                 _marked({1: "x = ((a) > (b) ? (a) : (b));", 3: "#pragma unroll",
                          4: "for (;;) {}"}))
    assert view.kept == [True] * 7
    # Braces are counted in the expanded code, without the #pragma.
    assert view.code == {1: "x = ((a) > (b) ? (a) : (b));", 4: "for (;;) {}"}


def test_view_takes_text_from_the_file_with_continued_lines_and_crlf():
    source = ("#define LONG(x) \\\r\n  (x)\r\nint g() {\r\n#ifdef NO\r\n  return 1;\r\n"
              "#endif\r\n\treturn \\\r\n  2;\r\n}\r\n")
    # Clang prints spliced code on its first line and turns the tab into a space.
    view = _view(source, _marked({1: "#define LONG(x) (x)", 3: "int g() {", 7: " return 2;",
                                  9: "}"}))
    assert view.kept == [False, False, True, False, False, False, True, True, True]
    assert view.text(3, 9) == "int g() {\r\n\r\n\r\n\r\n\treturn \\\r\n  2;\r\n}\r\n"


# Function ends


def _end(source: str, start=1, last=None):
    return function_end(_src(source).splitlines(), start, last)


def test_function_end_ignores_braces_in_comments_and_literals():
    assert _end("""
        __device__ char f(int a) {  // }
          const char *s = "}}{";  /* } */
          char c = '}';
          auto r = R"x(}})x";
          int n = 1'000'000;
          /* }
          } */
          return s[a] + c + '{';
        }
        __device__ void g() {}
    """) == 9


def test_function_end_skips_braced_initializers_before_the_body():
    assert _end("""
        __device__ S make(S s = {1, 2},
                          T t = T{}) {
          return {s.x, t.y};
        }
    """) == 4


def test_function_end_handles_member_initializers():
    assert _end("""
        __device__ Box::Box(int w)
            : width{w}, height{2 * w},
              depth(w) {
          if (w) { area(); }
        }
    """) == 5
    # RAJA's ReduceLastBlock_Data: the last initializer is braced and the body
    # is empty.
    assert _end("""
          ReduceLastBlock_Data(const ReduceLastBlock_Data& other)
              : value {other.identity},
                owns_device_pointer {false}
          {}

          ReduceLastBlock_Data& operator=(const ReduceLastBlock_Data&) = default;
    """) == 4


def test_function_end_of_a_lambda_inside_a_call():
    # The first lambda ends at its own brace, not after the second one.
    assert _end("""
        forall(0, n, [=] __device__ (int i) {
          a[i] = 0;
        }, [=] __device__ (int i) {
          b[i] = 0;
        });
    """) == 3


def test_function_end_one_line_function_and_safety_net():
    assert _end("__device__ int one() { return 1; }") == 1
    # A body that would end before the last line with code is not trusted.
    assert _end("""
        int f() {
        }
        int g() { return 0; }
    """, last=3) is None
    assert _end("int declaration_only();") is None


def test_function_end_of_a_declaration_does_not_run_into_the_next_body():
    # RAJA's AsIntegerArray: the defaulted constructor ends on its own line,
    # not at the end of array_size().
    assert _end("""
          AsIntegerArray() = default;

          RAJA_HOST_DEVICE constexpr size_t array_size() const
          {
            return num_integer_type;
          }
    """) == 1
    assert _end("Box(const Box&) = delete;\nvoid g() {}") == 1
    # An implicit member's line can be the class's forward declaration.
    assert _end("class ReduceSum;\nclass ReduceMin { };") is None


# Against the real compiler


def _clang():
    for path in (os.environ.get("FINDINGMNEMO_TEST_CLANG"),
                 os.path.join(os.environ.get("ROCM_PATH", "/opt/rocm"), "llvm", "bin", "clang++")):
        if path and os.path.isfile(path):
            return path
    return None


CLANG = _clang()
needs_clang = pytest.mark.skipif(CLANG is None, reason="no ROCm clang (set ROCM_PATH)")


def _compile(directory, file, *flags, archs=("gfx942",)):
    """Compile ``file`` for the device to textual IR the way a build with
    -grecord-command-line would, and return each architecture's module."""
    cmd = [CLANG, "-x", "hip", *(f"--offload-arch={a}" for a in archs), "--offload-device-only",
           "-O1", "-g", "-grecord-command-line", "-S", "-emit-llvm", *flags, file]
    if len(archs) == 1:
        cmd += ["-o", "out.ll"]
    subprocess.run(cmd, cwd=directory, check=True, capture_output=True)
    stem = os.path.splitext(os.path.basename(file))[0]
    names = ["out.ll"] if len(archs) == 1 else [f"{stem}-hip-amdgcn-amd-amdhsa-{a}.ll" for a in archs]
    return [open(os.path.join(directory, n)).read() for n in names]


def _views(module, files=None):
    unit, = compile_units(module)
    return unit, preprocess(unit, set(files or [unit.file]))


def _assert_agrees_with_ir(module, view):
    """Every line the IR attributes code to was compiled."""
    for fn in ir.parse_module(module).values():
        for block in fn.blocks:
            for file, line in block.lines:
                if os.path.normpath(file) == view.path:
                    assert view.contradiction([line]) is None, (fn.name, line)


TOY = _src("""
    #include <hip/hip_runtime.h>
    #define SQUARE(x) ((x) * (x))
    #define SCALE 2.0
    #define NOTHING(x)

    #ifdef USE_FAST
    __device__ double transform(double a) { return a * SCALE; }
    #else
    __device__ double transform(double a) { return SQUARE(a) + SCALE; }
    #endif

    __device__ double helper(double a) {
    #if defined(__HIP_DEVICE_COMPILE__)
      NOTHING(a)
      return transform(a);
    #else
      return 0.0;
    #endif
    }

    __global__ void kernel(double *p, int n) {
      int i = blockIdx.x * blockDim.x + threadIdx.x;
    #if 0
      // Nine lines the preprocessor drops with a line marker, not blank lines.
      p[i] = 1;
      p[i] = 2;
      p[i] = 3;
      p[i] = 4;
      p[i] = 5;
      p[i] = 6;
      p[i] = 7;
    #endif
    #pragma unroll
      for (int j = 0; j < 4; ++j)
        if (i < n)
          p[i] = helper(SQUARE(p[i]
                               + 1.0));
    }
""")


@needs_clang
def test_device_view_of_a_recorded_compile(tmp_path):
    (tmp_path / "toy.hip").write_text(TOY)
    module, = _compile(tmp_path, "toy.hip", "-DUSE_FAST")
    unit, views = _views(module)
    assert unit.arch == "gfx942"
    view = views[str(tmp_path / "toy.hip")]
    _assert_agrees_with_ir(module, view)
    lines = TOY.splitlines()

    def line(text):
        return lines.index(text) + 1

    # -DUSE_FAST from the recorded command chose the first transform.
    assert view.compiled(line("__device__ double transform(double a) { return a * SCALE; }"))
    assert not view.compiled(line("__device__ double transform(double a) { return SQUARE(a) + SCALE; }"))

    start = line("__device__ double helper(double a) {")
    end = view.function_end(start)
    assert end == start + 7
    assert view.text(start, end).split("\n") == [
        "__device__ double helper(double a) {", "", "  NOTHING(a)", "  return transform(a);",
        "", "", "", "}", ""]

    start = line("__global__ void kernel(double *p, int n) {")
    end = view.function_end(start)
    assert lines[end - 1] == "}" and end == len(lines)
    assert not any(view.compiled(n) for n in range(line("#if 0"), line("#endif", ) + 1)
                   if n > start)
    assert view.compiled(line("#pragma unroll"))
    # The macro call stays as written, on its two lines.
    assert "p[i] = helper(SQUARE(p[i]\n                           + 1.0));\n" in view.text(start, end)


HEADER = _src("""
    #pragma once
    template <typename T>
    __device__ T twice(T x) {
    #ifdef SMALL
      return x;
    #else
      return x + x;
    #endif
    }
""")

MAIN = _src("""
    #include <hip/hip_runtime.h>
    #include "twice.h"
    #define OPEN {
    #define CLOSE }
    __device__ int arch_value() OPEN
    #if defined(__gfx90a__)
      return 90;
    #elif defined(__gfx942__)
      return 942;
    #endif
    CLOSE
    __global__ void k(int *p) { p[0] = twice(p[0]) + arch_value(); }
""")


@needs_clang
def test_device_view_per_architecture_with_headers_and_spaces(tmp_path):
    src = tmp_path / "src dir"
    inc = tmp_path / "inc dir"
    src.mkdir()
    inc.mkdir()
    (inc / "twice.h").write_text(HEADER)
    (src / "main.hip").write_text(MAIN)
    modules = _compile(src, "main.hip", f"-I{inc}", "-MD", "-MF", "deps.d", "-Werror",
                       archs=("gfx90a", "gfx942"))
    (src / "deps.d").unlink()
    header = os.path.normpath(str(inc / "twice.h"))
    lines = MAIN.splitlines()
    for module, arch, kept, dropped in ((modules[0], "gfx90a", "  return 90;", "  return 942;"),
                                        (modules[1], "gfx942", "  return 942;", "  return 90;")):
        unit, views = _views(module, [str(src / "main.hip"), header])
        assert unit.arch == arch
        view = views[str(src / "main.hip")]
        _assert_agrees_with_ir(module, view)
        assert view.compiled(lines.index(kept) + 1)
        assert not view.compiled(lines.index(dropped) + 1)
        # Braces from OPEN and CLOSE count.
        assert view.function_end(lines.index("__device__ int arch_value() OPEN") + 1) \
            == lines.index("CLOSE") + 1
        # The template in the header, found through an -I with a space in it,
        # gets a view too.
        hview = views[header]
        assert hview.kept[3:8] == [False, False, False, True, False]
        assert hview.function_end(3) == 9
    # Preprocessing again did not write a dependency file.
    assert not (src / "deps.d").exists()


@needs_clang
def test_missing_compiler_or_compile_directory_fails(tmp_path):
    (tmp_path / "toy.hip").write_text(TOY)
    module, = _compile(tmp_path, "toy.hip")
    unit, = compile_units(module)
    compiler = str(tmp_path / "no-such-clang")
    unit.argv[0] = compiler
    with pytest.raises(PreprocessError, match=f"^could not run {compiler} to preprocess "):
        preprocess(unit, {unit.file})
    unit.directory = str(tmp_path / "gone")
    with pytest.raises(PreprocessError, match="compile directory .* is gone"):
        preprocess(unit, {unit.file})


def test_function_end_of_a_lambda_with_a_trailing_return_type():
    assert _end("""
        forall(0, n,
               [=] __device__ (int i) -> double {
                 return b[i] * 2;
               });
    """, start=2) == 4


LAMBDAS = _src("""
    #include <hip/hip_runtime.h>
    #define DEFINE_ADD(T) __device__ T add_##T(T a, T b) { return a + b; }
    DEFINE_ADD(int)

    template <typename Body>
    __global__ void forall(int n, Body body) {
      int i = blockIdx.x * blockDim.x + threadIdx.x;
      if (i < n) body(i);
    }

    void run(int *a, double *b, int n) {
      forall<<<1, 64>>>(n, [=] __device__ (int i) {
    #ifdef BUMP
        a[i] = add_int(a[i], 2);
    #else
        a[i] = add_int(a[i], 1);
    #endif
      });
      forall<<<1, 64>>>(n,
          [=] __device__ (int i) -> double {
            return b[i] = b[i] * 2;
          });
    }
""")


@needs_clang
def test_device_view_of_lambdas_and_macro_made_functions(tmp_path):
    (tmp_path / "lambdas.hip").write_text(LAMBDAS)
    module, = _compile(tmp_path, "lambdas.hip", "-O0")
    unit, views = _views(module)
    view = views[unit.file]
    _assert_agrees_with_ir(module, view)
    lines = LAMBDAS.splitlines()
    ends = {}
    for fn in ir.parse_module(module).values():
        if os.path.normpath(fn.file or "") != unit.file or not fn.line:
            continue
        last = max(ln for b in fn.blocks for f, ln in b.lines if os.path.normpath(f) == unit.file)
        ends[fn.display_name, fn.line] = view.function_end(fn.line, last)
    first = lines.index("  forall<<<1, 64>>>(n, [=] __device__ (int i) {") + 1
    second = lines.index("      [=] __device__ (int i) -> double {") + 1
    assert ends[("operator()", first)] == lines.index("  });") + 1
    assert ends[("operator()", second)] == lines.index("      });") + 1
    # The whole function comes from DEFINE_ADD on one line.
    assert ends[("add_int", 3)] == 3
    assert not view.compiled(lines.index("    a[i] = add_int(a[i], 2);") + 1)
    template = lines.index("__global__ void forall(int n, Body body) {") + 1
    assert any(ends[k] == template + 3 for k in ends if k[1] == template)


@needs_clang
def test_files_with_line_directives_fail(tmp_path):
    (tmp_path / "gen.hip").write_text(_src("""
        #include <hip/hip_runtime.h>
        #line 200 "grammar.y"
        __global__ void k(int *p) { p[0] = 1; }
    """))
    module, = _compile(tmp_path, "gen.hip")
    unit, = compile_units(module)
    with pytest.raises(PreprocessError, match="has #line directives"):
        preprocess(unit, {unit.file})


@pytest.mark.skipif(CLANG is None or shutil.which("mneme") is None, reason="needs clang and mneme")
def test_device_view_with_mnemes_compile_flags(tmp_path):
    flags = subprocess.run(["mneme", "config", "cflags"], capture_output=True, text=True,
                           check=True).stdout.split()
    (tmp_path / "toy.hip").write_text(TOY)
    module, = _compile(tmp_path, "toy.hip", "-DUSE_FAST", *flags)
    unit, = compile_units(module)
    assert any(a.startswith("-fpass-plugin=") for a in unit.argv)
    _assert_agrees_with_ir(module, preprocess(unit, {unit.file})[unit.file])


@needs_clang
def test_export_writes_the_device_view(tmp_path):
    (tmp_path / "toy.hip").write_text(TOY)
    module, = _compile(tmp_path, "toy.hip", "-DUSE_FAST", "-O0")
    unit, views = _views(module)
    prog = _Program.__new__(_Program)
    prog.unit_views = {unit.key: views}
    helper = next(f for f in ir.parse_module(module).values() if f.display_name == "helper")
    fn = _Function("device", helper.name, "helper(double)", "helper", unit.file, helper.line)
    fn.ir_fn, fn.unit = helper, unit
    source, info = _function_source(prog, fn)
    assert info == {"source_arch": "gfx942"}
    assert fn.end_line == helper.line + 7
    assert source.split("\n") == ["__device__ double helper(double a) {", "", "  NOTHING(a)",
                                  "  return transform(a);", "", "", "", "}", ""]


@needs_clang
def test_compiler_generated_functions_have_no_source(tmp_path):
    (tmp_path / "copy.hip").write_text(_src("""
        #include <hip/hip_runtime.h>
        struct Inner {
          int v;
          __device__ Inner(const Inner &o) : v(o.v + 1) {}
          __device__ Inner(int x) : v(x) {}
        };
        struct hip_pol {};
        // As RAJA declares its reducers. The debug info puts the copy
        // constructor of the specialization on the primary template.
        template <typename P, typename T> class ReduceSum;
        template <typename T> class ReduceSum<hip_pol, T> {
        public:
          Inner in;
          __device__ ReduceSum(int x) : in(x) {}
        };
        template <typename T> struct Holder {
          Inner in;
        };
        __device__ int use(ReduceSum<hip_pol, int> r, Holder<int> h) { return r.in.v + h.in.v; }
        __global__ void k(int *p) {
          ReduceSum<hip_pol, int> r(p[0]);
          Holder<int> h{Inner(p[0])};
          p[0] = use(r, h);
        }
    """))
    module, = _compile(tmp_path, "copy.hip", "-O0")
    unit, = compile_units(module)
    prog = _program_with_views(module, [unit])
    functions = {fn.name: fn for fn in prog.functions.values()}
    copies = ["_ZN9ReduceSumI7hip_poliEC2ERKS1_", "_ZN6HolderIiEC2ERKS0_"]
    assert sorted(name for name, fn in functions.items() if fn.ir_fn.artificial) == sorted(copies)
    for name in copies:
        assert _function_source(prog, functions[name]) == (None, {"compiler_generated": True})
        assert functions[name].end_line is None
    assert _function_source(prog, functions["_ZN9ReduceSumI7hip_poliEC2Ei"])[0] == \
        "  __device__ ReduceSum(int x) : in(x) {}\n"


@needs_clang
def test_preprocessing_again_writes_nothing_into_the_build(tmp_path):
    (tmp_path / "toy.hip").write_text(TOY)
    (tmp_path / "lib dir").mkdir()
    module, = _compile(tmp_path, "toy.hip", "-DUSE_FAST", "-MD", "-ftime-trace",
                       "-Wl,--as-needed", "-L", str(tmp_path / "lib dir"), "-Xlinker", "-M",
                       "-lm")
    unit, = compile_units(module)
    # Compiling with -save-temps checksums the temporary preprocessed file
    # instead of toy.hip, so it is only added to the recorded command here.
    unit.argv.insert(1, "-save-temps")
    before = {p: p.stat().st_mtime_ns for p in tmp_path.rglob("*")}
    _assert_agrees_with_ir(module, preprocess(unit, {unit.file})[unit.file])
    assert {p: p.stat().st_mtime_ns for p in tmp_path.rglob("*")} == before


@needs_clang
def test_a_command_with_two_inputs_fails_plainly(tmp_path):
    (tmp_path / "toy.hip").write_text(TOY)
    (tmp_path / "other.hip").write_text("__device__ int other() { return 7; }\n")
    module, = _compile(tmp_path, "toy.hip")
    unit, = compile_units(module)
    unit.argv.append("other.hip")
    with pytest.raises(PreprocessError, match="cannot specify -o when generating multiple "
                                              "output files"):
        preprocess(unit, {unit.file})


def _program_with_views(module, units):
    """A program with the module's functions, each in its compile unit, after
    building its views."""
    by_id = {unit.id: unit for unit in units}
    prog = _Program.__new__(_Program)
    prog.unit_views = {}
    prog.functions = {}
    for f in ir.parse_module(module).values():
        fn = _Function("device", f.name, f.display_name, f.display_name,
                       f.file and os.path.normpath(f.file), f.line)
        fn.ir_fn, fn.unit = f, by_id.get(f.unit_id)
        prog.functions[("device", f.name)] = fn
    prog.build_views()
    return prog


@needs_clang
def test_export_fails_on_a_view_that_contradicts_the_ir(tmp_path, capsys):
    (tmp_path / "toy.hip").write_text(TOY)
    module, = _compile(tmp_path, "toy.hip", "-DUSE_FAST", "-O0")
    unit, = compile_units(module)
    assert unit.file in _program_with_views(module, [unit]).unit_views[unit.key]
    assert capsys.readouterr().err == ""
    # As if the build had defined USE_FAST some way the command does not
    # record, e.g. through an environment variable. The driver records
    # -DUSE_FAST as two arguments.
    i = unit.argv.index("USE_FAST")
    assert unit.argv[i - 1] == "-D"
    del unit.argv[i - 1:i + 1]
    with pytest.raises(SystemExit) as exc:
        _program_with_views(module, [unit])
    fast = TOY.splitlines().index("__device__ double transform(double a) { return a * SCALE; }")
    assert f"puts code of transform on line {fast + 1}," in str(exc.value)


@needs_clang
def test_each_function_gets_the_view_of_the_compile_it_came_from(tmp_path):
    # A HIP -fgpu-rdc build links the device code of several files into a
    # kernel's module, which then has a compile unit for each file. Here the
    # two files compile different code of the header they share.
    (tmp_path / "common.h").write_text(_src("""
        #ifdef MODE_A
        __device__ int fa(int x) { return x + 3; }
        #else
        __device__ int fb(int x) { return x - 3; }
        #endif
    """))
    for name, call in (("a", "fa"), ("b", "fb")):
        (tmp_path / f"{name}.hip").write_text(
            f'#include <hip/hip_runtime.h>\n#include "common.h"\n'
            f"__global__ void k{name}(int *p) {{ p[0] = {call}(p[0]); }}\n")
    (tmp_path / "a.ll").write_text(_compile(tmp_path, "a.hip", "-fgpu-rdc", "-O0", "-DMODE_A")[0])
    (tmp_path / "b.ll").write_text(_compile(tmp_path, "b.hip", "-fgpu-rdc", "-O0")[0])
    module = subprocess.run([os.path.join(os.path.dirname(CLANG), "llvm-link"), "-S", "a.ll",
                             "b.ll"], cwd=tmp_path, capture_output=True, text=True,
                            check=True).stdout
    units = compile_units(module)
    assert sorted(os.path.basename(unit.file) for unit in units) == ["a.hip", "b.hip"]
    prog = _program_with_views(module, units)
    functions = {fn.display_name: fn for fn in prog.functions.values()}
    assert functions["fa"].unit.file == str(tmp_path / "a.hip")
    assert functions["fb"].unit.file == str(tmp_path / "b.hip")
    assert _function_source(prog, functions["fa"])[0] == \
        "__device__ int fa(int x) { return x + 3; }\n"
    assert _function_source(prog, functions["fb"])[0] == \
        "__device__ int fb(int x) { return x - 3; }\n"


@needs_clang
def test_export_fails_when_a_source_changed_since_the_build(tmp_path):
    (tmp_path / "toy.hip").write_text(TOY)
    module, = _compile(tmp_path, "toy.hip", "-DUSE_FAST")
    (tmp_path / "toy.hip").write_text(TOY.replace("SCALE; }", "SCALE + 1; }"))
    unit, = compile_units(module)
    with pytest.raises(SystemExit) as exc:
        _program_with_views(module, [unit])
    assert str(exc.value) == f"findingmnemo export: {unit.file} changed since it was compiled"


@needs_clang
def test_export_fails_for_a_function_without_a_device_view(tmp_path):
    (tmp_path / "toy.hip").write_text(TOY)
    module, = _compile(tmp_path, "toy.hip", "-DUSE_FAST", "-O0")
    unit, = compile_units(module)
    prog = _program_with_views(module, [unit])
    helper = next(fn for fn in prog.functions.values() if fn.display_name == "helper")

    def fails(message, **changes):
        fn = _Function(**{**helper.__dict__, **changes})
        with pytest.raises(SystemExit) as exc:
            _function_source(prog, fn)
        assert str(exc.value) == f"findingmnemo export: {message}"

    fails("the debug info has no source location for helper", line=None)
    fails("the debug info of helper has no compile command; build with -grecord-command-line",
          unit=None)
    fails(f"{tmp_path}/other.hip, the file of helper, is not part of its recorded device compile",
          file=str(tmp_path / "other.hip"))
    last = len(TOY.splitlines())
    fails(f"cannot find the closing brace of helper, which starts on line {last} of {unit.file}",
          line=last)
