from typing import Tuple
from libcube.orientation import Side, Orientation

import pytest

T = Side.TOP
L = Side.LEFT
R = Side.RIGHT
D = Side.BOTTOM
F = Side.FRONT
B = Side.BACK


@pytest.mark.parametrize("current, left, top, right, bottom", [
    ((F, T), (L, T), (T, B), (R, T), (D, F)),
    ((F, R), (T, R), (R, B), (D, R), (L, F)),
    ((F, D), (R, D), (D, B), (L, D), (T, F)),
    ((F, L), (D, L), (L, B), (T, L), (R, F)),

    ((R, T), (F, T), (T, L), (B, T), (D, R)),
    ((R, B), (T, B), (B, L), (D, B), (F, R)),
    ((R, D), (B, D), (D, L), (F, D), (T, R)),
    ((R, F), (D, F), (F, L), (T, F), (B, R)),

    ((L, T), (B, T), (T, R), (F, T), (D, L)),
    ((L, B), (D, B), (B, R), (T, B), (F, L)),
    ((L, D), (F, D), (D, R), (B, D), (T, L)),
    ((L, F), (T, F), (F, R), (D, F), (B, L)),

    ((B, D), (L, D), (D, F), (R, D), (T, B)),
    ((B, L), (T, L), (L, F), (D, L), (R, B)),
    ((B, T), (R, T), (T, F), (L, T), (D, B)),
    ((B, R), (D, R), (R, F), (T, R), (L, B)),

    ((T, B), (L, B), (B, D), (R, B), (F, T)),
    ((T, L), (F, L), (L, D), (B, L), (R, T)),
    ((T, R), (B, R), (R, D), (F, R), (L, T)),
    ((T, F), (R, F), (F, D), (L, F), (B, T)),

    ((D, B), (R, B), (B, T), (L, B), (F, D)),
    ((D, L), (B, L), (L, T), (F, L), (R, D)),
    ((D, R), (F, R), (R, T), (B, R), (L, D)),
    ((D, F), (L, F), (F, T), (R, F), (B, D))
])
def test_rotations(current: Tuple[Side, Side], left: Tuple[Side, Side],
                   top: Tuple[Side, Side], right: Tuple[Side, Side],
                   bottom: Tuple[Side, Side]) -> None:
    current_orientation = Orientation(*current)

    assert current_orientation.to_top.front == top[0]
    assert current_orientation.to_top.top == top[1]

    assert current_orientation.to_right.front == right[0]
    assert current_orientation.to_right.top == right[1]

    assert current_orientation.to_bottom.front == bottom[0]
    assert current_orientation.to_bottom.top == bottom[1]

    assert current_orientation.to_left.front == left[0]
    assert current_orientation.to_left.top == left[1]


@pytest.mark.parametrize("front, top, rotation", [
    (F, T, 0), (F, R, 1), (F, D, 2), (F, L, 3),
    (R, T, 0), (R, B, 1), (R, D, 2), (R, F, 3),
    (B, T, 0), (B, L, 1), (B, D, 2), (B, R, 3),
    (L, T, 0), (L, F, 1), (L, D, 2), (L, B, 3),
    (T, B, 0), (T, R, 1), (T, F, 2), (T, L, 3),
    (D, L, 0), (D, F, 1), (D, R, 2), (D, B, 3)
])
def test_get_side_rotation(front: Side, top: Side, rotation: int):
    orientation = Orientation(front, top)
    assert orientation.get_side_rotation() == rotation


rotations = [
    (F, T, [R, D, L]),
    (R, T, [B, D, F]),
    (B, T, [L, D, R]),
    (L, T, [F, D, B]),
    (T, R, [F, L, B]),
    (D, L, [F, R, B])
]


@pytest.mark.parametrize("front, top, after_rotation", rotations)
def test_rotation_clockwise(front, top, after_rotation):
    orientation = Orientation(front, top).rotate_clockwise()
    for after_top in after_rotation:
        assert orientation.top == after_top
        orientation = orientation.rotate_clockwise()
    assert orientation.top == top


@pytest.mark.parametrize("front, top, after_rotation", rotations)
def test_rotation_counter_clockwise(front, top, after_rotation):
    orientation = Orientation(front, top).rotate_counterclockwise()
    for after_top in after_rotation[::-1]:
        assert orientation.top == after_top
        orientation = orientation.rotate_counterclockwise()
    assert orientation.top == top
