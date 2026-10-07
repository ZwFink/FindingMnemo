import os
import shutil
import subprocess
import textwrap

import pytest

from findingmnemo import ir
from findingmnemo.export import _Function, _function_source, _Program
from findingmnemo.preprocess import (CompileUnit, build_view, compile_units, function_end,
                                     parse_output, preprocess, preprocess_argv, split_command)


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


TAIL = ["--no-offload-arch=all", "--offload-arch=gfx942", "-E", "-C", "-dD",
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
        # An option the code knows nothing about keeps its value.
        "-unknown-separate", "value", "-Wl,--as-needed", "-lm", "other.o",
        "-x", "hip", "k.hip", "-x", "none", "lib.a",
    ]
    removed = [
        # Dependency files and lists, and output that is not the source.
        "-MD", "-MF", "k.d", "-MT", "k.o", "-MQk.o", "-MJcdb.json", "-M", "-MM", "-MMD", "-MP",
        "-P", "-CC", "-dM", "-###",
        # Proteus and other plugins and LLVM options.
        "-fpass-plugin=/p/libProteusPass.so", "-fplugin=/p/libProteusPass.so",
        "-Xclang", "-mllvm", "-Xclang", "-force-proteus-jit-annotate-all",
        "-Xclang", "-load", "-Xclang", "x.so", "-mllvm", "-some-option", "-mllvm=-other",
        # Recorded for the device compile; the host compile rejects it.
        "-mcpu=gfx942",
    ]
    argv = preprocess_argv(_unit(["/rocm/clang-19", *kept[:20], *removed, *kept[20:]]))
    assert argv == ["/rocm/clang-19", *kept, *TAIL]


def test_preprocess_argv_uses_a_copy_and_another_compiler():
    argv = preprocess_argv(_unit(["clang", "-x", "hip", "./k.hip", "-c"]), source="/copy/k.hip",
                           compiler="/llvm/bin/clang")
    # The copy takes the main file's place, after its -x. Quoted includes
    # still find the original directory's headers.
    assert argv == ["/llvm/bin/clang", "-x", "hip", "/copy/k.hip", "-c", *TAIL,
                    "-iquote", "/src"]


def test_preprocess_argv_adds_a_main_file_the_command_does_not_name():
    assert preprocess_argv(_unit(["clang", "@args.rsp"])) == ["clang", "@args.rsp", *TAIL,
                                                               "/src/k.hip"]


# Preprocessed output


OUTPUT = _src("""
    # 1 "k.hip"
    # 1 "<built-in>" 1
    #define __clang__ 1
    # 1 "<command line>" 1
    #define FAST 1
    # 1 "<built-in>" 2
    # 1 "/rocm/include/hip.h" 1 3
    #define __device__ __attribute__((device))
    # 2 "k.hip" 2
    # 1 "./inc/defs.h" 1
    #define SQUARE(x) ((x) * (x))
    # 3 "k.hip" 2
    __attribute__((device)) int f(int a) {

      return ((a) * (a));
    # 20 "k.hip"
    }
""")


def test_parse_output_follows_markers_and_macros():
    files, macros = parse_output(OUTPUT, "/src")
    main = files["/src/k.hip"]
    assert main.text == {3: "__attribute__((device)) int f(int a) {", 5: "  return ((a) * (a));",
                         20: "}"}
    # Lines 1 and 2 are #includes that were entered.
    assert main.evidence == {1, 2, 3, 5, 20}
    assert files["/rocm/include/hip.h"].system and not files["/src/inc/defs.h"].system
    assert macros == {"__clang__": "<built-in>", "FAST": "<command line>",
                      "__device__": "/rocm/include/hip.h", "SQUARE": "/src/inc/defs.h"}


def _view(source: str, output: str, path="/src/k.hip"):
    files, macros = parse_output(output, "/src")
    return build_view(path, source, files[path], macros, files)


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


