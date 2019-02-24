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
            side.colors[i, j] = color


def side_to_string(side: ICubeSide):
    out = []
    for i in range(side.rows):
        for j in range(side.columns):
            color = side.colors[i, j].name[0].upper()
            out.append(color)
        out.append("/")
    return "".join(out[:-1])


def data_to_string(side: ICubeSide):
    out = []
    for i in range(side.rows):
        out.append(" ".join(str(side[i, j].data) for j in range(side.columns)))
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


def test_rotation_horizontal(sample_cube: Cube) -> None:
    orientation = Orientation(Side.RIGHT, Side.FRONT)
    sample_cube.rotate_horizontal(orientation, 1, 1)

    assert_cube(sample_cube, "GGG/RRW/OYB", "YOO/GGW/RGW", "YYR/OOW/OOG", "YYW/BBB/OWB",
                "BGG/BYY/RRR", "YRW/RWO/WBB")


def test_rotation_horizontal_last(sample_cube: Cube) -> None:
    orientation = Orientation(Side.BOTTOM, Side.LEFT)
    sample_cube.rotate_horizontal(orientation, -1, 3)

    assert_cube(sample_cube, "ORG/YRY/BWW", "OWW/OGG/RRR", "BYR/OOW/YOG", "YYY/BBR/OWW",
                "BGO/BYO/BBY", "RGG/RWG/WBG")


def test_rotation_slice(sample_cube: Cube) -> None:
    orientation = Orientation(Side.RIGHT, Side.BACK)
    sample_cube.rotate_slice(orientation, 1, 1)

    assert_cube(sample_cube, "ORY/YRO/BWB", "RRR/GGO/WWO", "WYR/YOW/GOG", "YYY/BBR/OWW",
                "BGG/BYG/BBG", "RGO/RWO/WBY")


def test_data_flat(sample_cube: Cube) -> None:
    orientation = Orientation(Side.RIGHT, Side.BACK)

    sample_cube.set_data(orientation, 1, 1, "a")
    sample_cube.set_data(orientation, 0, 0, "b")
    sample_cube.set_data(orientation, 1, 2, "c")

    def get_side(orient: Orientation) -> str:
        return data_to_string(sample_cube.get_side(orient))

    orientation = Orientation(Side.FRONT, Side.TOP)
    assert get_side(orientation) == "None None None/None None None/None None None"
    assert get_side(orientation.to_top) == "None None b/None None None/None None None"
    assert get_side(orientation.to_right) == "None None b/None a None/None c None"
    assert get_side(orientation.to_right.to_right) == "b None None/None None None/None None None"
    assert get_side(orientation.to_bottom) == "None None None/None None c/None None None"


def test_data_rotation(sample_cube: Cube) -> None:
    orientation = Orientation(Side.FRONT, Side.TOP)
    sample_cube.set_data(orientation, 0, 2, "b")
    sample_cube.set_data(orientation, 1, 2, "a")
    sample_cube.rotate_vertical(orientation, 3, 1)

    def get_side(orient: Orientation) -> str:
        return data_to_string(sample_cube.get_side(orient))

    assert get_side(orientation) == "None None None/None None None/None None None"
    assert get_side(orientation.to_right) == "None a b/None None None/None None None"
    assert get_side(orientation.to_top) == "None None b/None None a/None None None"


def test_iterate() -> None:
    def orient_to_str(i: int, j: int, side: Side) -> str:
        return f"{side.name[0].upper()}{i}:{j}"

    cube = Cube((3, 4, 4))
    result = set(map(lambda x: orient_to_str(*x), cube.iterate_components()))
    assert result == {"F0:0", "F0:1", "F0:2", "F1:0", "F1:1", "F1:2", "F2:0", "F2:1", "F2:2", "F3:0", "F3:1", "F3:2",
                      "R0:1", "R0:2", "R1:1", "R1:2", "R2:1", "R2:2", "R3:1", "R3:2",
                      "B0:0", "B0:1", "B0:2", "B1:0", "B1:1", "B1:2", "B2:0", "B2:1", "B2:2", "B3:0", "B3:1", "B3:2",
                      "L0:1", "L0:2", "L1:1", "L1:2", "L2:1", "L2:2", "L3:1", "L3:2",
                      "T1:1", "T2:1", "B1:1", "B2:1"}
