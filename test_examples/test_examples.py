import subprocess
from pathlib import Path
from sys import stdout

import pytest

from libcube.cube import Cube
from libcube.orientation import Orientation, Side
from libcube.parser import parse_actions


FILES = [("beginner", 3), ("pocket-cube", 2)]


def generate_tests():
    for seed in range(50):
        for file in FILES:
            yield (seed, *file, True, True)
            yield (seed, *file, False, True)
            yield (seed, *file, True, False)
            yield (seed, *file, False, False)


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


@pytest.mark.parametrize("seed, filename, dimension, rotations, optimizations",
                         list(generate_tests()))
def test_example(seed, filename, dimension, rotations, optimizations):
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
    if not rotations:
        arguments.append("-r")
    if not optimizations:
        arguments.append("-o")

    arguments.append(str(Path(__file__).parents[1] / "examples" / filename))
    solution = subprocess.check_output(arguments).decode("utf-8")

    for action in parse_actions(solution):
        orientation = action.perform(cube, orientation)
    assert_solved(cube)
