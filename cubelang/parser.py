from typing import Iterator, Dict
from string import whitespace

from .actions import Turn, Action, Rotate
from .orientation import Side


SIDE_LETTERS: Dict[str, Side] = {
    "L": Side.LEFT,
    "R": Side.RIGHT,
    "F": Side.FRONT,
    "B": Side.BACK,
    "U": Side.TOP,
    "D": Side.BOTTOM
}

ROTATE_LETTERS: Dict[str, Side] = {
    "X": Side.RIGHT,
    "Y": Side.TOP,
    "Z": Side.FRONT
}

ROTATE_REVERSE: Dict[Side, str] = {
    Side.RIGHT: "X", Side.LEFT: "X",
    Side.TOP: "Y", Side.BOTTOM: "Y",
    Side.FRONT: "Z", Side.BACK: "Z"
}


class ParsingError(Exception):
    def __init__(self, message: str, column: int) -> None:
        super(ParsingError, self).__init__(message)
        self.column = column


class ParsingStateMachine:
    def __init__(self):
        self.actions = []
        self.column = 0

        self.action_type = None
        self.amount = 1

        self.current_number = 0
        self.number_present = False
        self.numbers = []

    def yield_action(self):
        if self.action_type is None:
            return
        if self.action_type in ROTATE_LETTERS:
            side = ROTATE_LETTERS[self.action_type]
            if self.amount == 3:
                side = side.opposite()
            self.actions.append(Rotate(side, self.amount == 2))
        else:
            action = Turn(SIDE_LETTERS[self.action_type],
                          self.numbers if len(self.numbers) > 0 else 1,
                          self.amount)
            self.actions.append(action)

        self.action_type = None
        self.numbers = []
        self.amount = 1
        self.number_present = False

    def _unexpected(self, char: str):
        if char == "\n":
            raise ParsingError(f"Unexpected end at {self.column + 1}", self.column)
        else:
            raise ParsingError(f"Unexpected character: '{char}' at {self.column + 1}", self.column)

    def state_action_type(self, char: str):
        self.yield_action()
        if char == "\n":
            return True, None
        elif char not in SIDE_LETTERS and char not in ROTATE_LETTERS:
            self._unexpected(char)
        else:
            self.action_type = char
            return True, self.state_action_spec

    def state_action_spec(self, char: str):
        if char in SIDE_LETTERS or char in ROTATE_LETTERS:
            return False, self.state_action_type
        if char == "'":
            self.amount = 3
            return True, self.state_range_start
        elif char == "2":
            self.amount = 2
            return True, self.state_range_start
        elif char == "[":
            return False, self.state_range_start
        elif char == "\n":
            return True, None
        else:
            self._unexpected(char)

    def state_range_start(self, char: str):
        if char == "[":
            if self.action_type in ROTATE_LETTERS:
                self._unexpected(char)
            return True, self.state_range_number
        else:
            return False, self.state_action_type

    def state_range_number(self, char: str):
        def next_number(force_number: bool = False):
            if not self.number_present and force_number:
                self._unexpected(char)
            elif self.number_present:
                self.numbers.append(self.current_number)
            self.current_number = 0
            self.number_present = False

        if char.isdigit():
            self.current_number = self.current_number * 10 + int(char)
            self.number_present = True
        elif char == ":":
            if not self.number_present and len(self.numbers) > 0:
                self._unexpected(char)
            next_number()
            self.numbers.append(...)
        elif char == ",":
            next_number(True)
        elif char == "]":
            if not(self.number_present or (len(self.numbers) > 0 and self.numbers[-1] == Ellipsis)):
                self._unexpected(char)
            next_number()
            return True, self.state_action_type
        else:
            self._unexpected(char)
        return True, self.state_range_number

    def parse(self, algorithm: str):
        algorithm = algorithm.translate({ord(x): None for x in whitespace}) + "\n"
        state = self.state_action_type
        self.column = 0

        while self.column < len(algorithm):
            goto_next, state = state(algorithm[self.column])
            if goto_next:
                self.column += 1
        self.yield_action()


def parse_actions(algorithm: str) -> Iterator[Action]:
    sm = ParsingStateMachine()
    sm.parse(algorithm)
    return sm.actions
