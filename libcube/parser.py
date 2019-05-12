from typing import Iterator, Callable, Dict, Optional
import string

from .actions import Turn, Action, Rotate, TurningType
from .orientation import Side

ActionFactory = Callable[[bool, bool], Action]


def create_turn_factory(side: Side) -> ActionFactory:
    def factory(double: bool, opposite: bool) -> Action:
        return Turn(side, 1, 2 if double else 3 if opposite else 1)
    return factory


def create_rotate_factory(side: Side) -> ActionFactory:
    def factory(double: bool, opposite: bool) -> Action:
        return Rotate(side.opposite() if opposite else side, double)
    return factory


sides_letters: Dict[Side, str] = {
    Side.LEFT: "L",
    Side.RIGHT: "R",
    Side.FRONT: "F",
    Side.BACK: "B",
    Side.TOP: "U",
    Side.BOTTOM: "D"
}

rotation_letters: Dict[Side, str] = {
    Side.RIGHT: "X",
    Side.TOP: "Y",
    Side.FRONT: "Z",
}

action_factories: Dict[str, ActionFactory] = {
    **{letter: create_turn_factory(side) for side, letter in sides_letters.items()},
    **{letter: create_rotate_factory(side) for side, letter in rotation_letters.items()}
}


class ParsingError(Exception):
    def __init__(self, message: str, column: int) -> None:
        super(ParsingError, self).__init__(message)
        self.column = column


def parse_actions(algorithm: str) -> Iterator[Action]:
    double = False
    opposite = False
    factory: Optional[ActionFactory] = None

    for index, char in enumerate(algorithm):
        if char in string.whitespace:
            continue

        if char == "'" or char == "2":
            if factory is None:
                raise ParsingError(f"Illegal modifier '{char}' at {index + 1}", index)
            if char == "'":
                opposite = True
            else:
                double = True
        elif char in action_factories:
            if factory is not None:
                yield factory(double, opposite)
                double = False
                opposite = False
            factory = action_factories[char]
        else:
            raise ParsingError(f"Unknown character '{char}' at {index + 1}", index)
    if factory is not None:
        yield factory(double, opposite)


def get_action_representation(action: Action) -> str:
    if isinstance(action, Turn):
        if action.type == TurningType.VERTICAL:
            letter = "L" if action.sides[0] > 0 else "R"
        elif action.type == TurningType.HORIZONTAL:
            letter = "U" if action.sides[0] > 0 else "D"
        else:
            letter = "F" if action.sides[0] > 0 else "B"

        if action.turns == 2:
            return letter + "2"
        else:
            turns = action.turns
            if letter not in {"D", "R", "F"}:
                turns = 4 - turns
            if turns == 3:
                letter += "'"
            return letter
    elif isinstance(action, Rotate):
        if action.axis_side in rotation_letters:
            letter = rotation_letters[action.axis_side]
        else:
            letter = rotation_letters[action.axis_side.opposite()]
            if not action.twice:
                letter += "'"
        if action.twice:
            return letter + "2"
        else:
            return letter
    else:
        raise ValueError(f"Unknown action type: {type(Action)}")
