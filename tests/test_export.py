from findingmnemo.export import _body, _short_name
from findingmnemo.ir import BasicBlock, Function, Loop


class _NoFunctions:
    functions = {}


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
    assert _short_name("main") == "main"
