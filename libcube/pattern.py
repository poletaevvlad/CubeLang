from typing import List, Union, Dict, Optional, Iterable, Tuple
from .orientation import Color
from .cube import ICubeSide


class PatternGroup:
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, PatternGroup) and other.name == self.name

    def __hash__(self):
        return hash(self.name)


class Pattern:
    def __init__(self, values: List[List[Union[Color, PatternGroup, None]]]):
        self.values = values
        self.rows = len(values)
        self.columns = len(values[0])

    def _get_items(self) -> Iterable[Tuple[int, int, Union[PatternGroup, Color]]]:
        yield from ((row_index, col_index, column)
                    for row_index, row in enumerate(self.values)
                    for col_index, column in enumerate(row)
                    if column is not None)

    def match(self, side: ICubeSide, known: Dict[PatternGroup, Color]) -> \
            Optional[Dict[PatternGroup, Color]]:
        if self.rows != side.rows or self.columns != side.columns:
            return None

        result = dict()
        for row, column, cell in self._get_items():
            color = side.colors[row, column]
            if isinstance(cell, Color):
                if cell != color:
                    return None
            elif (cell in known and known[cell] != color) or (cell in result and result[cell] != color):
                return None
            elif cell not in known:
                result[cell] = color

        return result
