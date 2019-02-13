from libcube.orientation import Side, Orientation
from libcube.actions import Rotate

import pytest


@pytest.mark.parametrize("around, front, top", [
    (Side.FRONT, Side.FRONT, Side.RIGHT),
    (Side.BACK, Side.FRONT, Side.LEFT),
    (Side.RIGHT, Side.BOTTOM, Side.FRONT),
    (Side.LEFT, Side.TOP, Side.BACK),
    (Side.TOP, Side.RIGHT, Side.TOP),
    (Side.BOTTOM, Side.LEFT, Side.TOP)
])
def test_rotations(around: Side, front: Side, top: Side):
    orientation = Orientation(Side.FRONT, Side.TOP)
    action = Rotate(around)
    # noinspection PyTypeChecker
    orientation = action.perform(None, orientation)

    assert orientation.front == front
    assert orientation.top == top
