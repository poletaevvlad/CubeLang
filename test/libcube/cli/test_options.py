from string import ascii_lowercase
import pytest
import argparse
from libcube.cli.options import truncate_string_around, dimension_type, \
    side_colors_type, formula_type
from libcube.parser import ParsingError
from unittest import mock

from libcube.orientation import Color


@pytest.mark.parametrize("position, expected", [
    (3, ("abcdefg~~", 3)),
    (4, ("abcdefgh~~", 4)),
    (5, ("abcdefghi~~", 5)),
    (6, ("~~defghij~~", 5)),

    (19, ("~~qrstuvw~~", 5)),
    (20, ("~~rstuvwxyz", 5)),
    (21, ("~~stuvwxyz", 5))
])
def test_truncation(position, expected):
    result = truncate_string_around(ascii_lowercase, position, 5, 5, "~~")
    assert expected == result


class TestDimensionType:
    def test_normal(self):
        assert dimension_type("2") == 2

    def test_invalid(self):
        with pytest.raises(argparse.ArgumentTypeError) as e:
            dimension_type("abc")
        assert str(e.value) == "`abc` is not an integer"

    def test_too_small(self):
        with pytest.raises(argparse.ArgumentTypeError) as e:
            dimension_type("1")
        assert str(e.value) == "Cube's dimension must be greater or equal two"


class TestFormulaParam:
    @mock.patch("libcube.cli.options.parse_actions", return_value=iter([1, 2, 3]))
    def test_correct(self, parse_actions_function):
        actual = formula_type("abcdef")
        assert actual == [1, 2, 3]
        parse_actions_function.assert_called_once_with("abcdef")

    @mock.patch("libcube.cli.options.parse_actions", side_effect=ParsingError("~~test error~~", 10))
    @mock.patch("libcube.cli.options.truncate_string_around", return_value=("~~rendered~~", 4))
    def test_invalid_syntax(self, _1, _2):
        with pytest.raises(argparse.ArgumentTypeError) as e:
            formula_type(ascii_lowercase)

        assert str(e.value) == "~~test error~~\n       ~~rendered~~\n           ^"


class TestSideConfiguration:
    def test_valid(self):
        actual = side_colors_type("RRO/GGY/BBW")
        assert actual == [[Color.RED, Color.RED, Color.ORANGE],
                          [Color.GREEN, Color.GREEN, Color.YELLOW],
                          [Color.BLUE, Color.BLUE, Color.WHITE]]

    @mock.patch("libcube.cli.options.truncate_string_around", return_value=("~~rendered~~", 4))
    def test_wrong_symbol(self, truncate_fn: mock.MagicMock):
        with pytest.raises(argparse.ArgumentTypeError) as e:
            side_colors_type("RRO/GGM/BBW")

        assert str(e.value) == "Unknown color: `M`\n       ~~rendered~~\n           ^"
        assert truncate_fn.call_args_list[0][0][1] == 6

    @mock.patch("libcube.cli.options.truncate_string_around", return_value=("~~rendered~~", 4))
    def test_wrong_line_length(self, _1):
        with pytest.raises(argparse.ArgumentTypeError) as e:
            side_colors_type("RRO/G/BBW")

        assert str(e.value) == "Inconsistent line length"
