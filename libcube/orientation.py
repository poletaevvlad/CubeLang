import enum
from typing import Any, Iterable, Optional, Callable


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

    def opposite(self):
        opposites = {Side.LEFT: Side.RIGHT, Side.RIGHT: Side.LEFT,
                     Side.TOP: Side.BOTTOM, Side.BOTTOM: Side.TOP,
                     Side.FRONT: Side.BACK, Side.BACK: Side.FRONT}
        return opposites[self]


class Orientation:
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
        return Orientation(self.top, self.front.opposite())

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
        return Orientation(self.top.opposite(), self.front)

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

    def iterate_rotations(self, keeping: Optional[Side] = None) -> Iterable["Orientation"]:
        def orientation_changes(orientation: Orientation, action: Callable[[Orientation], Orientation]):
            for _ in range(4):
                yield orientation
                orientation = action(orientation)

        def iterate_cube_rotations() -> Iterable["Orientation"]:
            if keeping == Side.FRONT or keeping == Side.BACK:
                yield from orientation_changes(self, lambda x: x.rotate_clockwise())
            elif keeping == Side.LEFT or keeping == Side.RIGHT:
                yield from orientation_changes(self, lambda x: x.to_top)
            else:
                yield from orientation_changes(self, lambda x: x.to_left)
            if keeping is None:
                yield self.to_top
                yield self.to_bottom

        if keeping is not None:
            yield from iterate_cube_rotations()
        else:
            for rotation in iterate_cube_rotations():
                yield from orientation_changes(rotation, lambda x: x.rotate_clockwise())

    def turns_to_origin(self) -> Iterable[Side]:
        def perform_top():
            if self.top == Side.LEFT:
                yield Side.BACK
            elif self.top == Side.RIGHT:
                yield Side.FRONT
            elif self.top == Side.BACK:
                yield Side.FRONT
                yield Side.FRONT
            yield Side.RIGHT

        if self.front == Side.TOP:
            yield from perform_top()
        elif self.front == Side.BOTTOM:
            yield from (x.opposite() for x in perform_top())
        else:
            if self.top == Side.BOTTOM:
                yield Side.FRONT
                yield Side.FRONT
            elif self.top != Side.TOP:
                if self.to_left.top == Side.TOP:
                    yield Side.FRONT
                else:
                    yield Side.BACK
            if self.front == Side.RIGHT:
                yield Side.BOTTOM
            elif self.front == Side.LEFT:
                yield Side.TOP
            elif self.front == Side.BACK:
                yield Side.TOP
                yield Side.TOP
