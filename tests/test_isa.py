import os
import subprocess

import pytest

from findingmnemo.isa import KernelCode, bundles, choose, disassemble_kernels

MAGIC = b"__CLANG_OFFLOAD_BUNDLE__"


def test_bundles_splits_one_per_translation_unit():
    first = MAGIC + b"\x02" + b"a" * 20
    second = MAGIC + b"\x02" + b"b" * 7
    padding = b"\0" * 9
    assert bundles(first + padding + second) == [first + padding, second]
    assert bundles(first) == [first]
    # Not a bundle: passed on whole, as before.
    assert bundles(b"CCOB...") == [b"CCOB..."]


def _code(instructions, unit):
    isa = "".join(f"\t{i} // {n:012X}: {n}\n" for n, i in enumerate(instructions))
    return KernelCode(isa, "k", "k.hpp", 3, unit)


def test_choose_takes_identical_copies_and_tells_different_ones_apart():
    a = _code(["s_load_dword s0", "s_endpgm"], "/src/a.cpp")
    a_moved = _code(["s_load_dword s0", "s_endpgm"], "/src/b.cpp")
    a_moved.isa = a_moved.isa.replace("// 0000", "// 4000")
    b = _code(["s_load_dword s1", "s_nop 0", "s_endpgm"], "/src/c.cpp")
    assert choose([]).isa is None
    assert choose([b]) is b
    # Copies that differ only in addresses are the same code.
    assert choose([a, a_moved]) is a
    assert choose([a, b], ["/src/c.cpp"]) is b
    assert choose([a, b], ["/src/other.cpp"]) is None
    assert choose([a, b]) is None


def test_choose_ignores_where_the_code_object_put_a_call_or_variable():
    def call(lo, hi, value="0x0"):
        return _code(["s_mov_b32 s6, " + value, "s_getpc_b64 s[4:5]", "s_getpc_b64 s[8:9]",
                      f"s_add_u32 s4, s4, {lo}", f"s_addc_u32 s5, s5, {hi}",
                      "s_add_u32 s8, s8, 0x40", "s_addc_u32 s9, s9, 0",
                      "s_swappc_b64 s[30:31], s[4:5]", "s_add_u32 s4, s4, 0x10", "s_endpgm"],
                     "/src/a.cpp")
    first = call("0xfffff920", "-1")
    # The offsets from the PC to the callee and the variable differ.
    assert choose([first, call("0x120", "0")]) is first
    # A literal not added to the PC is still the code's own.
    assert choose([first, call("0xfffff920", "-1", "0x1")]) is None
    later = call("0xfffff920", "-1")
    later.isa = later.isa.replace("s4, s4, 0x10", "s4, s4, 0x20")
    assert choose([first, later]) is None


def _clang():
    for path in (os.environ.get("FINDINGMNEMO_TEST_CLANG"),
                 os.path.join(os.environ.get("ROCM_PATH", "/opt/rocm"), "llvm", "bin", "clang++")):
        if path and os.path.exists(path):
            return path
    return None


CLANG = _clang()
needs_clang = pytest.mark.skipif(CLANG is None, reason="no ROCm clang (set ROCM_PATH)")

HEADER = """
#include <hip/hip_runtime.h>
template <typename T>
static __global__ void normalize(T *x, T a, int n) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n)
    x[i] = a * x[i] / sqrt(x[i] * x[i] + a);
}
"""
PRECISE = """
#include "normalize.hpp"
void precise(float *x, int n) { normalize<<<(n + 255) / 256, 256>>>(x, 2.0f, n); }
"""
FAST = """
#include "normalize.hpp"
__global__ void only_fast(float *x) { x[threadIdx.x] = 0; }
void fast(float *x, int n) {
  normalize<<<(n + 255) / 256, 256>>>(x, 3.0f, n);
  only_fast<<<1, 64>>>(x);
}
"""
MAIN = """
void precise(float *x, int n);
void fast(float *x, int n);
int main() { precise(nullptr, 0); fast(nullptr, 0); }
"""