def test_view_classifies_lines():
    view = _view(SOURCE, OUTPUT.replace('# 20 "k.hip"', '# 9 "k.hip"'))
    assert view.kinds == ["directive", "directive", "expanded", "directive", "expanded",
                          "directive", "skipped", "directive", "same"]
    assert view.text(3, 9) == _src("""
        __device__ int f(int a) {

          return SQUARE(a);



        }
    """)
    assert view.function_end(3) == 9
    # __device__ comes from a system header, so only SQUARE is listed.
    assert view.expansions(3, 9) == [{"line": 5, "macros": ["SQUARE"],
                                      "text": "return ((a) * (a));"}]


def test_view_contradicts_code_on_lines_it_does_not_compile():
    view = _view(SOURCE, OUTPUT.replace('# 20 "k.hip"', '# 9 "k.hip"'))
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
    # The comment survives -C, which shows the #else branch was taken.
    view = _view(source, _marked({1: "#define CHECK(x)", 6: "  // checked", 11: "  use(a);"}))
    assert view.kinds == ["directive", "directive", "skipped", "directive", "empty", "same",
                          "directive", "directive", "skipped", "directive", "same"]


def test_view_joins_multi_line_macro_calls_and_keeps_pragmas():
    source = _src("""
        x = MAX(a,
                b);
        #pragma unroll
        for (;;) {}
        /* a comment
        #if not a directive
        */
    """)
    view = _view(source, _marked({1: "x = ((a) > (b) ? (a) : (b));", 3: "#pragma unroll",
                                  4: "for (;;) {}", 5: "/* a comment", 6: "#if not a directive",
                                  7: "*/"}))
    assert view.kinds == ["expanded", "joined", "pragma", "same", "same", "same", "same"]


def test_view_keeps_directive_continuations_out_and_crlf_line_ends():
    source = "#define LONG(x) \\\r\n  (x)\r\nint g() {\r\n#ifdef NO\r\n  return 1;\r\n#endif\r\n  return 2;\r\n}\r\n"
    view = _view(source, _marked({1: "#define LONG(x) (x)", 3: "int g() {", 7: "  return 2;", 8: "}"}))
    assert view.kinds[:2] == ["directive", "directive"]
    assert view.text(3, 8) == "int g() {\r\n\r\n\r\n\r\n  return 2;\r\n}\r\n"


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


# Exporter fallback without a device view


def test_export_fallback_finds_the_end_past_conditional_code(tmp_path):
    copy = tmp_path / "k.hip"
    copy.write_text(_src("""
        __device__ double helper(double a) {
        #if defined(__HIP_DEVICE_COMPILE__)
          return transform(a);
        #else
          return 0.0;
        #endif
        }
    """))
    prog = _Program.__new__(_Program)
    prog.unit_views, prog.source_copies = {}, {"/src/k.hip": str(copy)}
    fn = _Function("device", "helper", "helper", None, "/src/k.hip", 1, end_line=3)
    fn.ir_fn = ir.Function("helper", "/src/k.hip", 1,
                           blocks=[ir.BasicBlock("entry", 2, [("/src/k.hip", 3)])])
    source, info = _function_source(prog, fn)
    assert fn.end_line == 7 and source == copy.read_text()
    assert info == {"source_view": "as_written"}


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


def _views(module, files=None, **kwargs):
    unit, = compile_units(module)
    result = preprocess(unit, set(files or [unit.file]), **kwargs)
    assert result.error is None
    return unit, result


