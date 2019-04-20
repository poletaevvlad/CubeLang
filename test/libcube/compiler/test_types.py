import typing

import pytest
from libcube.compiler.types import Type, Integer, Real, Bool, List, Set, Function, Void, type_annotation_to_type, T, \
    Color, Side


@pytest.mark.parametrize("type_object, representation", [
    (Integer, "Integer"),
    (Real, "Real"),
    (Bool, "Bool"),
    (Void, "Void"),
    (List(Set(Integer)), "List(Set(Integer))"),
    (Set(Bool), "Set(Bool)"),
    (Function(([Integer, Real, List(Bool)], Void)), "Function(([Integer, Real, List(Bool)], Void))")
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
    (Function(([Integer], Real)), Function(([Integer], Real)))
])
def test_hash_simple(a: Type, b: Type):
    assert a == b
    assert hash(a) == hash(b)


@pytest.mark.parametrize("a, b, result", [
    (Real, Integer, None),
    (Integer, Integer, {}),
    (List(T), List(Integer), {"T": Integer}),
    (List(T), Set(Integer), None),
    (List(Set(T)), List(Set(List(Integer))), {"T": List(Integer)})
])
def test_generic_args(a: Type, b: Type, result):
    actual = a.get_generic_vars(b)
    assert result == actual


@pytest.mark.parametrize("args, return_type", [
    ([Integer, Integer], Integer),
    ([Integer, Real], Bool),
    ([Real, Real], Color),
    ([Bool, Real], None),
    ([Real, List(Integer)], Real),
    ([Integer, List(Integer)], Real),
    ([Real, List(Real)], None),
    ([Real, Set(Real)], None)
])
def test_function_arguments(args: typing.List[Type], return_type: Type):
    func = Function(([Integer, Integer], Integer),
                    ([Integer, Real], Bool),
                    ([Real, Real], Color),
                    ([Real, List(Integer)], Real))
    res = func.takes_arguments(args)
    assert res == return_type


@pytest.mark.parametrize("args, return_type", [
    ([Set(Integer), List(Set(Integer))], Set(Set(Integer))),
    ([Real, List(Real)], Set(Real)),
    ([Set(List(Bool))], Integer),
    ([Set(Color), List(Color)], Color),
    ([Color, List(Side)], None),
    ([Set(Side), List(Color)], None)
])
def test_function_arguments_generic(args: typing.List[Type], return_type: Type):
    func = Function(([T, List(T)], Set(T)),
                    ([Set(List(T))], Integer),
                    ([Set(T), List(T)], T))
    assert func.takes_arguments(args) == return_type


@pytest.mark.parametrize("annotation, val_type", [
    (int, Integer), (float, Real), (bool, Bool), (None, Void),
    (typing.List[int], List(Integer)),
    (typing.Set[float], Set(Real)),
    (typing.List[typing.Set[int]], List(Set(Integer)))
])
def test_from_annotation(annotation: typing.Any, val_type: Type):
    assert type_annotation_to_type(annotation) == val_type


@pytest.mark.parametrize("type, value", [
    (Integer, "0"), (Real, "0.0"), (Bool, "False"), (List(Bool), "list()"), (Set(Integer), "set()")
])
def test_default(type: Type, value: str):
    assert type.default_value() == value
