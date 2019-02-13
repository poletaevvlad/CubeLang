from abc import ABC, abstractmethod

from .cube import Cube
from .orientation import Orientation, Side


class Action(ABC):
    @abstractmethod
    def perform(self, cube: Cube, orientation: Orientation) -> Orientation:
        pass


class Rotate(Action):
    def __init__(self, around: Side):
        self.axis_side = around

    def perform(self, cube: Cube, orientation: Orientation) -> Orientation:
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
