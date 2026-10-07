from findingmnemo.isa import KernelCode, bundles, choose

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
