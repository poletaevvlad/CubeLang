from abc import ABC, abstractmethod
from typing import Union, List, Iterable, TypeVar, Tuple
from itertools import groupby
import enum

from .cube import Cube
from .orientation import Orientation, Side


T = TypeVar("T")


def count_occurrences(seq: Iterable[T]) -> Iterable[Tuple[T, int]]:
    return ((val, sum(1 for _ in group)) for val, group in groupby(seq))


class Action(ABC):
    @abstractmethod
    def perform(self, cube: Cube, orientation: Orientation) -> Orientation:
        pass


class Rotate(Action):
    def __init__(self, around: Side, twice: bool = False) -> None:
        self.axis_side: Side = around
        self.twice = twice

    def perform_single(self, orientation: Orientation) -> Orientation:
        if self.axis_side == Side.FRONT:
            return orientation.rotate_clockwise()
        elif self.axis_side == Side.BACK:
            return orientation.rotate_counterclockwise()
        elif self.axis_side == Side.RIGHT:
            return orientation.to_bottom
        elif self.axis_side == Side.LEFT:
            return orientation.to_top
        elif self.axis_side == Side.TOP:
            return orientation.to_right
        else:
            return orientation.to_left

    def perform(self, cube: Cube, orientation: Orientation) -> Orientation:
        if self.twice:
            return self.perform_single(self.perform_single(orientation))
        else:
            return self.perform_single(orientation)

    def __repr__(self):
        return f"Rotate({self.axis_side}, {self.twice})"

    @staticmethod
    def from_turn_steps(steps: Iterable[Side]) -> Iterable["Rotate"]:
        for side, turns in count_occurrences(steps):
            turns = turns % 4
            if turns == 3:
                side = side.opposite()
            if turns != 0:
                yield Rotate(side, turns == 2)


class TurningType(enum.Enum):
    HORIZONTAL = enum.auto()
    VERTICAL = enum.auto()
    SLICE = enum.auto()


class Turn(Action):
    TYPES = {
        Side.LEFT: TurningType.VERTICAL, Side.RIGHT: TurningType.VERTICAL,
        Side.TOP: TurningType.HORIZONTAL, Side.BOTTOM: TurningType.HORIZONTAL,
        Side.FRONT: TurningType.SLICE, Side.BACK: TurningType.SLICE
    }

    def __init__(self, side: Union[Side, TurningType], indices: Union[int, List[int]], turns: int = 1) -> None:
        self.sides: List[int] = indices if isinstance(indices, list) else [indices]
        self.turns: int = turns

        self.type: TurningType
        if isinstance(side, Side):
            self.type = Turn.TYPES[side]

            if side in {Side.BACK, Side.RIGHT, Side.BOTTOM}:
                self.sides = [-x for x in self.sides]

            if side not in {Side.BOTTOM, Side.RIGHT, Side.FRONT}:
                self.turns: int = 4 - turns
        else:
            self.type = side

    def perform(self, cube: Cube, orientation: Orientation) -> Orientation:
        turning_functions = {
            TurningType.VERTICAL: cube.turn_vertical,
            TurningType.HORIZONTAL: cube.turn_horizontal,
            TurningType.SLICE: cube.turn_slice
        }
        rotate_function = turning_functions[self.type]
        for side in self.sides:
            rotate_function(orientation, side, self.turns)
        return orientation

    def __repr__(self):
        return f"Turn({self.type}, {self.sides}, {self.turns})"

    def _transform(self, turn: Side) -> "Turn":
        if Turn.TYPES[turn] == self.type:
            return self

        if turn == Side.TOP:
            if self.type == TurningType.SLICE:
                return Turn(TurningType.VERTICAL, self.sides, self.turns)
            else:  # TurningType.VERTICAL
                return Turn(TurningType.SLICE, [-x for x in self.sides], self.turns)
        elif turn == Side.FRONT:
            if self.type == TurningType.VERTICAL:
                return Turn(TurningType.HORIZONTAL, self.sides, self.turns)
            else:  # TurningType.HORIZONTAL
                return Turn(TurningType.VERTICAL, [-x for x in self.sides], self.turns)
        elif turn == Side.RIGHT:
            if self.type == TurningType.SLICE:
                return Turn(TurningType.HORIZONTAL, self.sides, self.turns)
            else:  # TurningType.HORIZONTAL
                return Turn(TurningType.SLICE, [-x for x in self.sides], self.turns)
        else:
            raise ValueError("Unsupported turn")

    def from_orientation(self, orientation: Orientation) -> "Turn":
        result: Turn = self
        for turn in orientation.turns_to_origin():
            result = result._transform(turn)
        return result
