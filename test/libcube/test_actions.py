from libcube.cube import Cube
from libcube.orientation import Side, Orientation
from libcube.actions import Rotate, Turn, TurningType

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


# noinspection PyTypeChecker
@pytest.mark.parametrize("around", [x for x in Side])
def test_rotation_2(around: Side):
    action1 = Rotate(around, False)
    action2 = Rotate(around.opposite(), False)

    initial = Orientation(Side.LEFT, Side.BACK)
    orientation = action1.perform(None, initial)
    orientation = action2.perform(None, orientation)

    assert orientation == initial


def test_from_turn_steps():
    turns = [Side.RIGHT, Side.FRONT, Side.FRONT,
             Side.TOP, Side.TOP, Side.TOP,
             Side.RIGHT, Side.RIGHT, Side.RIGHT, Side.RIGHT, Side.TOP]
    actions = list(Rotate.from_turn_steps(turns))
    expected_sides = [Side.RIGHT, Side.FRONT, Side.BOTTOM, Side.TOP]
    expected_twice = [False, True, False, False, False]
    assert len(actions) == len(expected_sides)
    for action, side, twice in zip(actions, expected_sides, expected_twice):
        assert action.axis_side == side
        assert action.twice == twice


class CubeMock(object):
    def __init__(self):
        self.turn_slice = None
        self.turn_vertical = None
        self.turn_horizontal = None


@pytest.mark.parametrize("side, func, out_sides, out_amount", [
    (Side.FRONT, "turn_slice", [1, 2], 1),
    (Side.BACK, "turn_slice", [-1, -2], 3),
    (Side.RIGHT, "turn_vertical", [-1, -2], 1),
    (Side.LEFT, "turn_vertical", [1, 2], 3),
    (Side.TOP, "turn_horizontal", [1, 2], 3),
    (Side.BOTTOM, "turn_horizontal", [-1, -2], 1)
])
def test_turning_vertical(side: Side, func: str, out_sides: List[int], out_amount: int) -> None:
    cube: Cube = CubeMock()
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


@pytest.mark.parametrize("side, turn, res_side, res_sides, res_turns", [
    (Side.TOP,   Side.FRONT, TurningType.VERTICAL, 1, 3),
    (Side.RIGHT, Side.FRONT, TurningType.HORIZONTAL, 1, 3),

    (Side.RIGHT, Side.TOP, TurningType.SLICE, 1, 1),
    (Side.FRONT, Side.TOP, TurningType.VERTICAL, 1, 3),

    (Side.FRONT, Side.RIGHT, TurningType.HORIZONTAL, 1, 3),
    (Side.TOP, Side.RIGHT, TurningType.SLICE, -1, 3),
])
def test_turning_transform(side: Side, turn: Side, res_side: TurningType,
                           res_sides: int, res_turns: int):
    action = Turn(side, [1], 1)
    transformed = action._transform(turn)
    assert transformed.type == res_side
    assert transformed.turns == res_turns
    assert transformed.sides[0] == res_sides


@pytest.mark.parametrize("orientation, action, type, indices", [
    (Orientation(Side.BACK, Side.LEFT), Turn(Side.RIGHT, 1, 3), TurningType.HORIZONTAL, 1),
    (Orientation(Side.TOP, Side.BACK), Turn(Side.TOP, 1, 1), TurningType.SLICE, -1),
    (Orientation(Side.RIGHT, Side.BOTTOM), Turn(Side.FRONT, 1, 1), TurningType.VERTICAL, -1)
])
def test_orientation_changes(orientation: Side, action: Turn, type: TurningType,
                             indices: int):
    new_action = action.from_orientation(orientation)
    assert new_action.type == type
    assert new_action.sides[0] == indices
