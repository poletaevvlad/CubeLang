from typing import List

from libcube.cube import Cube
from libcube.sides import CubeSide, CubeSideView, ICubeSide
from libcube.orientation import Orientation, Side, Color

from unittest.mock import MagicMock
import pytest


def test_get_side():
    orientation: Orientation = Orientation(Side.LEFT, Side.TOP)
    orientation.get_side_rotation = MagicMock()
    orientation.get_side_rotation.return_value = 0

    cube = Cube((3, 3, 3))
    side = cube.get_side(orientation)
    assert isinstance(side, CubeSide)
    assert side == cube.sides[Side.LEFT]


def test_get_side_rotated():
    orientation: Orientation = Orientation(Side.LEFT, Side.TOP)
    orientation.get_side_rotation = MagicMock()
    orientation.get_side_rotation.return_value = 3

    cube = Cube((3, 3, 3))
    side = cube.get_side(orientation)
    assert isinstance(side, CubeSideView)
    assert side.side == cube.sides[Side.LEFT]
    assert side.rotation == 3


def _set_side_colors(side: ICubeSide, colors: List[List[Color]]) -> None:
    for i, row in enumerate(colors):
        for j, color in enumerate(row):
            side[i, j] = color


def side_to_string(side: ICubeSide):
    out = []
    for i in range(side.rows):
        for j in range(side.columns):
            color = side[i, j].name[0].upper()
            out.append(color)
        out.append("/")
    return "".join(out[:-1])


def assert_cube(cube: Cube, front: str, right: str, back: str, left: str,
                top: str, bottom: str) -> None:
    orientation = Orientation()
    assert front == side_to_string(cube.get_side(orientation))
    assert right == side_to_string(cube.get_side(orientation.to_right))
    assert back == side_to_string(cube.get_side(orientation.to_right.to_right))
    assert left == side_to_string(cube.get_side(orientation.to_left))
    assert top == side_to_string(cube.get_side(orientation.to_top))
    assert bottom == side_to_string(cube.get_side(orientation.to_bottom))


@pytest.fixture()
def sample_cube() -> Cube:
    cube = Cube((3, 3, 3))
    orientation = Orientation()
    assert orientation.get_side_rotation() == 0

    red = cube.get_side(orientation)
    _set_side_colors(red, [
        [Color.ORANGE, Color.RED, Color.GREEN],
        [Color.YELLOW, Color.RED, Color.GREEN],
        [Color.BLUE, Color.WHITE, Color.GREEN]
    ])

    green = cube.get_side(orientation.to_right)
    _set_side_colors(green, [
        [Color.RED, Color.ORANGE, Color.ORANGE],
        [Color.RED, Color.GREEN, Color.WHITE],
        [Color.RED, Color.GREEN, Color.WHITE]
    ])

    orange = cube.get_side(orientation.to_left.to_left)
    _set_side_colors(orange, [
        [Color.YELLOW, Color.YELLOW, Color.RED],
        [Color.ORANGE, Color.ORANGE, Color.WHITE],
        [Color.ORANGE, Color.ORANGE, Color.GREEN]
    ])

    blue = cube.get_side(orientation.to_left)
    _set_side_colors(blue, [
        [Color.YELLOW, Color.YELLOW, Color.YELLOW],
        [Color.BLUE, Color.BLUE, Color.RED],
        [Color.ORANGE, Color.WHITE, Color.WHITE]
    ])

    yellow = cube.get_side(orientation.to_top)
    _set_side_colors(yellow, [
        [Color.BLUE, Color.GREEN, Color.GREEN],
        [Color.BLUE, Color.YELLOW, Color.YELLOW],
        [Color.BLUE, Color.BLUE, Color.WHITE]
    ])

    white = cube.get_side(orientation.to_bottom)
    _set_side_colors(white, [
        [Color.RED, Color.GREEN, Color.YELLOW],
        [Color.RED, Color.WHITE, Color.ORANGE],
        [Color.WHITE, Color.BLUE, Color.BLUE]
    ])

    assert_cube(cube, "ORG/YRG/BWG", "ROO/RGW/RGW", "YYR/OOW/OOG", "YYY/BBR/OWW",
                "BGG/BYY/BBW", "RGY/RWO/WBB")
    return cube


def test_rotation_rightmost(sample_cube: Cube) -> None:
    orientation = Orientation(Side.FRONT, Side.RIGHT)
    sample_cube.rotate_vertical(orientation, -1, 1)

    assert_cube(sample_cube, "ORG/YRG/OWW", "ROO/RGW/BWG", "YYR/OOW/RGW", "YYY/BBR/OOG",
                "BGG/BYY/BBW", "WRR/BWG/BOY")


def test_rotation_leftmost(sample_cube: Cube) -> None:
    orientation = Orientation(Side.BACK, Side.BOTTOM)
    sample_cube.rotate_vertical(orientation, 1, 3)

    assert_cube(sample_cube, "BRG/BRG/BWG", "ROO/RGW/RGW", "YYW/OOR/OOR", "OBY/WBY/WRY",
                "GGG/WYY/RBW", "OGY/YWO/BBB")
