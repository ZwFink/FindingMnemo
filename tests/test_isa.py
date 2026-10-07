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
