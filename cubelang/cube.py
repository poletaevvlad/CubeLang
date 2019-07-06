from typing import Tuple, Dict, List, Generic, TypeVar, Iterator, Optional
from .orientation import Side, Color, Orientation
from .sides import CubeSide, ICubeSide, CubeSideView
from .pattern import Pattern

T = TypeVar("T")


def shift_list(list: List[T], amount: int = 1) -> List[T]:
    return list[amount:] + list[:amount]


class Cube(Generic[T]):
    def __init__(self, shape: Tuple[int, int, int]):
        self.shape: Tuple[int, int, int] = shape
        self.sides: Dict[Side, CubeSide[T]] = {
            Side.FRONT: CubeSide[T](shape[0], shape[2], Color.RED),
            Side.LEFT: CubeSide[T](shape[1], shape[2], Color.BLUE),
            Side.BACK: CubeSide[T](shape[0], shape[2], Color.ORANGE),
            Side.RIGHT: CubeSide[T](shape[1], shape[2], Color.GREEN),
            Side.TOP: CubeSide[T](shape[0], shape[1], Color.YELLOW),
            Side.BOTTOM: CubeSide[T](shape[0], shape[1], Color.WHITE)
        }

    def get_side(self, orientation: Orientation) -> ICubeSide[T]:
        rotation = orientation.get_side_rotation()

        if rotation == 0:
            return self.sides[orientation.front]
        else:
            return CubeSideView(self.sides[orientation.front], rotation)

    @staticmethod
    def _fix_index(index: int, items_count: int) -> int:
        if index == 0:
            raise ValueError("index cannot be zero")
        elif abs(index) > items_count:
            raise ValueError(f"An absolute value of index is too large. "
                             f"{items_count} is an upper limit")
        elif index < 0:
            index = items_count + 1 + index
        return index - 1

    def turn_vertical(self, orientation: Orientation, index: int, turns: int) -> None:
        faces: List[ICubeSide] = []
        for i in range(4):
            faces.append(self.get_side(orientation))
            orientation = orientation.to_top

        index = self._fix_index(index, faces[0].columns)
        columns = [face.get_column(index) for face in faces]
        columns = shift_list(columns, 4 - turns)
        for face, column in zip(faces, columns):
            face.set_column(index, column)

        if index == 0:
            left_face = self.get_side(orientation.to_left)
            left_face.rotate(4 - turns)
        elif index == faces[0].columns - 1:
            right_face = self.get_side(orientation.to_right)
            right_face.rotate(turns)

    def turn_horizontal(self, orientation: Orientation, index: int, turns: int) -> None:
        orientation = orientation.rotate_counterclockwise()
        self.turn_vertical(orientation, index, turns)

    def turn_slice(self, orientation: Orientation, index: int, turns: int) -> None:
        orientation = orientation.to_right
        self.turn_vertical(orientation, index, 4 - turns)

    def get_data(self, orientation: Orientation, i: int, j: int) -> Optional[T]:
        return self.get_side(orientation)[i, j].data

    def set_data(self, orientation: Orientation, i: int, j: int, value: Optional[T]) -> None:
        front = self.get_side(orientation)
        front[i, j].data = value

        if j == 0:
            left = self.get_side(orientation.to_left)
            left[i, left.columns - 1].data = value
        elif j == front.columns - 1:
            right = self.get_side(orientation.to_right)
            right[i, 0].data = value

        if i == 0:
            top = self.get_side(orientation.to_top)
            top[top.rows - 1, j].data = value
        elif i == front.rows - 1:
            bottom = self.get_side(orientation.to_bottom)
            bottom[0, j].data = value

    def iterate_components(self) -> Iterator[Tuple[Side, int, int]]:
        for i in range(self.shape[2]):
            for j in range(self.shape[0]):
                yield Side.FRONT, i, j
                yield Side.BACK, i, j

        for j in range(1, self.shape[1] - 1):
            for i in range(1, self.shape[0] - 1):
                yield Side.TOP, j, i,
                yield Side.BOTTOM, j, i

            for k in range(self.shape[2]):
                yield Side.LEFT, k, j
                yield Side.RIGHT, k, j

    def get_absolute_coordinates(self, side: Side, i: int, j: int) -> Tuple[int, int, int]:
        if side == Side.FRONT:
            return j, i, 0
        elif side == Side.RIGHT:
            return self.shape[0] - 1, i, j
        elif side == Side.BACK:
            return self.shape[0] - 1 - j, i, self.shape[1] - 1
        elif side == Side.LEFT:
            return 0, i, self.shape[1] - 1 - j
        elif side == Side.TOP:
            return j, 0, self.shape[1] - 1 - i
        elif side == Side.BOTTOM:
            return j, self.shape[2] - 1, i
        raise ValueError("Unknown value for `side` argument")

    def orient(self, orientation: Orientation, keeping: Optional[Side] = None,
               front: Optional[Pattern] = None, top: Optional[Pattern] = None,
               left: Optional[Pattern] = None, right: Optional[Pattern] = None,
               back: Optional[Pattern] = None, bottom: Optional[Pattern] = None) -> Optional[Orientation]:
        def match(pattern: Optional[Pattern], front_orientation: Orientation, values: Dict) -> bool:
            if pattern is None:
                return True
            new_values = pattern.match(self.get_side(front_orientation), values)
            if new_values is None:
                return False
            for key in new_values:
                if key in values and values[key] != new_values[key]:
                    return False
            values.update(new_values)
            return True

        def perform_matching(new_front):
            values = {}
            yield match(front, new_front, values)
            yield match(top, new_front.to_top, values)
            yield match(left, new_front.to_left, values)
            yield match(right, new_front.to_right, values)
            yield match(bottom, new_front.to_bottom, values)
            yield match(back, new_front.to_left.to_left, values)

        for possible_front in orientation.iterate_rotations(keeping):
            if all(perform_matching(possible_front)):
                return possible_front
        else:
            return None
