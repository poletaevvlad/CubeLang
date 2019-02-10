import enum


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
    _OPPOSITES = {
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
        Side.BOTTOM: [Side.BACK, Side.LEFT, Side.FRONT, Side.RIGHT]
    }

    def __init__(self, front: Side = Side.FRONT, top: Side = Side.TOP):
        self.front: Side = front
        self.top: Side = top

    @property
    def to_top(self) -> "Orientation":
        return Orientation(self.top, Orientation._OPPOSITES[self.front])

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
        return Orientation(Orientation._OPPOSITES[self.top], self.front)

    def __eq__(self, other):
        return (isinstance(other, Orientation) and
                other.front == self.front and other.top == self.top)

    def __hash__(self):
        return hash((self.front, self.top))