def _assert_agrees_with_ir(module, view):
    """Every line the IR attributes code to was compiled."""
    for fn in ir.parse_module(module).values():
        for block in fn.blocks:
            for file, line in block.lines:
                if os.path.normpath(file) == view.path:
                    assert view.kind(line) not in ("skipped", "directive", "blank"), (fn.name, line)


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
    unit, result = _views(module)
    assert unit.arch == "gfx942" and not result.used_copy
    view = result.views[str(tmp_path / "toy.hip")]
    _assert_agrees_with_ir(module, view)
    lines = TOY.splitlines()

    def line(text):
        return lines.index(text) + 1

    # -DUSE_FAST from the recorded command chose the first transform.
    assert view.kind(line("__device__ double transform(double a) { return a * SCALE; }")) == "expanded"
    assert view.kind(line("__device__ double transform(double a) { return SQUARE(a) + SCALE; }")) == "skipped"

    start = line("__device__ double helper(double a) {")
    end = view.function_end(start)
    assert end == start + 7
    assert view.text(start, end).split("\n") == [
        "__device__ double helper(double a) {", "", "  NOTHING(a)", "  return transform(a);",
        "", "", "", "}", ""]

    start = line("__global__ void kernel(double *p, int n) {")
    end = view.function_end(start)
    assert lines[end - 1] == "}" and end == len(lines)
    assert all(view.kind(n) == "skipped" for n in range(line("#if 0") + 1, line("#endif", ) + 1)
               if n > start)
    assert view.kind(line("#pragma unroll")) == "pragma"
    call = line("      p[i] = helper(SQUARE(p[i]")
    assert (view.kind(call), view.kind(call + 1)) == ("expanded", "joined")
    assert view.expansions(start, end) == [{
        "line": call, "macros": ["SQUARE"], "text": "p[i] = helper(((p[i] + 1.0) * (p[i] + 1.0)));"}]


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
        unit, result = _views(module, [str(src / "main.hip"), header])
        assert unit.arch == arch
        view = result.views[str(src / "main.hip")]
        _assert_agrees_with_ir(module, view)
        assert view.kind(lines.index(kept) + 1) == "same"
        assert view.kind(lines.index(dropped) + 1) == "skipped"
        # Braces from OPEN and CLOSE count.
        assert view.function_end(lines.index("__device__ int arch_value() OPEN") + 1) \
            == lines.index("CLOSE") + 1
        # The template in the header, found through an -I with a space in it,
        # gets a view too.
        hview = result.views[header]
        assert hview.kinds[3:8] == ["directive", "skipped", "directive", "same", "directive"]
        assert hview.function_end(3) == 9
    # Preprocessing again did not write a dependency file.
    assert not (src / "deps.d").exists()


@needs_clang
def test_changed_source_uses_mnemes_copy_or_gives_up(tmp_path):
    (tmp_path / "toy.hip").write_text(TOY)
    module, = _compile(tmp_path, "toy.hip", "-DUSE_FAST")
    copy_dir = tmp_path / "copy"
    copy_dir.mkdir()
    shutil.copy(tmp_path / "toy.hip", copy_dir / "toy.hip")
    (tmp_path / "toy.hip").write_text(TOY.replace("SCALE; }", "SCALE + 1; }"))
    unit, = compile_units(module)
    assert preprocess(unit, {unit.file}).error.endswith("changed since it was compiled")
    result = preprocess(unit, {unit.file}, copies={unit.file: str(copy_dir / "toy.hip")})
    assert result.error is None and result.used_copy
    view = result.views[unit.file]
    _assert_agrees_with_ir(module, view)
    assert view.lines == TOY.splitlines(keepends=True)


@needs_clang
def test_missing_compiler_falls_back_or_reports(tmp_path):
    (tmp_path / "toy.hip").write_text(TOY)
    module, = _compile(tmp_path, "toy.hip")
    unit, = compile_units(module)
    unit.argv[0] = str(tmp_path / "no-such-clang")
    assert preprocess(unit, {unit.file}).error.startswith("could not run")
    result = preprocess(unit, {unit.file}, fallback_compiler=CLANG)
    assert result.error is None and result.compiler == CLANG
    # Without -DUSE_FAST this time.
    lines = TOY.splitlines()
    view = result.views[unit.file]
    assert view.kind(lines.index("__device__ double transform(double a) { return a * SCALE; }") + 1) \
        == "skipped"


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
    unit, result = _views(module)
    view = result.views[unit.file]
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
    assert view.expansions(3, 3)[0]["macros"] == ["DEFINE_ADD"]
    assert view.kind(lines.index("    a[i] = add_int(a[i], 2);") + 1) == "skipped"
    template = lines.index("__global__ void forall(int n, Body body) {") + 1
    assert any(ends[k] == template + 3 for k in ends if k[1] == template)


@needs_clang
def test_files_with_line_directives_get_no_view(tmp_path):
    (tmp_path / "gen.hip").write_text(_src("""
        #include <hip/hip_runtime.h>
        #line 200 "grammar.y"
        __global__ void k(int *p) { p[0] = 1; }
    """))
    module, = _compile(tmp_path, "gen.hip")
    unit, = compile_units(module)
    assert preprocess(unit, {unit.file}).views == {}


