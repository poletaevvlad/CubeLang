from abc import ABC, abstractmethod
from typing import Tuple, List, Generic, TypeVar, Optional

from .orientation import Color

T = TypeVar("T")


class Component(Generic[T]):
    def __init__(self, color: Color, data: Optional[T]) -> None:
        self.color: Color = color
        self.data: Optional[T] = data

    def __repr__(self) -> str:
        return f"Component({self.color}, {self.data})"


class ICubeSide(ABC, Generic[T]):
    def __init__(self) -> None:
        self.colors = ColorsAccessor(self)

    @property
    @abstractmethod
    def rows(self) -> int:
        pass

    @property
    @abstractmethod
    def columns(self) -> int:
        pass

    @abstractmethod
    def __getitem__(self, item: Tuple[int, int]) -> Component[T]:
        pass

    @abstractmethod
    def __setitem__(self, key: Tuple[int, int], value: Component[T]) -> None:
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
                    values = [self[i1, j1] for i1, j1 in indices]

                    if amount == 3:
                        values = values[1:] + [values[0]]
                    else:
                        values = [values[-1]] + values[:-1]
                    for (i1, j1), val in zip(indices, values):
                        self[i1, j1] = val

    def get_row(self, i: int) -> List[Component[T]]:
        return [self[i, j] for j in range(self.columns)]

    def get_column(self, j: int) -> List[Component[T]]:
        return [self[i, j] for i in range(self.rows)]

    def set_row(self, i: int, values: List[Component[T]]) -> None:
        assert len(values) == self.columns
        for j in range(self.columns):
            self[i, j] = values[j]

    def set_column(self, j: int, values: List[Component[T]]) -> None:
        assert len(values) == self.rows
        for i in range(self.rows):
            self[i, j] = values[i]

    def __repr__(self) -> str:
        content = "/".join(
            ", ".join(f"{self[r, c].color.name[0]}({self[r, c].data})" for c in range(self.columns))
            for r in range(self.rows))
        return f"<Side: {content}>"


class ColorsAccessor(Generic[T]):
    def __init__(self, side: ICubeSide[T]) -> None:
        self.side: ICubeSide[T] = side

    def __repr__(self):
        return "/".join("".join(self[i, j].name[0] for j in range(self.side.columns))
                        for i in range(self.side.rows))

    def __getitem__(self, item: Tuple[int, int]) -> Color:
        return self.side[item].color

    def __setitem__(self, key: Tuple[int, int], value: Color) -> None:
        self.side[key].color = value


class CubeSideView(ICubeSide[T]):
    def __init__(self, side: ICubeSide, rotation: int) -> None:
        super().__init__()
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
        if self.rotation == 1:
            return j, self.side.columns - 1 - i
        elif self.rotation == 2:
            return self.side.rows - 1 - i, self.side.columns - 1 - j
        elif self.rotation == 3:
            return self.side.rows - 1 - j, i
        else:
            return i, j

    def __getitem__(self, item: Tuple[int, int]) -> Component[T]:
        i, j = self._transform_coord(item)
        return self.side[i, j]

    def __setitem__(self, key: Tuple[int, int], value: Component[T]) -> None:
        i, j = self._transform_coord(key)
        self.side[i, j] = value


class CubeSide(ICubeSide[T]):
    def __init__(self, rows: int, columns: int, default: Color):
        super().__init__()
        self.shape = (rows, columns)
        self.items: List[List[Component[T]]] = [[Component[T](default, None) for _j in range(columns)]
                                                for _i in range(rows)]

    def __getitem__(self, item: Tuple[int, int]) -> Component[T]:
        i, j = item
        return self.items[i][j]

    def __setitem__(self, key: Tuple[int, int], value: Component[T]) -> None:
        i, j = key
        self.items[i][j] = value

    @property
    def rows(self) -> int:
        return self.shape[0]

    @property
    def columns(self) -> int:
        return self.shape[1]
