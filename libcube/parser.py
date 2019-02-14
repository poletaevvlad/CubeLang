from typing import Iterator, Callable, Dict, Optional
import string

from .actions import Turn, Action
from .orientation import Side

ActionFactory = Callable[[bool, bool], Action]


def create_turn_factory(side: Side) -> ActionFactory:
    def factory(double: bool, opposite: bool) -> Action:
        return Turn(side, 1, 2 if double else 3 if opposite else 1)
    return factory


action_factories: Dict[str, ActionFactory] = {
    "L": create_turn_factory(Side.LEFT),
    "R": create_turn_factory(Side.RIGHT),
    "F": create_turn_factory(Side.FRONT),
    "B": create_turn_factory(Side.BACK),
    "U": create_turn_factory(Side.TOP),
    "D": create_turn_factory(Side.BOTTOM)
}


class ParsingError(Exception):
    def __init__(self, message: str, column: int):
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
