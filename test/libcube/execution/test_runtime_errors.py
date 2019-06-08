from unittest import mock
from libcube.execution.rt_error import RuntimeError
from libcube.execution.rt_function import runtime_function
from textwrap import dedent
import pytest


class TestUpdateError:
    @mock.patch("libcube.execution.rt_error.RuntimeError.get_exception_line")
    def test_create(self, get_line_fn: mock.MagicMock):
        get_line_fn.return_value = 10

        e = ValueError("value error")
        exp = RuntimeError.update_error("function", e)
        assert isinstance(exp, RuntimeError)
        assert len(exp.stack_entries) == 1
        assert exp.stack_entries[0].function_name == "function"
        assert exp.stack_entries[0].line_number == 10

    @mock.patch("libcube.execution.rt_error.RuntimeError.get_exception_line")
    def test_update(self, get_line_fn: mock.MagicMock):
        get_line_fn.return_value = 20

        e = RuntimeError("abc")
        e.add_stack_entry("func1", 10)
        exp = RuntimeError.update_error("func2", e)
        assert isinstance(exp, RuntimeError)
        assert tuple(exp.stack_entries[0]) == ("func1", 10)
        assert tuple(exp.stack_entries[1]) == ("func2", 20)

    def test_wrong_exception(self):
        e = NameError()
        with pytest.raises(NameError):
            RuntimeError.update_error("function", e)


def test_runtime_function_decorator():
    @runtime_function("123")
    def function():
        return 1

    assert function.name == "123"
    assert function() == 1


def test_error_propagation():
    code = dedent("""
        @runtime_function("func_a")
        def a():
            raise ValueError("~~error~~")
        
        @runtime_function("func_b")    
        def b():
            a()
            
        @runtime_function("func_c")
        def c():
            b() 
        
        c()
    """)
    with pytest.raises(RuntimeError) as e:
        try:
            exec(compile(code, "<string>", "exec"),
                 {"runtime_function": runtime_function})
        except RuntimeError as e1:
            raise RuntimeError.update_error(None, e1)

    error: RuntimeError = e.value
    assert tuple(error.stack_entries[0]) == ("func_a", 3)
    assert tuple(error.stack_entries[1]) == ("func_b", 7)
    assert tuple(error.stack_entries[2]) == ("func_c", 11)
    assert tuple(error.stack_entries[3]) == (None, 13)
