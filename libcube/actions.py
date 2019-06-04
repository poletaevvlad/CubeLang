import enum
from abc import ABC, abstractmethod
from typing import Union, List, Iterable, TypeVar, Optional, Set

from .cube import Cube
from .orientation import Orientation, Side, count_occurrences

T = TypeVar("T")


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

    def perform(self, cube: Optional[Cube], orientation: Orientation) -> Orientation:
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

    def __init__(self, side: Union[Side, TurningType],
                 indices: Union[int, List[Union[int, type(Ellipsis)]]],
                 turns: int = 1) -> None:
        self.indices: List[Union[int, ellipsis]] = indices if isinstance(indices, list) else [indices]
        self.turns: int = turns

        self.type: TurningType
        if isinstance(side, Side):
            self.type = Turn.TYPES[side]

            if side in {Side.BACK, Side.RIGHT, Side.BOTTOM}:
                self.indices = Turn.opposite_side(self.indices)

            if side not in {Side.BOTTOM, Side.RIGHT, Side.FRONT}:
                self.turns: int = 4 - turns
        else:
            self.type = side

    def perform(self, cube: Cube, orientation: Orientation) -> Orientation:
        turning_functions = {
            TurningType.VERTICAL: (cube.turn_vertical, cube.get_side(orientation).columns),
            TurningType.HORIZONTAL: (cube.turn_horizontal, cube.get_side(orientation).rows),
            TurningType.SLICE: (cube.turn_slice, cube.get_side(orientation.to_right).columns)
        }
        rotate_function, size = turning_functions[self.type]
        for side in Turn.normalize_indices(self.indices, size):
            rotate_function(orientation, side, self.turns)
        return orientation

    def __repr__(self):
        return f"Turn({self.type}, {self.indices}, {self.turns})"

    def _transform(self, turn: Side) -> "Turn":
        if Turn.TYPES[turn] == self.type:
            return self

        if turn == Side.TOP:
            if self.type == TurningType.SLICE:
                return Turn(TurningType.VERTICAL, self.indices, 4 - self.turns)
            else:  # TurningType.VERTICAL
                return Turn(TurningType.SLICE, [-x for x in self.indices], self.turns)
        elif turn == Side.FRONT:
            if self.type == TurningType.VERTICAL:
                return Turn(TurningType.HORIZONTAL, self.indices, 4 - self.turns)
            else:  # TurningType.HORIZONTAL
                return Turn(TurningType.VERTICAL, [-x for x in self.indices], self.turns)
        elif turn == Side.RIGHT:
            if self.type == TurningType.SLICE:
                return Turn(TurningType.HORIZONTAL, self.indices, 4 - self.turns)
            else:  # TurningType.HORIZONTAL
                return Turn(TurningType.SLICE, [-x for x in self.indices], self.turns)
        else:
            raise ValueError("Unsupported turn")

    def from_orientation(self, orientation: Orientation, origin=Orientation()) -> "Turn":
        result: Turn = self
        for turn in orientation.turns_to(origin):
            result = result._transform(turn)
        return result

    @staticmethod
    def opposite_side(indices: List[Union[int, type(Ellipsis)]]) -> List[Union[int, type(Ellipsis)]]:
        return [Ellipsis if index == Ellipsis else -index for index in indices]

    @staticmethod
    def normalize_indices(indices: List[Union[int, type(Ellipsis)]], width: int) -> Set[int]:
        def to_positive(idx: Union[int, type(Ellipsis)]):
            if idx == Ellipsis:
                return ...
            elif idx < 0:
                return width + idx + 1
            else:
                return idx

        def add_ends(it: Iterable[Union[int, type(Ellipsis)]]):
            yield 0
            yield from it
            yield width + 1

        def get_tripples(it: Iterable[Union[int, type(Ellipsis)]]):
            v_iter = iter(it)
            a = next(v_iter)
            b = next(v_iter)
            while True:
                try:
                    c = next(v_iter)
                    yield a, b, c
                    a, b = b, c
                except StopIteration:
                    break

        result = set()
        stream = add_ends(map(to_positive, indices))
        for prev_value, value, next_value in get_tripples(stream):
            if value == Ellipsis:
                if prev_value > next_value:
                    prev_value, next_value = next_value, prev_value
                result.update(range(prev_value + 1, next_value))
            else:
                result.add(value)
        return result
