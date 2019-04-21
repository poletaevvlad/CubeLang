import enum
from typing import Any


class Color (enum.Enum):
    RED = enum.auto()
    BLUE = enum.auto()
    YELLOW = enum.auto()
    WHITE = enum.auto()
    GREEN = enum.auto()
    ORANGE = enum.auto()


class Side (enum.Enum):
    FRONT = enum.auto()
    BACK = enum.auto()
    LEFT = enum.auto()
    RIGHT = enum.auto()
    TOP = enum.auto()
    BOTTOM = enum.auto()


class Orientation:
    OPPOSITES = {
        Side.LEFT: Side.RIGHT, Side.RIGHT: Side.LEFT,
        Side.TOP: Side.BOTTOM, Side.BOTTOM: Side.TOP,
        Side.FRONT: Side.BACK, Side.BACK: Side.FRONT
    }

    _RELATIVE_SIDES = {
        Side.FRONT: [Side.TOP, Side.RIGHT, Side.BOTTOM, Side.LEFT],
        Side.LEFT: [Side.TOP, Side.FRONT, Side.BOTTOM, Side.BACK],
        Side.BACK: [Side.TOP, Side.LEFT, Side.BOTTOM, Side.RIGHT],
        Side.RIGHT: [Side.TOP, Side.BACK, Side.BOTTOM, Side.FRONT],
        Side.TOP: [Side.BACK, Side.RIGHT, Side.FRONT, Side.LEFT],
        Side.BOTTOM: [Side.LEFT, Side.FRONT, Side.RIGHT, Side.BACK]
    }

    def __init__(self, front: Side = Side.FRONT, top: Side = Side.TOP) -> None:
        self.front: Side = front
        self.top: Side = top

    @property
    def to_top(self) -> "Orientation":
        return Orientation(self.top, Orientation.OPPOSITES[self.front])

    @property
    def to_left(self) -> "Orientation":
        index = Orientation._RELATIVE_SIDES[self.front].index(self.top)
        index = (4 + index - 1) % 4
        return Orientation(Orientation._RELATIVE_SIDES[self.front][index], self.top)

    @property
    def to_right(self) -> "Orientation":
        index = Orientation._RELATIVE_SIDES[self.front].index(self.top)
        index = (4 + index + 1) % 4
        return Orientation(Orientation._RELATIVE_SIDES[self.front][index], self.top)

    @property
    def to_bottom(self) -> "Orientation":
        return Orientation(Orientation.OPPOSITES[self.top], self.front)

    def get_side_rotation(self) -> int:
        return Orientation._RELATIVE_SIDES[self.front].index(self.top)

    def __eq__(self, other: Any) -> bool:
        return (isinstance(other, Orientation) and
                other.front == self.front and other.top == self.top)

    def __hash__(self) -> int:
        return hash((self.front, self.top))

    def rotate_counterclockwise(self) -> "Orientation":
        index = (4 + Orientation._RELATIVE_SIDES[self.front].index(self.top) - 1) % 4
        return Orientation(self.front, Orientation._RELATIVE_SIDES[self.front][index])

    def rotate_clockwise(self) -> "Orientation":
        index = (Orientation._RELATIVE_SIDES[self.front].index(self.top) + 1) % 4
        return Orientation(self.front, Orientation._RELATIVE_SIDES[self.front][index])

    def __repr__(self) -> str:
        return f"Orientation(front={repr(self.front)}, top={repr(self.top)})"

    @classmethod
    def regular(cls, side: Side) -> "Orientation":
        if side == Side.BOTTOM:
            return Orientation(side, Side.FRONT)
        else:
            return Orientation(side, Orientation._RELATIVE_SIDES[side][0])
