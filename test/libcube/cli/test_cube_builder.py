from libcube.cube import Cube
from libcube.orientation import Orientation, Side, Color
from libcube.cli.cube_builder import apply_side
from click import BadOptionUsage
from pytest import raises


class TestApplySide:
    orientation = Orientation(Side.RIGHT, Side.BOTTOM)

    def test_apply_side(self):
        cube = Cube((2, 2, 2))
        colors = [[Color.WHITE, Color.RED], [Color.ORANGE, Color.GREEN]]

        apply_side(cube, self.orientation, colors, "test")
        actual_colors = [[cube.get_side(self.orientation).colors[i, j] for j in [0, 1]] for i in [0, 1]]
        assert colors == actual_colors

    def test_wrong_columns(self):
        cube = Cube((2, 2, 2))
        colors = [[Color.WHITE, Color.RED, Color.BLUE], [Color.ORANGE, Color.GREEN, Color.BLUE]]
        with raises(BadOptionUsage) as e:
            apply_side(cube, self.orientation, colors, "test")
        assert str(e.value) == """Invalid value for "--test": Incorrect number of columns"""

    def test_wrong_lines(self):
        cube = Cube((2, 2, 2))
        colors = [[Color.WHITE, Color.RED]]
        with raises(BadOptionUsage) as e:
            apply_side(cube, self.orientation, colors, "test")
        assert str(e.value) == """Invalid value for "--test": Incorrect number of lines"""
