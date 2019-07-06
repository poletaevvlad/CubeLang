import enum
from typing import Any, Iterable, Optional, Callable, Tuple, TypeVar
from itertools import groupby
from functools import wraps

T = TypeVar("T")


def count_occurrences(seq: Iterable[T]) -> Iterable[Tuple[T, int]]:
    return ((val, sum(1 for _ in group)) for val, group in groupby(seq))


def pipe(g):
    def wrapper(f):
        @wraps(f)
        def function(*args, **kwargs):
            return g(f(*args, **kwargs))
        return function
    return wrapper


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


def _normalize_turns(turns: Iterable[Side]) -> Iterable[Side]:
    for t, count in count_occurrences(turns):
        count = count % 4
        if count == 0:
            continue

        if t not in {Side.RIGHT, Side.TOP, Side.FRONT}:
            count = 4 - count
            t = t.opposite()

        yield from (t for _ in range(count))


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

    def rotate_clockwise(self) -> "Orientation":
        index = (4 + Orientation._RELATIVE_SIDES[self.front].index(self.top) - 1) % 4
        return Orientation(self.front, Orientation._RELATIVE_SIDES[self.front][index])

    def rotate_counterclockwise(self) -> "Orientation":
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

    def _all_turns(self) -> Iterable[Tuple[Side, "Orientation"]]:
        yield Side.TOP, self.to_right
        yield Side.BOTTOM, self.to_left
        yield Side.RIGHT, self.to_bottom
        yield Side.LEFT, self.to_top

    @pipe(_normalize_turns)
    def turns_to(self, other: "Orientation") -> Iterable[Side]:
        orientation = self

        if orientation.front != other.front:
            for new_side, new_orientation in orientation._all_turns():
                if new_orientation.front == other.front:
                    yield new_side
                    orientation = new_orientation
                    break
            else:
                if orientation.to_bottom.front == other.front:
                    yield Side.RIGHT
                    yield Side.RIGHT
                    orientation = orientation.to_top.to_top
                else:
                    yield Side.TOP
                    yield Side.TOP
                    orientation = orientation.to_right.to_right

        while orientation.top != other.top:
            yield Side.FRONT
            orientation = orientation.rotate_clockwise()
        assert orientation == other
