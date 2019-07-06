from typing import List, Tuple, TypeVar, Dict

from ..actions import Action
from ..parser import ParsingError, parse_actions
from ..orientation import Color

from argparse import ArgumentTypeError

T = TypeVar("T")


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


def integer_type(min_value: int):
    def type(value: str):
        try:
            val = int(value)
            if val < min_value:
                raise ArgumentTypeError(f"the minimum value is {min_value}")
            return val
        except ValueError:
            raise ArgumentTypeError(f"invalid integer value: '{value}'")
    return type


def dict_type(dictionary: Dict[str, T]):
    def type(value: str) -> T:
        if value in dictionary:
            return dictionary[value]
        else:
            keys = list(dictionary.keys())
            values = ", ".join(f"'{x}'" for x in keys[:-1]) + f" or '{keys[-1]}'"
            raise ArgumentTypeError(f"unknown value: '{value}'; expected either {values}")
    return type


def formula_type(value: str) -> List[Action]:
    try:
        return list(parse_actions(value))
    except ParsingError as e:
        raise ArgumentTypeError(_get_syntax_error_message(str(e), value, e.column))


SYMBOLS = {"R": Color.RED, "G": Color.GREEN, "B": Color.BLUE,
           "W": Color.WHITE, "Y": Color.YELLOW, "O": Color.ORANGE}


def side_colors_type(value: str):
    result: List[List[Color]] = []
    lines = value.upper().split("/")
    position = 0
    for line in lines:
        result_line: List[Color] = []
        if len(line) != len(lines[0]):
            raise ArgumentTypeError("inconsistent line length")
        for symbol in line:
            if symbol not in SYMBOLS:
                msg = _get_syntax_error_message(f"unknown color: `{symbol}`", value, position)
                raise ArgumentTypeError(msg)
            else:
                result_line.append(SYMBOLS[symbol])
            position += 1
        result.append(result_line)
        position += 1
    return result


def file_contents_type(value: str):
    try:
        with open(value) as file:
            return file.read()
    except IOError as e:
        raise ArgumentTypeError(f"cannot open a file: {e}")
