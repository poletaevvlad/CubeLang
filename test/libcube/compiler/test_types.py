import typing

import pytest
from libcube.compiler.types import Type, Integer, Real, Bool, List, Set, Function, Void


@pytest.mark.parametrize("type_object, representation", [
    (Integer, "Integer"),
    (Real, "Real"),
    (Bool, "Bool"),
    (Void, "Void"),
    (List(Set(Integer)), "List(Set(Integer))"),
    (Set(Bool), "Set(Bool)"),
    (Function([Integer, Real, List(Bool)], Void), "Function([Integer, Real, List(Bool)], Void)")
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
    (List(Set(List(Bool))), List(Set(List(Bool)))),
    (Function([Integer], Real), Function([Integer], Real))
])
def test_hash_simple(a: Type, b: Type):
    assert a == b
    assert hash(a) == hash(b)


@pytest.mark.parametrize("real, check, result", [
    ([Integer, Real], [Integer], False),
    ([Integer, Real], [Integer, Integer], True),
    ([List(Integer), Set(List(Integer))], [List(Integer), Set(Integer)], False),
    ([List(Integer), Set(List(Integer))], [List(Integer), Set(List(Integer))], True)
])
def test_function_arguments(real: typing.List[Type], check: typing.List[Type], result: bool):
    func = Function(real, Void)
    res = func.takes_arguments(check)
    assert res == result
