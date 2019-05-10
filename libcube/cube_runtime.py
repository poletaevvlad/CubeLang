from .cube import Cube
from .orientation import Orientation, Side, Color
from .stdlib import Library
from .compiler import types
from .actions import Turn, Action, Rotate
from typing import Callable


class CubeRuntime:
    SIDE_NAMES = {
        "front": Side.FRONT, "back": Side.BACK,
        "left": Side.LEFT, "right": Side.RIGHT,
        "top": Side.TOP, "bottom": Side.BOTTOM
    }

    COLOR_NAMES = {
        "red": Color.RED, "green": Color.GREEN, "blue": Color.BLUE,
        "white": Color.WHITE, "yellow": Color.YELLOW, "orange": Color.ORANGE
    }

    def __init__(self, callback: Callable[[Action], None]):
        self.cube = Cube((3, 3, 3))
        self.orientation = Orientation()
        self.callback = callback

        self.functions = Library()
        self.functions.add_function("cube_turn", self.perform_turn, [types.Side, types.Integer], types.Void)
        self.functions.add_function("cube_get_color", self.get_color,
                                    [types.Color, types.Integer, types.Integer], types.Color)
        self.functions.add_function("cube_rotate", self.perform_rotate, [types.Side, types.Bool], types.Void)

        for name, side in CubeRuntime.SIDE_NAMES.items():
            self.functions.add_value(name, types.Side, side)
        for name, color in CubeRuntime.COLOR_NAMES.items():
            self.functions.add_value(name, types.Color, color)

    def perform_turn(self, side: Side, amount: int):
        action = Turn(side, 1, amount)
        self.orientation = action.perform(self.cube, self.orientation)
        self.callback(action)

    def perform_rotate(self, side: Side, twice: bool):
        action = Rotate(side, twice)
        self.orientation = action.perform(self.cube, self.orientation)
        self.callback(action)

    def get_color(self, side: Side, i: int, j: int):
        if side == Side.FRONT:
            local_orientation = self.orientation
        elif side == Side.LEFT:
            local_orientation = self.orientation.to_left
        elif side == Side.RIGHT:
            local_orientation = self.orientation.to_right
        elif side == Side.BACK:
            local_orientation = self.orientation.to_left.to_left
        elif side == Side.TOP:
            local_orientation = self.orientation.to_top
        else:
            local_orientation = self.orientation.to_bottom
        return self.cube.get_side(local_orientation).colors[i, j]
