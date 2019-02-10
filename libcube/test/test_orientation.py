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
