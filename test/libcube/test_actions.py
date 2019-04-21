from libcube.cube import Cube
from libcube.orientation import Side, Orientation
from libcube.actions import Rotate, Turn

import pytest
from typing import List
from unittest.mock import MagicMock


@pytest.mark.parametrize("around, front, top, twice", [
    (Side.FRONT, Side.FRONT, Side.RIGHT, False),
    (Side.BACK, Side.FRONT, Side.LEFT, False),
    (Side.RIGHT, Side.BOTTOM, Side.FRONT, False),
    (Side.LEFT, Side.TOP, Side.BACK, False),
    (Side.TOP, Side.RIGHT, Side.TOP, False),
    (Side.BOTTOM, Side.LEFT, Side.TOP, False),

    (Side.FRONT, Side.FRONT, Side.BOTTOM, True),
    (Side.LEFT, Side.BACK, Side.BOTTOM, True)
])
def test_rotations(around: Side, front: Side, top: Side, twice: bool) -> None:
    orientation = Orientation(Side.FRONT, Side.TOP)
    action = Rotate(around, twice)
    # noinspection PyTypeChecker
    orientation = action.perform(None, orientation)

    assert orientation.front == front
    assert orientation.top == top

class Object(object):
    pass


@pytest.mark.parametrize("side, func, out_sides, out_amount", [
    (Side.FRONT, "rotate_slice", [1, 2], 1),
    (Side.BACK, "rotate_slice", [-1, -2], 3),
    (Side.RIGHT, "rotate_vertical", [-1, -2], 1),
    (Side.LEFT, "rotate_vertical", [1, 2], 3),
    (Side.TOP, "rotate_horizontal", [1, 2], 3),
    (Side.BOTTOM, "rotate_horizontal", [-1, -2], 1)
])
def test_turning_vertical(side: Side, func: str, out_sides: List[int], out_amount: int) -> None:
    cube: Cube = Object()
    mock = MagicMock()
    setattr(cube, func, mock)

    orientation = Orientation()
    action = Turn(side, [1, 2], 1)
    assert action.perform(cube, orientation) == orientation
    assert len(mock.call_args_list) == len(out_sides)
    print(mock.call_args_list[0])
    for args, side in zip(mock.call_args_list, out_sides):
        arg_orientation, arg_index, arg_turn = tuple(args)[0]
        assert arg_orientation == orientation
        assert arg_index == side
        assert arg_turn == out_amount
