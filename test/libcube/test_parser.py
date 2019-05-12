from pytest import raises
import pytest

from libcube.parser import ParsingError, parse_actions, get_action_representation
from libcube.actions import Turn, Action, Rotate, TurningType
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
    expected_sides = [TurningType.VERTICAL, TurningType.VERTICAL,
                      TurningType.HORIZONTAL, TurningType.VERTICAL,
                      TurningType.HORIZONTAL, TurningType.VERTICAL]
    expected_turns = [1, 2, 1, 1, 3, 3]

    assert len(actions) == len(expected_sides)
    for action, type, turns in zip(actions, expected_sides, expected_turns):
        assert isinstance(action, Turn)
        assert action.type == type
        assert action.turns == turns


@pytest.mark.parametrize("text, type, index, turns", [
    ("F", TurningType.SLICE, 1, 1),
    ("F'", TurningType.SLICE, 1, 3),
    ("B", TurningType.SLICE, -1, 3),
    ("B'", TurningType.SLICE, -1, 1),

    ("R", TurningType.VERTICAL, -1, 1),
    ("R'", TurningType.VERTICAL, -1, 3),
    ("L", TurningType.VERTICAL, 1, 3),
    ("L'", TurningType.VERTICAL, 1, 1),

    ("U", TurningType.HORIZONTAL, 1, 3),
    ("U'", TurningType.HORIZONTAL, 1, 1),
    ("D", TurningType.HORIZONTAL, -1, 1),
    ("D'", TurningType.HORIZONTAL, -1, 3)
])
def test_turn_single(text: str, type: TurningType, index: int, turns: int):
    actions = list(parse_actions(text))
    assert len(actions) == 1
    action = actions[0]
    assert isinstance(action, Turn)
    assert action.sides[0] == index
    assert action.turns == turns
    assert action.type == type

    assert text == get_action_representation(action)


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
    (Turn(Side.LEFT, 1, 1), "L"),
    (Turn(Side.RIGHT, 1, 2), "R2"),
    (Turn(Side.BACK, 1, 3), "B'"),
    (Turn(Side.TOP, 1, 1), "U"),
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
