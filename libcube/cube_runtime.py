from .cube import Cube
from .orientation import Orientation, Side, Color
from .stdlib import Library
from .compiler import types
from .actions import Turn, Action
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

        for name, side in CubeRuntime.SIDE_NAMES.items():
            self.functions.add_value(name, types.Side, side)
        for name, color in CubeRuntime.COLOR_NAMES.items():
            self.functions.add_value(name, types.Color, color)

    def perform_turn(self, side: Side, amount: int):
        action = Turn(side, 1, amount)
        self.orientation = action.perform(self.cube, self.orientation)
        self.callback(action)
