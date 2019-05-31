from typing import Optional

import pytest
from itertools import zip_longest

from libcube.orientation import Side
from libcube.actions import Rotate, Turn, TurningType
from libcube.postprocessing import OptimizingPreprocessor
from libcube.parser import parse_actions


@pytest.mark.parametrize("side1, double1, side2, double2, res, res_double", [
    (Side.LEFT, False, Side.RIGHT, False, None, None),
    (Side.RIGHT, True, Side.LEFT, True, None, None),
    (Side.TOP, True, Side.BOTTOM, False, Side.TOP, False),
    (Side.BOTTOM, False, Side.TOP, True, Side.TOP, False),

    (Side.LEFT, False, Side.LEFT, False, Side.LEFT, True),
    (Side.RIGHT, True, Side.RIGHT, True, None, None),
    (Side.TOP, False, Side.TOP, True, Side.BOTTOM, False),
    (Side.FRONT, True, Side.FRONT, False, Side.BACK, False)
])
def test_rotations(side1, double1, side2, double2, res, res_double):
    a1 = Rotate(side1, double1)
    a2 = Rotate(side2, double2)
    actual = []

    pp = OptimizingPreprocessor()
    pp.callback = actual.append
    pp.process(a1)
    pp.process(a2)
    pp.done()

    if res is None:
        assert len(actual) == 0
    else:
        assert len(actual) == 1
        actual = actual[0]
        assert isinstance(actual, Rotate)
        assert actual.axis_side == res
        assert actual.twice == res_double


@pytest.mark.parametrize("a1, a2", [
    (Rotate(Side.LEFT, True), Rotate(Side.TOP, False)),
    (Rotate(Side.LEFT, True), Turn(Side.TOP, 1)),
    (Turn(TurningType.HORIZONTAL, [1], 1), Turn(TurningType.VERTICAL, [1], 1)),
    (Turn(TurningType.HORIZONTAL, [1], 1), Turn(TurningType.HORIZONTAL, [2], 1))
])
def test_rotations_do_nothing(a1, a2):
    actual = []
    pp = OptimizingPreprocessor()
    pp.callback = actual.append
    pp.process(a1)
    pp.process(a2)
    pp.done()

    for x, y in zip_longest(actual, [a1, a2]):
        assert repr(x) == repr(y)


@pytest.mark.parametrize("type, amount1, amount2, exp_amount", [
    (TurningType.HORIZONTAL, 1, 1, 2),
    (TurningType.VERTICAL,   1, 2, 3),
    (TurningType.SLICE,      1, 3, None),
    (TurningType.HORIZONTAL, 2, 1, 3),
    (TurningType.VERTICAL,   2, 2, None),
    (TurningType.SLICE,      2, 3, 1),
    (TurningType.HORIZONTAL, 3, 1, None),
    (TurningType.VERTICAL,   3, 2, 1),
    (TurningType.SLICE,      3, 3, 2),
])
def test_turning(type: TurningType, amount1: int, amount2: int, exp_amount: Optional[int]):
    a1 = Turn(type, [1], amount1)
    a2 = Turn(type, [1], amount2)
    actual = []

    pp = OptimizingPreprocessor()
    pp.callback = actual.append
    pp.process(a1)
    pp.process(a2)
    pp.done()

    if exp_amount is None:
        assert len(actual) == 0
    else:
        assert len(actual) == 1
        actual = actual[0]
        assert isinstance(actual, Turn)
        assert actual.type == type
        assert actual.turns == exp_amount
        assert actual.sides == [1]


@pytest.mark.parametrize("actions, expected", [
    ("FRUU'R'F'", ""),
    ("FLRUU'R'F'", "FLF'"),
    ("XYY'ZZ'R", "XR")
])
def test_multiple(actions, expected):
    a = parse_actions(actions)
    b = parse_actions(expected)
    actual = []

    pp = OptimizingPreprocessor()
    pp.callback = actual.append
    for x in a:
        pp.process(x)
    pp.done()

    assert all(repr(x) == repr(y) for x, y in zip_longest(actual, b))
