from abc import ABC, abstractmethod
from typing import Tuple, List

from .orientation import Color


class ICubeSide(ABC):
    @property
    @abstractmethod
    def rows(self) -> int:
        pass

    @property
    @abstractmethod
    def columns(self) -> int:
        pass

    @abstractmethod
    def __getitem__(self, item: Tuple[int, int]) -> Color:
        pass

    @abstractmethod
    def __setitem__(self, key: Tuple[int, int], value: Color) -> None:
        pass

    def create_view(self, rotation: int) -> "CubeSideView":
        return CubeSideView(self, rotation)

    def rotate(self, amount: int) -> None:
        amount = amount % 4
        if amount == 0:
            return
        elif amount % 2 == 0:
            for i in range(self.rows // 2):
                for j in range(self.columns):
                    i1, i2 = self.rows - 1 - i, self.columns - 1 - j
                    self[i, j], self[i1, i2] = self[i1, i2], self[i, j]
            if self.rows % 2 != 0:
                for j in range(self.columns // 2):
                    i = self.rows // 2
                    self[i, j], self[i, self.columns - i] = self[i, self.columns - i], self[i, j]
        else:
            if self.rows != self.columns:
                raise AttributeError("Cannot rotate a side: it would have different shape after rotation")
            size = self.rows
            for i in range(size // 2):
                for j in range(i, size - 1 - i):
                    indices = [(i, j), (j, size - 1 - i), (size - 1 - i, size - 1 - j), (size - 1 - j, i)]
                    print("a", indices)
                    values = [self[i1, j1] for i1, j1 in indices]

                    if amount == 3:
                        values = values[1:] + [values[0]]
                    else:
                        values = [values[-1]] + values[:-1]
                    for (i1, j1), val in zip(indices, values):
                        self[i1, j1] = val

    def get_row(self, i: int) -> List[Color]:
        return [self[i, j] for j in range(self.columns)]

    def get_column(self, j: int) -> List[Color]:
        return [self[i, j] for i in range(self.rows)]

    def set_row(self, i: int, values: List[Color]) -> None:
        assert len(values) == self.columns
        for j in range(self.columns):
            self[i, j] = values[j]

    def set_column(self, j: int, values: List[Color]) -> None:
        assert len(values) == self.rows
        for i in range(self.rows):
            self[i, j] = values[i]


class CubeSideView(ICubeSide):
    def __init__(self, side: ICubeSide, rotation: int):
        self.side: ICubeSide = side
        self.rotation: int = rotation % 4

    @property
    def rows(self) -> int:
        return self.side.rows if self.rotation % 2 == 0 else self.side.columns

    @property
    def columns(self) -> int:
        return self.side.columns if self.rotation % 2 == 0 else self.side.rows

    def _transform_coord(self, coords: Tuple[int, int]) -> Tuple[int, int]:
        i, j = coords
        if self.rotation == 1 or self.rotation == 2:
            j = self.columns - 1 - j
        if self.rotation >= 2:
            i = self.rows - 1 - i
        return (i, j) if self.rotation % 2 == 0 else (j, i)

    def __getitem__(self, item: Tuple[int, int]) -> Color:
        i, j = self._transform_coord(item)
        return self.side[i, j]

    def __setitem__(self, key: Tuple[int, int], value: Color) -> None:
        i, j = self._transform_coord(key)
        self.side[i, j] = value

    def create_view(self, rotation: int) -> "CubeSideView":
        return CubeSideView(self.side, self.rotation + rotation)


class CubeSide(ICubeSide):
    def __init__(self, rows: int, columns: int, default: Color):
        self.shape = (rows, columns)
        self.items: List[List[Color]] = [[default for _j in range(columns)]
                                         for _i in range(rows)]

    def __getitem__(self, item: Tuple[int, int]) -> Color:
        i, j = item
        return self.items[i][j]

    def __setitem__(self, key: Tuple[int, int], value: Color) -> None:
        i, j = key
        self.items[i][j] = value

    @property
    def rows(self) -> int:
        return self.shape[0]

    @property
    def columns(self) -> int:
        return self.shape[1]
