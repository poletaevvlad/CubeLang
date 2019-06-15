import subprocess
from pathlib import Path
from sys import stdout

import pytest

from libcube.cube import Cube
from libcube.orientation import Orientation, Side
from libcube.parser import parse_actions


def assert_solved(cube: Cube):
    for front in Side:
        face = cube.get_side(Orientation.regular(front))
        color = None
        for row in range(face.rows):
            for column in range(face.columns):
                c = face.colors[row, column]
                if color is None:
                    color = c
                else:
                    assert c == color


def run_test(seed, filename, dimension):
    scramble = subprocess.check_output(
        ["python", "-m", "libcube.scrambler", "-d", str(dimension),
         "-s", str(seed)])

    scramble = scramble.decode(stdout.encoding).strip()

    cube = Cube((dimension, dimension, dimension))
    orientation = Orientation()
    for action in parse_actions(scramble):
        orientation = action.perform(cube, orientation)

    arguments = ["python", "-m", "libcube", "-d", str(dimension),
                 "-s", scramble]
    arguments.append(str(Path(__file__).parents[1] / "examples" / filename))
    solution = subprocess.check_output(arguments).decode("utf-8")

    for action in parse_actions(solution):
        orientation = action.perform(cube, orientation)
    assert_solved(cube)


@pytest.mark.parametrize("seed", range(75))
@pytest.mark.timeout(20)
def test_pocket(seed):
    run_test(seed, "pocket-cube", 2)


@pytest.mark.parametrize("seed", range(75))
@pytest.mark.timeout(20)
def test_beginner(seed, rotations, optimizations):
    run_test(seed, "beginner", 3)
