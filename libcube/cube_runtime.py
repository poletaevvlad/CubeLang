from typing import Callable

from .actions import Turn, Action, Rotate
from .compiler import types
from .cube import Cube
from .orientation import Orientation, Side, Color
from .pattern import Pattern
from .stdlib import Library


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

    def __init__(self, cube: Cube, orientation: Orientation,
                 callback: Callable[[Action], None],
                 done_callback: Callable[[], None]):
        self.cube = cube
        self.orientation = orientation
        self.callback = callback
        self.done_callback = done_callback

        self.functions = Library()
        self.functions.add_function("cube_turn", self.perform_turn, [types.Side, types.Integer], types.Void)
        self.functions.add_function("cube_get_color", self.get_color,
                                    [types.Color, types.Integer, types.Integer], types.Color)
        self.functions.add_function("cube_rotate", self.perform_rotate, [types.Side, types.Bool], types.Void)
        self.functions.exec_globals["orient"] = self.perform_orient
        self.functions.exec_globals["Pattern"] = Pattern

        for name, side in CubeRuntime.SIDE_NAMES.items():
            self.functions.add_value(name, types.Side, side)
        for name, color in CubeRuntime.COLOR_NAMES.items():
            self.functions.add_value(name, types.Color, color)

    def perform_orient(self, *args, **kwargs):
        new_orientation = self.cube.orient(self.orientation, *args, **kwargs)
        if new_orientation is not None:
            actions = Rotate.from_turn_steps(self.orientation.turns_to(new_orientation))
            for action in actions:
                self.callback(action)
            self.orientation = new_orientation
            return True
        else:
            return False

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

    def finished(self):
        self.done_callback()
