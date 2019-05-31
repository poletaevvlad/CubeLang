from click import BadOptionUsage

from libcube.actions import Action
from libcube.cube import Cube
from libcube.orientation import Orientation, Color, Side
from typing import Optional, List, Tuple


def apply_side(cube: Cube, orientation: Orientation,
               colors: Optional[List[List[Color]]], option_name: str):
    if colors is None:
        return
    side = cube.get_side(orientation)
    if side.rows != len(colors):
        raise BadOptionUsage(option_name, f"Invalid value for \"--{option_name}\": Incorrect number of lines")
    elif side.columns != len(colors[0]):
        raise BadOptionUsage(option_name, f"Invalid value for \"--{option_name}\": Incorrect number of columns")

    for i, line in enumerate(colors):
        for j, color in enumerate(line):
            side.colors[i, j] = color


class CubeBuilder:
    def __init__(self, size: Tuple[int, int, int]):
        self.cube = Cube(size)
        self.orientation = Orientation()

    def scramble(self, actions: List[Action]) -> "CubeBuilder":
        for action in actions:
            self.orientation = action.perform(self.cube, self.orientation)
        return self

    def side(self, side: Side, colors: List[List[Color]]) -> "CubeBuilder":
        orientation = Orientation.regular(side)
        apply_side(self.cube, orientation, colors, side.name.lower())
        return self

    def get(self) -> Tuple[Cube, Orientation]:
        return self.cube, self.orientation
