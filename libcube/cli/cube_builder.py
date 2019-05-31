from click import BadOptionUsage

from libcube.cube import Cube
from libcube.orientation import Orientation, Color
from typing import Optional, List


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
