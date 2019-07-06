from typing import Callable, Optional, List, Union
from collections import deque
import sys

from .actions import Turn, Action, Rotate
from .compiler import types
from .cube import Cube
from .orientation import Orientation, Side, Color
from .pattern import Pattern
from .stdlib import Library
from .execution.rt_error import TerminateExecutionError


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

    EXPORTED_FUNCTIONS = [
        ("push_orientation", "push_orientation", [], types.Void),
        ("pop_orientation", "pop_orientation", [], types.Void),
        ("suspend_rotations", "suspend_rotations", [], types.Void),
        ("resume_rotations", "resume_rotations", [], types.Void),
        ("exit", "perform_exit", [], types.Void),
        ("print", "debug_print", [types.T, ...], types.Void)
    ]

    def __init__(self, cube: Cube, orientation: Orientation,
                 callback: Callable[[Action], None],
                 done_callback: Callable[[], None]):
        self.cube = cube
        self.orientation = orientation
        self.orientations_stack = deque()
        self.suspended_orientation: Optional[Orientation] = None
        self.callback = callback
        self.done_callback = done_callback

        self.functions = Library()
        for name, local_name, argument_types, return_type in CubeRuntime.EXPORTED_FUNCTIONS:
            self.functions.add_function(name, getattr(self, local_name),
                                        argument_types, return_type)

        self.functions.exec_globals["cube_turn"] = self.perform_turn
        self.functions.exec_globals["cube_rotate"] = self.perform_rotate
        self.functions.exec_globals["cube_get_color"] = self.get_color
        self.functions.exec_globals["orient"] = self.perform_orient
        self.functions.exec_globals["Pattern"] = Pattern

        for name, side in CubeRuntime.SIDE_NAMES.items():
            self.functions.add_value(name, types.Side, side)
        for name, color in CubeRuntime.COLOR_NAMES.items():
            self.functions.add_value(name, types.Color, color)

    def yield_action(self, action: Action) -> None:
        if self.suspended_orientation is None:
            self.callback(action)
        elif isinstance(action, Turn):
            self.callback(action.from_orientation(self.orientation,
                                                  self.suspended_orientation))

    def debug_print(self, *args):
        print(*args, file=sys.stderr)

    def perform_orient(self, *args, **kwargs) -> bool:
        new_orientation = self.cube.orient(self.orientation, *args, **kwargs)
        if new_orientation is not None:
            actions = Rotate.from_turn_steps(self.orientation.turns_to(new_orientation))
            for action in actions:
                self.yield_action(action)
            self.orientation = new_orientation
            return True
        return False

    def suspend_rotations(self):
        self.suspended_orientation = self.orientation

    def resume_rotations(self):
        turns = self.suspended_orientation.turns_to(self.orientation)
        self.suspended_orientation = None
        for action in Rotate.from_turn_steps(turns):
            self.yield_action(action)

    def push_orientation(self):
        self.orientations_stack.append(self.orientation)

    def pop_orientation(self):
        new_orientation = self.orientations_stack.pop()
        turns = self.orientation.turns_to(new_orientation)
        for action in Rotate.from_turn_steps(turns):
            self.yield_action(action)
        self.orientation = new_orientation

    def perform_turn(self, side: Side, amount: int,
                     indices: List[Union[int, type(Ellipsis)]]):
        action = Turn(side, indices, amount)
        self.orientation = action.perform(self.cube, self.orientation)
        self.yield_action(action)

    def perform_rotate(self, side: Side, twice: bool):
        action = Rotate(side, twice)
        self.orientation = action.perform(self.cube, self.orientation)
        self.yield_action(action)

    def perform_exit(self):
        raise TerminateExecutionError()

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
