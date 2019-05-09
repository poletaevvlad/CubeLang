from io import StringIO

from libcube.cli.error_display import ErrorsOutput


def test_code_single_line():
    file = StringIO()
    errors = ErrorsOutput(file)
    errors.max_width = 11
    errors.line_number_margin = 1

    text = "0123456789" * 3
    errors.display_code(text, 0, 10, 0, 20)

    result = file.getvalue()
    assert "1 012345678\n  901234567\n   ~~~~~~~~\n  890123456\n  ~~~\n  789\n" == result


def test_code_many_lines():
    file = StringIO()
    errors = ErrorsOutput(file)

    text = "\n".join("abcdefghi")
    errors.display_code(text, 2, 0, 7, 0)

    result = file.getvalue()
    assert "3  c\n4  d\n...\n7  g\n8  h\n" == result


def test_code_few_lines():
    file = StringIO()
    errors = ErrorsOutput(file)

    text = "\n".join("abcdefghijklmnopq")
    errors.display_code(text, 8, 0, 11, 0)

    result = file.getvalue()
    assert " 9  i\n10  j\n11  k\n12  l\n" == result
