from io import StringIO

from libcube.cli.error_display import display_code_line


def test_display_error_line():
    file = StringIO()
    text = "01234567890123456789012345"
    display_code_line(file, text, 13, 3, 15, use_color=False)
    result = file.getvalue()
    assert " 13  0123456789\n     0123456789\n     012345\n" == result


def test_display_error_single_line():
    file = StringIO()
    text = "0123"
    display_code_line(file, text, 10, 3, 15, use_color=False)
    result = file.getvalue()
    assert " 10  0123\n" == result
