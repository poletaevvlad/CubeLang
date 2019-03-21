import pytest
from libcube.compiler.types import Type, Integer, Real, Bool, List, Set


@pytest.mark.parametrize("type_object, representation", [
    (Integer, "Integer"),
    (Real, "Real"),
    (Bool, "Bool"),
    (List(Set(Integer)), "List(Set(Integer))"),
    (Set(Bool), "Set(Bool)")
])
def test_repr(type_object: Type, representation: str):
    assert repr(type_object) == representation


@pytest.mark.parametrize("type1, type2, result", [
    (Integer, Integer, True),
    (Integer, Real, False),
    (Real, Integer, True),
    (Bool, Bool, True),
    (Bool, Integer, False),
    (List(Integer), List(Integer), True),
    (List(Real), List(Integer), False),
    (Set(Integer), List(Integer), False)
])
def test_assignability(type1: Type, type2: Type, result: bool):
    actual = type1.is_assignable(type2)
    assert actual == result


@pytest.mark.parametrize("a, b", [
    (Integer, Integer),
    (List(Integer), List(Integer)),
    (List(Set(List(Bool))), List(Set(List(Bool))))
])
def test_hash_simple(a: Type, b: Type):
    assert hash(a) == hash(b)