@pytest.mark.skipif(CLANG is None or shutil.which("mneme") is None, reason="needs clang and mneme")
def test_device_view_with_mnemes_compile_flags(tmp_path):
    flags = subprocess.run(["mneme", "config", "cflags"], capture_output=True, text=True,
                           check=True).stdout.split()
    (tmp_path / "toy.hip").write_text(TOY)
    module, = _compile(tmp_path, "toy.hip", "-DUSE_FAST", *flags)
    unit, = compile_units(module)
    assert any(a.startswith("-fpass-plugin=") for a in unit.argv)
    result = preprocess(unit, {unit.file})
    assert result.error is None
    _assert_agrees_with_ir(module, result.views[unit.file])


@needs_clang
def test_export_writes_the_device_view(tmp_path):
    (tmp_path / "toy.hip").write_text(TOY)
    module, = _compile(tmp_path, "toy.hip", "-DUSE_FAST", "-O0")
    unit, result = _views(module)
    prog = _Program.__new__(_Program)
    prog.unit_views, prog.source_copies = {unit.key: result}, {}
    helper = next(f for f in ir.parse_module(module).values() if f.display_name == "helper")
    fn = _Function("device", helper.name, "helper(double)", "helper", unit.file, helper.line)
    fn.ir_fn, fn.units = helper, [unit]
    source, info = _function_source(prog, fn)
    assert info == {"source_view": "device", "source_arch": "gfx942"}
    assert fn.end_line == helper.line + 7
    assert source.split("\n") == ["__device__ double helper(double a) {", "", "  NOTHING(a)",
                                  "  return transform(a);", "", "", "", "}", ""]


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
    result = preprocess(unit, {unit.file})
    assert result.error is None
    _assert_agrees_with_ir(module, result.views[unit.file])
    assert {p: p.stat().st_mtime_ns for p in tmp_path.rglob("*")} == before


@needs_clang
def test_a_command_with_two_inputs_fails_plainly(tmp_path):
    (tmp_path / "toy.hip").write_text(TOY)
    (tmp_path / "other.hip").write_text("__device__ int other() { return 7; }\n")
    module, = _compile(tmp_path, "toy.hip")
    unit, = compile_units(module)
    unit.argv.append("other.hip")
    assert "cannot specify -o when generating multiple output files" in \
        preprocess(unit, {unit.file}).error


def _program_with_views(module, unit):
    """A program with the module's functions, after building its views."""
    functions = ir.parse_module(module)
    prog = _Program.__new__(_Program)
    prog.unit_views, prog.source_copies, prog.llvm_bin = {}, {}, os.path.dirname(CLANG)
    prog.unit_functions = {unit.key: functions}
    prog.functions = {}
    for f in functions.values():
        fn = _Function("device", f.name, f.display_name, f.display_name, unit.file, f.line)
        fn.ir_fn, fn.units = f, [unit]
        prog.functions[("device", f.name)] = fn
    prog.build_views()
    return prog


@needs_clang
def test_export_drops_a_view_that_contradicts_the_ir(tmp_path, capsys):
    (tmp_path / "toy.hip").write_text(TOY)
    module, = _compile(tmp_path, "toy.hip", "-DUSE_FAST", "-O0")
    unit, = compile_units(module)
    assert unit.file in _program_with_views(module, unit).unit_views[unit.key].views
    assert capsys.readouterr().err == ""
    # As if the build had defined USE_FAST some way the command does not
    # record, e.g. through an environment variable. The driver records
    # -DUSE_FAST as two arguments.
    i = unit.argv.index("USE_FAST")
    assert unit.argv[i - 1] == "-D"
    del unit.argv[i - 1:i + 1]
    prog = _program_with_views(module, unit)
    assert prog.unit_views[unit.key].views == {}
    fast = TOY.splitlines().index("__device__ double transform(double a) { return a * SCALE; }")
    assert f"puts code of transform on line {fast + 1}," in capsys.readouterr().err
    helper = next(fn for fn in prog.functions.values() if fn.display_name == "helper")
    assert _function_source(prog, helper)[1] == {}
