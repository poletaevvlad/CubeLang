from string import ascii_lowercase
import pytest
import argparse
from cubelang.cli.options import truncate_string_around, integer_type, \
    side_colors_type, formula_type, file_contents_type, dict_type
from cubelang.parser import ParsingError
from unittest import mock

from cubelang.orientation import Color


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


class TestIntegerType:
    def test_normal(self):
        assert integer_type(1)("2") == 2

    def test_invalid(self):
        with pytest.raises(argparse.ArgumentTypeError):
            integer_type(5)("abc")

    def test_too_small(self):
        with pytest.raises(argparse.ArgumentTypeError):
            integer_type(5)("2")


class TestFormulaParam:
    @mock.patch("cubelang.cli.options.parse_actions", return_value=iter([1, 2, 3]))
    def test_correct(self, parse_actions_function):
        actual = formula_type("abcdef")
        assert actual == [1, 2, 3]
        parse_actions_function.assert_called_once_with("abcdef")

    @mock.patch("cubelang.cli.options.parse_actions", side_effect=ParsingError("~~test error~~", 10))
    @mock.patch("cubelang.cli.options.truncate_string_around", return_value=("~~rendered~~", 4))
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

    @mock.patch("cubelang.cli.options.truncate_string_around", return_value=("~~rendered~~", 4))
    def test_wrong_symbol(self, truncate_fn: mock.MagicMock):
        with pytest.raises(argparse.ArgumentTypeError) as e:
            side_colors_type("RRO/GGM/BBW")

        assert str(e.value) == "unknown color: `M`\n       ~~rendered~~\n           ^"
        assert truncate_fn.call_args_list[0][0][1] == 6

    @mock.patch("cubelang.cli.options.truncate_string_around", return_value=("~~rendered~~", 4))
    def test_wrong_line_length(self, _1):
        with pytest.raises(argparse.ArgumentTypeError) as e:
            side_colors_type("RRO/G/BBW")

        assert str(e.value) == "inconsistent line length"


class TestFileOpen:
    def test_normal(self):
        with mock.patch("cubelang.cli.options.open", mock.mock_open(read_data="data")) as open_mock:
            assert file_contents_type("/file") == "data"
            open_mock.assert_called_once_with("/file")

    @mock.patch("cubelang.cli.options.open")
    def test_io_error(self, open_mock):
        open_mock.side_effect = IOError("~~error~~")
        with pytest.raises(argparse.ArgumentTypeError) as e:
            file_contents_type("/file")
        assert str(e.value) == "cannot open a file: ~~error~~"


class TestDictType:
    def test_valid(self):
        t = dict_type(dict(a=1, b=2, c=3))
        assert t("a") == 1
        assert t("b") == 2

    def test_invalid(self):
        t = dict_type(dict(a=1, b=2, c=3))
        with pytest.raises(argparse.ArgumentTypeError) as e:
            t("d")
        assert str(e.value) == "unknown value: 'd'; expected either 'a', 'b' or 'c'"

    def test_invalid_two_options(self):
        t = dict_type(dict(a=1, b=2))
        with pytest.raises(argparse.ArgumentTypeError) as e:
            t("d")
        assert str(e.value) == "unknown value: 'd'; expected either 'a' or 'b'"