@needs_clang
def test_kernels_from_every_translation_unit(tmp_path):
    for name, text in [("normalize.hpp", HEADER), ("precise.cpp", PRECISE),
                       ("fast.cpp", FAST), ("main.cpp", MAIN)]:
        (tmp_path / name).write_text(text)
    objects = []
    for source, flags in [("precise.cpp", []), ("fast.cpp", ["-ffast-math"]), ("main.cpp", [])]:
        objects.append(str(tmp_path / (source + ".o")))
        subprocess.run([CLANG, "-x", "hip", "--offload-arch=gfx942", "-O3", "-g", *flags, "-c",
                        str(tmp_path / source), "-o", objects[-1]], check=True)
    exe = str(tmp_path / "app")
    subprocess.run([CLANG, "--hip-link", "--offload-arch=gfx942", *objects, "-o", exe], check=True)

    normalize, only_fast = "_ZL9normalizeIfEvPT_S0_i", "_Z9only_fastPf"
    arch, code = disassemble_kernels(exe, [normalize, only_fast], os.path.dirname(CLANG))
    assert arch == "gfx942"
    precise_cpp, fast_cpp = str(tmp_path / "precise.cpp"), str(tmp_path / "fast.cpp")
    # Only in the second translation unit's code object.
    assert [c.unit for c in code[only_fast]] == [fast_cpp]
    assert code[only_fast][0].instructions
    # Each translation unit has its own copy, and -ffast-math changes it.
    copies = code[normalize]
    assert sorted(c.unit for c in copies) == sorted([precise_cpp, fast_cpp])
    assert choose(copies) is None
    fast_copy, precise_copy = choose(copies, [fast_cpp]), choose(copies, [precise_cpp])
    assert (fast_copy.unit, precise_copy.unit) == (fast_cpp, precise_cpp)
    assert fast_copy.instructions < precise_copy.instructions


# A template with external linkage that calls a function and reads a variable,
# so its code has offsets from the PC that depend on the rest of the code object.
SCALE_HEADER = """
#include <hip/hip_runtime.h>
__constant__ static float coef[16];
__device__ __noinline__ static float twice(float v) { return 2.0f * v * coef[1]; }
template <typename T>
__global__ void scale(T *x) { x[threadIdx.x] = twice(x[threadIdx.x]); }
"""
SCALE_A = """
#include "scale.hpp"
__device__ __noinline__ float pad(float v) { return v * v + 1.0f; }
__global__ void only_a(float *x) { x[threadIdx.x] = pad(x[threadIdx.x]); }
void a(float *x) { scale<<<1, 64>>>(x); only_a<<<1, 64>>>(x); }
"""
SCALE_B = """
#include "scale.hpp"
void b(float *x) { scale<<<1, 64>>>(x); }
int main() { b(nullptr); }
"""


@needs_clang
@pytest.mark.parametrize("rdc", [False, True], ids=["per-unit", "rdc"])
def test_template_kernels_that_call_and_read_variables(tmp_path, rdc):
    for name, text in [("scale.hpp", SCALE_HEADER), ("a.cpp", SCALE_A), ("b.cpp", SCALE_B)]:
        (tmp_path / name).write_text(text)
    flags = ["-x", "hip", "--offload-arch=gfx942", "-O3", "-g"] + (["-fgpu-rdc"] if rdc else [])
    objects = []
    for source in ("a.cpp", "b.cpp"):
        objects.append(str(tmp_path / (source + ".o")))
        subprocess.run([CLANG, *flags, "-c", str(tmp_path / source), "-o", objects[-1]],
                       check=True)
    exe = str(tmp_path / "app")
    subprocess.run([CLANG, "--hip-link", "--offload-arch=gfx942", *(["-fgpu-rdc"] if rdc else []),
                    *objects, "-o", exe], check=True)

    scale = "_Z5scaleIfEvPT_"
    arch, code = disassemble_kernels(exe, [scale], os.path.dirname(CLANG))
    # A relocatable device code link has one code object, where the template
    # is a weak symbol; otherwise each translation unit has its own copy.
    assert len(code[scale]) == (1 if rdc else 2)
    chosen = choose(code[scale])
    assert chosen is not None and chosen.instructions
    assert "s_getpc_b64" in chosen.isa
    assert (os.path.basename(chosen.file), chosen.line) == ("scale.hpp", 6)
