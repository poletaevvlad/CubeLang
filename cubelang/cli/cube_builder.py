from argparse import ArgumentParser, Namespace, ArgumentTypeError

from .options import formula_type, side_colors_type, integer_type
from ..actions import Action
from ..cube import Cube
from ..orientation import Orientation, Color, Side
from ..cube_runtime import CubeRuntime
from typing import Optional, List, Tuple


def apply_side(cube: Cube, orientation: Orientation,
               colors: Optional[List[List[Color]]]):
    if colors is None:
        return
    side = cube.get_side(orientation)
    if side.rows != len(colors):
        raise ArgumentTypeError(f"Incorrect number of lines")
    elif side.columns != len(colors[0]):
        raise ArgumentTypeError(f"Incorrect number of columns")

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
        apply_side(self.cube, orientation, colors)
        return self

    def get(self) -> Tuple[Cube, Orientation]:
        return self.cube, self.orientation


def init_cube_args_parser(argparse: ArgumentParser):
    group = argparse.add_argument_group("cube options")
    group.add_argument("-d", dest="dimension", help="dimensions of a cube",
                       default=3, metavar="N", type=integer_type(2))
    group.add_argument("-s", dest="scramble", help="formula to scramble a cube",
                       default=[], type=formula_type, metavar="FORMULA")
    for name, side in CubeRuntime.SIDE_NAMES.items():
        group.add_argument("--" + name, type=side_colors_type, metavar="COLORS",
                           help=f"colors of the {name} face of a cube", default=None)


def build_cube(arguments: Namespace):
    builder = CubeBuilder((arguments.dimension,) * 3)
    for name, side in CubeRuntime.SIDE_NAMES.items():
        builder.side(side, getattr(arguments, name))
    return builder.scramble(arguments.scramble).get()
