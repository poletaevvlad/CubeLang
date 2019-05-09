from pytest import raises
import pytest

from libcube.parser import ParsingError, parse_actions, get_action_representation
from libcube.actions import Turn, Action, Rotate
from libcube.orientation import Side


def test_illegal_modifier():
    with raises(ParsingError) as e_data:
        list(parse_actions("2RDR'D'"))
    assert e_data.value.column == 0
    assert str(e_data.value) == "Illegal modifier '2' at 1"


def test_illegal_character():
    with raises(ParsingError) as e_data:
        list(parse_actions("RLPRL"))
    assert e_data.value.column == 2
    assert str(e_data.value) == "Unknown character 'P' at 3"


def test_valid_parsing():
    actions = list(parse_actions("R  L2  U' RU L"))
    expected_sides = [Side.RIGHT, Side.LEFT, Side.TOP, Side.RIGHT, Side.TOP, Side.LEFT]
    expected_turns = [1, 2, 1, 1, 3, 3]

    assert len(actions) == len(expected_sides)
    for action, side, turns in zip(actions, expected_sides, expected_turns):
        assert isinstance(action, Turn)
        assert action.side == side
        assert action.turns == turns


def test_rotation():
    actions = list(parse_actions("X X' Y' Z2"))
    expected_sides = [Side.RIGHT, Side.LEFT, Side.BOTTOM, Side.FRONT]
    expected_twice = [False, False, False, True]

    assert len(actions) == len(expected_sides)
    for action, side, twice in zip(actions, expected_sides, expected_twice):
        assert isinstance(action, Rotate)
        assert action.twice == twice
        assert action.axis_side == side


@pytest.mark.parametrize("action, expected", [
    (Turn(Side.FRONT, 1, 1), "F"),
    (Turn(Side.FRONT, 1, 2), "F2"),
    (Turn(Side.FRONT, 1, 3), "F'"),
    (Turn(Side.LEFT, 1, 3), "L"),
    (Turn(Side.RIGHT, 1, 2), "R2"),
    (Turn(Side.BACK, 1, 1), "B'"),
    (Turn(Side.TOP, 1, 3), "U"),
    (Turn(Side.BOTTOM, 1, 2), "D2"),

    (Rotate(Side.FRONT, False), "Z"),
    (Rotate(Side.BACK, False), "Z'"),
    (Rotate(Side.BACK, True), "Z2"),
    (Rotate(Side.FRONT, True), "Z2"),
    (Rotate(Side.RIGHT, False), "X"),
    (Rotate(Side.BOTTOM, False), "Y'")
])
def test_representation(action: Action, expected: str):
    actual = get_action_representation(action)
    assert expected == actual
