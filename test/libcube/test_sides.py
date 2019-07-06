from cubelang.sides import CubeSide, ICubeSide, CubeSideView, Component
from cubelang.orientation import Color

import pytest


def side_to_string(side: ICubeSide):
    out = []
    for i in range(side.rows):
        for j in range(side.columns):
            color = side.colors[i, j].name[0].upper()
            out.append(color)
        out.append("/")
    return "".join(out[:-1])


def create_side(rows: int, columns: int, items: str):
    colors = {
        "Y": Color.YELLOW,
        "W": Color.WHITE,
        "R": Color.RED,
        "O": Color.ORANGE,
        "B": Color.BLUE,
        "G": Color.GREEN
    }

    side = CubeSide(rows, columns, Color.RED)
    for i, row in enumerate(items.split("/")):
        for j, char in enumerate(row):
            side.colors[i, j] = colors[char]
    return side


@pytest.mark.parametrize("rotation, expected, rows, columns", [
    [-1, "RO/GB/YW", 3, 2],
    [0, "RO/GB/YW", 3, 2],
    [1, "OBW/RGY", 2, 3],
    [2, "WY/BG/OR", 3, 2],
    [3, "YGR/WBO", 2, 3],
])
def test_get_set(rotation: int, expected: str, rows: int, columns: int) -> None:
    side = create_side(3, 2, "RO/GB/YW")
    if rotation >= 0:
        side = CubeSideView(side, rotation)
    assert side.rows == rows
    assert side.columns == columns
    assert side_to_string(side) == expected


def test_rotation_illegal():
    with pytest.raises(Exception):
        side = create_side(2, 3, "YWB/OBG")
        side.rotate(1)


@pytest.mark.parametrize("width, height, items, amount, expected", [
    [2, 3, "YWR/OBG", 2, "GBO/RWY"],
    [3, 3, "GBO/RWY/OWB", 1, "ORG/WWB/BYO"],
    [3, 3, "GBO/RWY/OWB", 2, "BWO/YWR/OBG"],
    [3, 3, "GBO/RWY/OWB", 3, "OYB/BWW/GRO"],
    [4, 4, "YOBG/RWYR/OBBY/GBRW", 3, "GRYW/BYBR/OWBB/YROG"],
    [4, 4, "YOBG/RWYR/OBBY/GBRW", 1, "GORY/BBWO/RBYB/WYRG"]
])
def test_rotation(width: int, height: int, items: str, amount: int, expected: str):
    side = create_side(width, height, items)
    side.rotate(amount)
    assert side_to_string(side) == expected


def test_get_row():
    side = create_side(4, 4, "YOBG/RWYR/OBBY/GBRW")
    assert (list(map(lambda x: x.color, side.get_row(1))) ==
            [Color.RED, Color.WHITE, Color.YELLOW, Color.RED])


def test_get_column():
    side = create_side(4, 4, "YOBG/RWYR/OBBY/GBRW")
    assert (list(map(lambda x: x.color, side.get_column(1))) ==
            [Color.ORANGE, Color.WHITE, Color.BLUE, Color.BLUE])


def test_set_row():
    side = create_side(4, 4, "YOBG/RWYR/OBBY/GBRW")
    side.set_row(1, list(map(lambda c: Component[None](c, None),
                             [Color.BLUE, Color.RED, Color.GREEN, Color.YELLOW])))
    assert side_to_string(side) == "YOBG/BRGY/OBBY/GBRW"


def test_set_column():
    side = create_side(4, 4, "YOBG/RWYR/OBBY/GBRW")
    side.set_column(1, list(map(lambda c: Component[None](c, None),
                                [Color.BLUE, Color.RED, Color.GREEN, Color.YELLOW])))
    assert side_to_string(side) == "YBBG/RRYR/OGBY/GYRW"
