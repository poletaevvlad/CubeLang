from abc import ABC, abstractmethod
from typing import Tuple, List

from .orientation import Color


class ICubeSide(ABC):
    @property
    @abstractmethod
    def rows(self) -> int: pass

    @property
    @abstractmethod
    def columns(self) -> int: pass

    @abstractmethod
    def __getitem__(self, item: Tuple[int, int]) -> Color: pass

    @abstractmethod
    def __setitem__(self, key: Tuple[int, int], value: Color) -> None: pass


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
