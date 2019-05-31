from string import ascii_lowercase
import pytest
from libcube.cli.options import truncate_string_around, CubeFormulaParamType, SideConfigurationType
from libcube.parser import ParsingError
from unittest import mock
import click

from libcube.orientation import Color


@pytest.fixture(scope="module")
def context():
    context = mock.create_autospec(click.Context)
    context.command = None
    return context


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


class TestFormulaParam:
    @mock.patch("libcube.cli.options.parse_actions", return_value=iter([1, 2, 3]))
    def test_correct(self, parse_actions_function, context):
        param = CubeFormulaParamType()

        actual = param.convert("abcdef", "test-param", context)
        assert actual == [1, 2, 3]
        parse_actions_function.assert_called_once_with("abcdef")

    @mock.patch("libcube.cli.options.parse_actions", side_effect=ParsingError("~~test error~~", 10))
    @mock.patch("libcube.cli.options.truncate_string_around", return_value=("~~rendered~~", 4))
    def test_invalid_syntax(self, _1, _2, context):
        param = CubeFormulaParamType()

        context = mock.create_autospec(click.Context)
        context.command = None

        with pytest.raises(click.exceptions.BadParameter) as e:
            param.convert(ascii_lowercase, "parameter", context)

        error: click.exceptions.BadParameter = e.value
        assert error.param == "parameter"
        assert error.ctx == context
        assert error.message == "~~test error~~\n       ~~rendered~~\n           ^"


class TestSideConfiguration:
    def test_valid(self, context):
        param = SideConfigurationType()
        actual = param.convert("RRO/GGY/BBW", "parameter", context)
        assert actual == [[Color.RED, Color.RED, Color.ORANGE],
                          [Color.GREEN, Color.GREEN, Color.YELLOW],
                          [Color.BLUE, Color.BLUE, Color.WHITE]]

    @mock.patch("libcube.cli.options.truncate_string_around", return_value=("~~rendered~~", 4))
    def test_wrong_symbol(self, truncate_fn: mock.MagicMock, context):
        param = SideConfigurationType()
        with pytest.raises(click.exceptions.BadParameter) as e:
            param.convert("RRO/GGM/BBW", "parameter", context)

        error: click.exceptions.BadParameter = e.value
        assert error.param == "parameter"
        assert error.ctx == context
        assert error.message == "Unknown color: `M`\n       ~~rendered~~\n           ^"
        assert truncate_fn.call_args_list[0][0][1] == 6

    @mock.patch("libcube.cli.options.truncate_string_around", return_value=("~~rendered~~", 4))
    def test_wrong_line_length(self, _1, context):
        param = SideConfigurationType()
        with pytest.raises(click.exceptions.BadParameter) as e:
            param.convert("RRO/G/BBW", "parameter", context)

        error: click.exceptions.BadParameter = e.value
        assert error.param == "parameter"
        assert error.ctx == context
        assert error.message == "Inconsistent line length"
