from libcube.cube import Cube
from libcube.sides import CubeSide, CubeSideView
from libcube.orientation import Orientation, Side

from unittest.mock import MagicMock


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
