from typing import Tuple, Dict, List, Generic, TypeVar, Iterator
from .orientation import Side, Color, Orientation
from .sides import CubeSide, ICubeSide, CubeSideView
from .listutils import shift_list

T = TypeVar("T")


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

    def rotate_vertical(self, orientation: Orientation, index: int, turns: int) -> None:
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

    def rotate_horizontal(self, orientation: Orientation, index: int, turns: int) -> None:
        orientation = orientation.rotate_clockwise()
        return self.rotate_vertical(orientation, index, turns)

    def rotate_slice(self, orientation: Orientation, index: int, turns: int) -> None:
        orientation = orientation.to_right
        return self.rotate_vertical(orientation, index, 4 - turns)

    def get_data(self, orientation: Orientation, i: int, j: int) -> T:
        return self.get_side(orientation)[i, j].data

    def set_data(self, orientation: Orientation, i: int, j: int, value: T) -> None:
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
