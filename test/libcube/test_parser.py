from pytest import raises

from libcube.parser import ParsingError, parse_actions
from libcube.actions import Turn
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
