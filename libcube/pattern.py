from typing import List, Union, Dict, Optional, Iterable, Tuple
from .orientation import Color
from .cube import ICubeSide
import string


class PatternGroup:
    pass


class Pattern:
    _COLOR_CHARS = {"R": Color.RED, "G": Color.GREEN, "B": Color.BLUE,
                    "W": Color.WHITE, "O": Color.ORANGE, "Y": Color.YELLOW}

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

    @staticmethod
    def parse(pattern: str) -> "Pattern":
        lines = pattern.split("/")
        columns = len(lines[0])

        groups: Dict[str, PatternGroup] = dict()
        out_lines = []
        for line in lines:
            out_line = []
            if len(line) != columns:
                raise ValueError("Inconsistent line lengths")
            for char in line:
                if char in string.ascii_lowercase:
                    if char in groups:
                        group = groups[char]
                    else:
                        group = PatternGroup()
                        groups[char] = group
                    out_line.append(group)
                elif char == "-":
                    out_line.append(None)
                elif char in Pattern._COLOR_CHARS:
                    out_line.append(Pattern._COLOR_CHARS[char])
                else:
                    raise ValueError(f"Unnown character in pattern: '{char}'")

            out_lines.append(out_line)
        return Pattern(out_lines)
