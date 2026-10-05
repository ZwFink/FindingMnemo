from findingmnemo.ir import parse_loops, parse_module

MODULE = """
define protected amdgpu_kernel void @kern(ptr %a) #0 !dbg !5 !proteus.jit !9 {
  %x = load i32, ptr %a, align 4, !dbg !7
  br label %for.cond, !dbg !7

for.cond:
  %c = call fastcc i32 @"helper.fn"(i32 %x), !dbg !8
  call void @llvm.lifetime.start.p0(i64 4, ptr %a)
  br label %for.cond, !dbg !8, !llvm.loop !10
}

define internal fastcc i32 @"helper.fn"(i32 %v) !dbg !6 {
entry:
  ret i32 %v
}

!1 = !DIFile(filename: "k.cpp", directory: "/src")
!5 = distinct !DISubprogram(name: "kern", scope: !1, file: !1, line: 10, unit: !0)
!6 = distinct !DISubprogram(name: "helper", scope: !1, file: !1, line: 3, unit: !0)
!7 = !DILocation(line: 11, column: 3, scope: !5)
!8 = !DILocation(line: 12, column: 5, scope: !5)
"""


def test_parse_module_functions_blocks_and_calls():
    functions = parse_module(MODULE)
    assert set(functions) == {"kern", "helper.fn"}

    kern = functions["kern"]
    assert (kern.file, kern.line, kern.display_name) == ("/src/k.cpp", 10, "kern")
    assert [b.label for b in kern.blocks] == ["entry", "for.cond"]
    assert [b.instructions for b in kern.blocks] == [2, 3]
    assert kern.blocks[0].lines == [("/src/k.cpp", 11)]
    # Intrinsics are not calls in the program's call graph.
    assert kern.calls == [("helper.fn", ("/src/k.cpp", 12))]

    helper = functions["helper.fn"]
    assert (helper.line, helper.display_name) == (3, "helper")
    assert helper.calls == []


def test_parse_loops_nesting():
    output = """Loop info for function 'kern':
Loop at depth 1 containing: %for.cond<header><exiting>,%for.body,%inner<latch>
    Loop at depth 2 containing: %inner<header><latch><exiting>
Loop at depth 1 containing: %while.cond<header><latch><exiting>
Loop info for function 'helper':
"""
    loops = parse_loops(output)
    assert loops["helper"] == []
    outer, inner, other = loops["kern"]
    assert (outer.depth, outer.header, outer.parent) == (1, "for.cond", None)
    assert outer.blocks == ["for.cond", "for.body", "inner"]
    assert (inner.depth, inner.header, inner.parent) == (2, "inner", 0)
    assert (other.depth, other.parent) == (1, None)
