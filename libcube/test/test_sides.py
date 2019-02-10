from libcube.sides import CubeSide, ICubeSide, CubeSideView
from libcube.orientation import Color

import pytest


def side_to_string(side: ICubeSide):
    out = []
    for i in range(side.rows):
        for j in range(side.columns):
            color = side[i, j].name[0].upper()
            out.append(color)
        out.append("/")
    return "".join(out[:-1])


@pytest.mark.parametrize("rotation, expected, rows, columns", [
    [-1, "RO/GB/YW", 3, 2], [0, "RO/GB/YW", 3, 2], [1, "YGR/WBO", 2, 3],
    [2, "WY/BG/OR", 3, 2], [3, "OBW/RGY", 2, 3]
])
def test_get_set(rotation: int, expected: str, rows: int, columns: int) -> None:
    side = CubeSide(3, 2, Color.RED)
    side[0, 0] = Color.RED
    side[0, 1] = Color.ORANGE
    side[1, 0] = Color.GREEN
    side[1, 1] = Color.BLUE
    side[2, 0] = Color.YELLOW
    side[2, 1] = Color.WHITE

    if rotation >= 0:
        side = CubeSideView(side, rotation)
    assert side.rows == rows
    assert side.columns == columns
    assert side_to_string(side) == expected
