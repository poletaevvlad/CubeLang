from typing import Tuple, Dict, List
from .orientation import Side, Color, Orientation
from .sides import CubeSide, ICubeSide, CubeSideView
from .listutils import shift_list


class Cube:
    def __init__(self, shape: Tuple[int, int, int]):
        self.shape: Tuple[int, int, int] = shape
        self.sides: Dict[Side, CubeSide] = {
            Side.FRONT: CubeSide(shape[0], shape[2], Color.RED),
            Side.LEFT: CubeSide(shape[1], shape[2], Color.BLUE),
            Side.BACK: CubeSide(shape[0], shape[2], Color.ORANGE),
            Side.RIGHT: CubeSide(shape[1], shape[2], Color.GREEN),
            Side.TOP: CubeSide(shape[0], shape[1], Color.YELLOW),
            Side.BOTTOM: CubeSide(shape[0], shape[1], Color.WHITE)
        }

    def get_side(self, orientation: Orientation) -> ICubeSide:
        rotation = orientation.get_side_rotation()

        if rotation == 0:
            return self.sides[orientation.front]
        else:
            return CubeSideView(self.sides[orientation.front], rotation)

    @staticmethod
    def _fix_index(index: int, items_count: int):
        if index == 0:
            raise ValueError("index cannot be zero")
        elif abs(index) > items_count:
            raise ValueError(f"An absolute value of index is too large. "
                             f"{items_count} is an upper limit")
        elif index < 0:
            index = items_count + 1 + index
        return index - 1

    def rotate_vertical(self, orientation: Orientation, index: int, turns: int):
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
