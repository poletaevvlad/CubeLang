import pytest
from itertools import zip_longest

from libcube.orientation import Side
from libcube.actions import Rotate, Turn
from libcube.postprocessing import optimizer_postprocessor


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
    actual = list(optimizer_postprocessor([a1, a2]))
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
    (Rotate(Side.LEFT, True), Turn(Side.TOP, 1))
])
def test_rotations_do_nothing(a1, a2):
    for x, y in zip_longest(list(optimizer_postprocessor([a1, a2])), [a1, a2]):
        assert repr(x) == repr(y)
