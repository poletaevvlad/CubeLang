from io import StringIO

from libcube.cli.error_display import ErrorsOutput
from libcube.compiler.types import Function, Integer, List, Set, Bool, Void
from libcube.compiler.code_map import CodeMap
from libcube.execution import RuntimeError


def test_code_single_line():
    file = StringIO()
    errors = ErrorsOutput(file)
    errors.max_width = 11
    errors.line_number_margin = 1

    text = "0123456789" * 3
    errors.display_code(text, 0, 10, 0, 20)

    result = file.getvalue()
    assert "1 012345678\n  901234567\n   ^^^^^^^^\n  890123456\n  ^^^\n  789\n" == result


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


def test_function_output():
    func = Function(([Integer, List(Integer), Set(Bool)], Bool),
                    ([Bool, Bool, Set(Set(Bool))], Integer),
                    ([Integer, Integer], Void))
    file = StringIO()
    errors = ErrorsOutput(file)
    errors.max_width = 32
    errors.write_function_overloads("function", func)

    expected = """\
Function arguments:
    function(int, list of int, 
             set of bool): bool
    function(bool, bool, 
             set of set of bool
            ): int
    function(int, int)

"""
    actual = file.getvalue()
    assert expected == actual


def test_supplied_argument():
    args = [Integer, List(Integer), Set(Bool), Bool, Bool]
    file = StringIO()
    errors = ErrorsOutput(file)
    errors.max_width = 25
    errors.write_supplied_arguments(args)
    expected = """\
Supplied arguments:
    int, list of int, 
    set of bool, bool, 
    bool

"""
    actual = file.getvalue()
    assert expected == actual


def test_traceback():
    file = StringIO()
    errors = ErrorsOutput(file)
    errors.max_width = 35

    error = RuntimeError("Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
    error.add_stack_entry("func1", 20)
    error.add_stack_entry("func2", 25)
    error.add_stack_entry(None, 30)

    src_map = CodeMap()
    src_map.add(20, 10)
    src_map.add(25, 12)
    src_map.add(30, 14)
    errors.print_traceback(error, src_map)

    expected = """\
[runtime error]

    Lorem ipsum dolor sit amet,
    consectetur adipiscing elit.

Stack trace:
    line 11   : func1
    line 13   : func2
    line 15   
"""
    actual = file.getvalue()
    assert expected == actual
