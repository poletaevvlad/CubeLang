from libcube.actions import Action
from libcube.cube import Cube
from libcube.orientation import Orientation, Side, Color
from libcube.cli.cube_builder import apply_side, CubeBuilder
from pytest import raises
from unittest import mock
import pytest
import string
import argparse
from typing import List


class TestApplySide:
    orientation = Orientation(Side.RIGHT, Side.BOTTOM)

    def test_apply_side(self):
        cube = Cube((2, 2, 2))
        colors = [[Color.WHITE, Color.RED], [Color.ORANGE, Color.GREEN]]

        apply_side(cube, self.orientation, colors)
        actual_colors = [[cube.get_side(self.orientation).colors[i, j] for j in [0, 1]] for i in [0, 1]]
        assert colors == actual_colors

    def test_wrong_columns(self):
        cube = Cube((2, 2, 2))
        colors = [[Color.WHITE, Color.RED, Color.BLUE], [Color.ORANGE, Color.GREEN, Color.BLUE]]
        with raises(argparse.ArgumentTypeError) as e:
            apply_side(cube, self.orientation, colors)
        assert str(e.value) == "Incorrect number of columns"

    def test_wrong_lines(self):
        cube = Cube((2, 2, 2))
        colors = [[Color.WHITE, Color.RED]]
        with raises(argparse.ArgumentTypeError) as e:
            apply_side(cube, self.orientation, colors)
        assert str(e.value) == "Incorrect number of lines"


class MockAction (Action):
    def __init__(self, results: List[str], name: str):
        self.results = results
        self.name = name

    def perform(self, cube: Cube, orientation: Orientation) -> Orientation:
        self.results.append(self.name)
        return Orientation(Side.LEFT, Side.RIGHT)


class TestBuilder:
    def test_create(self):
        builder = CubeBuilder((2, 2, 2))
        cube, orientation = builder.get()
        assert cube.shape == (2, 2, 2)
        assert orientation.top == Side.TOP
        assert orientation.front == Side.FRONT

    @mock.patch("libcube.cli.cube_builder.apply_side")
    @pytest.mark.parametrize("side, exp_orientation", [
        (Side.FRONT, Orientation(Side.FRONT, Side.TOP)),
        (Side.LEFT, Orientation(Side.LEFT, Side.TOP)),
        (Side.RIGHT, Orientation(Side.RIGHT, Side.TOP)),
        (Side.BACK, Orientation(Side.BACK, Side.TOP)),
        (Side.TOP, Orientation(Side.TOP, Side.BACK)),
        (Side.BOTTOM, Orientation(Side.BOTTOM, Side.FRONT))
    ])
    def test_side(self, apply_side_fn, side, exp_orientation):
        builder = CubeBuilder((2, 2, 2))
        builder.side(side, [])
        apply_side_fn.assert_called_once_with(builder.cube, exp_orientation, [])

    def test_scramble(self):
        result = []
        actions = [MockAction(result, string.ascii_uppercase[i]) for i in range(10)]

        builder = CubeBuilder((2, 2, 2))
        builder.scramble(actions)
        _, orientation = builder.get()

        assert orientation == Orientation(Side.LEFT, Side.RIGHT)
        assert result == list("ABCDEFGHIJ")
