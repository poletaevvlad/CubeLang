from abc import ABC, abstractmethod
from typing import Union, List

from .cube import Cube
from .orientation import Orientation, Side


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


class Turn(Action):
    def __init__(self, side: Side, sides: Union[int, List[int]], turns: int = 1) -> None:
        self.side: Side = side
        self.sides: List[int] = sides if isinstance(sides, list) else [sides]
        if side in {Side.BOTTOM, Side.RIGHT, Side.FRONT}:
            self.turns: int = turns
        else:
            self.turns: int = 4 - turns
        self.index_multiplier = 1 if side not in {Side.BACK, Side.RIGHT, Side.BOTTOM} else -1

    def perform(self, cube: Cube, orientation: Orientation) -> Orientation:
        if self.side == Side.LEFT or self.side == Side.RIGHT:
            rotate_function = cube.rotate_vertical
        elif self.side == Side.TOP or self.side == Side.BOTTOM:
            rotate_function = cube.rotate_horizontal
        else:
            rotate_function = cube.rotate_slice

        for side in self.sides:
            rotate_function(orientation, side * self.index_multiplier, self.turns)
        return orientation
