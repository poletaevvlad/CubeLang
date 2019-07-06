from typing import List, Union, Dict, Optional, Iterable, Tuple
from .orientation import Color
from .cube import ICubeSide


class Pattern:
    _COLOR_CHARS = {"R": Color.RED, "G": Color.GREEN, "B": Color.BLUE,
                    "W": Color.WHITE, "O": Color.ORANGE, "Y": Color.YELLOW}

    def __init__(self, values: List[List[Union[Color, str, None]]]):
        self.values = values
        self.rows = len(values)
        self.columns = len(values[0])

    def _get_items(self) -> Iterable[Tuple[int, int, Union[str, Color]]]:
        yield from ((row_index, col_index, column)
                    for row_index, row in enumerate(self.values)
                    for col_index, column in enumerate(row)
                    if column is not None)

    def match(self, side: ICubeSide, known: Dict[str, Color]) -> \
            Optional[Dict[str, Color]]:
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
                if color in known.values() or (color in result.values() and result.get(cell, None) != color):
                    return None
                result[cell] = color

        return result
