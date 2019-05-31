from typing import List, Tuple

from ..actions import Action
from ..parser import ParsingError, parse_actions
from ..orientation import Color

import click


def truncate_string_around(value: str, column: int, left_offset: int = 20, right_offset: int = 20,
                           truncation: str = "...") -> Tuple[str, int]:
    assert len(truncation) < left_offset
    assert len(truncation) < right_offset

    if column > left_offset:
        value = truncation + value[column - left_offset + len(truncation):]
        column = left_offset

    if len(value) - column - 1 > right_offset:
        value = value[:column + right_offset - len(truncation) + 1] + truncation

    return value, column


def _get_syntax_error_message(message: str, text: str, position: int):
    text = text.replace("\n", " ").replace("\t", " ")
    value, column = truncate_string_around(text, position)
    return "".join([message, "\n", " " * 7, value, "\n", " " * (7 + column), "^"])


class CubeFormulaParamType(click.ParamType):
    name = "formula"

    def convert(self, value: str, param: str, ctx: click.Context) -> List[Action]:
        try:
            return list(parse_actions(value))
        except ParsingError as e:
            self.fail(_get_syntax_error_message(str(e), value, e.column), param, ctx)


class SideConfigurationType(click.ParamType):
    name = "side"

    SYMBOLS = {"R": Color.RED, "G": Color.GREEN, "B": Color.BLUE,
               "W": Color.WHITE, "Y": Color.YELLOW, "O": Color.ORANGE}

    def convert(self, value: str, param: str, ctx: click.Context) -> List[List[Color]]:
        result: List[List[Color]] = []
        lines = value.upper().split("/")
        position = 0
        for line in lines:
            result_line: List[Color] = []
            if len(line) != len(lines[0]):
                self.fail("Inconsistent line length", param, ctx)
            for symbol in line:
                if symbol not in SideConfigurationType.SYMBOLS:
                    msg = _get_syntax_error_message(f"Unknown color: `{symbol}`", value, position)
                    self.fail(msg, param, ctx)
                else:
                    result_line.append(SideConfigurationType.SYMBOLS[symbol])
                position += 1
            result.append(result_line)
            position += 1
        return result
