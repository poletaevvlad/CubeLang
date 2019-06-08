import math
from unittest.mock import MagicMock

from libcube.compiler.code_map import CodeMap
from libcube.compiler.parser import parser
from libcube.compiler.stack import Stack
from libcube.compiler.types import Integer, Function, Void, Real
from libcube.execution.executor import ExecutionContext, ITracebackWriter
from libcube.execution.rt_error import RuntimeError
from libcube.stdlib import stdlib


class MockTracebackWriter(ITracebackWriter):
    def print_traceback(self, error: RuntimeError, code_map: CodeMap) -> None:
        raise RuntimeError("")


def test_execution_simple():
    code = """
        let x: int = -15
        let y: int = x * abs(x + a)
        print(x * y)
    """

    stack = Stack()
    stack.add_global("a", Integer)
    stack.add_global("abs", Function(([Integer], Integer)))
    stack.add_global("print", Function(([Integer], Void)))

    expressions = parser.parse(code, stack)
    globals = {
        "a": 10,
        "abs": abs,
        "print": MagicMock()
    }
    context = ExecutionContext(globals)
    context.compile(expressions)
    context.execute(MockTracebackWriter())
    assert tuple(globals["print"].call_args[0]) == (1125,)


def test_execution_gcd():
    code = """
        let a: int = 15
        let b: int = 6
        while a != 0 and b != 0 do
            if a > b then
                a = a - b
            else
                b = b - a
            end
        end
        print (a + b)
    """

    stack = Stack()
    stack.add_global("print", Function(([Integer], Void)))
    expressions = parser.parse(code, stack)

    context = ExecutionContext(dict(print=MagicMock()))
    context.compile(expressions)
    context.execute(MockTracebackWriter())
    assert tuple(context.globals["print"].call_args[0]) == (3,)


def test_execution_integration():
    """
    Computing pi by integrating:
    \frac{\pi}{2} = \int^1_{-1} \sqrt{1 - x^2} dx
    """

    code = """
        let delta_x: real = 0.001
        let x: real = -1
        let y: real = sqrt(1 - x * x)
        let result: real
                
        while x + delta_x < 1 do
            let next_x: real = x + delta_x 
            let next_y: real = sqrt(1 - next_x * next_x)
            result = result + (y + next_y) / 2 * delta_x
            
            y = next_y
            x = next_x
        end
        print(result * 2)
    """
    stack = Stack()
    stack.add_global("print", Function(([Real], Void)))
    stack.add_global("sqrt", Function(([Real], Real)))
    expressions = parser.parse(code, stack)

    context = ExecutionContext(dict(print=MagicMock(), sqrt=math.sqrt))
    context.compile(expressions)
    context.execute(MockTracebackWriter())
    return_value = context.globals["print"].call_args[0][0]
    assert abs(return_value - math.pi) < 0.01


def test_pascals_triangle():
    """
    Computes five lines of Pascal's triangle:
                     1
                   1   1
                 1   2   1
               1   3   3   1
            1   4   6   4    1
    Values are returned via `print` function line by line separated by `0`.
    """
    code = """
        let result: list of list of int        
        let row_size: int = 1
        
        repeat 5 times
            let row: list of int = new_list(row_size, 1)
            let i: int = 1
            while i < row_size - 1 do
                row[i] = result[size(result) - 1][i] + result[size(result) - 1][i - 1]
                i = i + 1 
            end
            add_last(result, row)
            row_size = row_size + 1
        end
        
        for row in result do
            for x in row do
                print(x)
            end
            print(0)
        end
    """
    stack = Stack()
    stack.add_global("print", Function(([Integer], Void)))
    stdlib.initialize_stack(stack)

    expressions = parser.parse(code, stack)

    print_fn = MagicMock()
    context = ExecutionContext(dict(print=print_fn, **stdlib.exec_globals))
    context.compile(expressions)
    context.execute(MockTracebackWriter())
    return_value = [x[0][0] for x in print_fn.call_args_list]
    assert return_value == [1, 0, 1, 1, 0, 1, 2, 1, 0, 1, 3, 3, 1, 0, 1, 4, 6, 4, 1, 0]


def test_functions():
    code = """
        func compute()
            func r(x: int): int
                func g(x: int): int
                    return x - 1
                end
            
                let c: int
                while x != 0 do
                    x = g(x)
                    c = c + 1
                end
                return c
            end
            
            let i: int = 1
            while true do
                if i == 5 then
                    return
                end
                print(r(i))
                i = i + 1
            end
        end
        compute()
    """
    stack = Stack()
    stack.add_global("print", Function(([Integer], Void)))
    stdlib.initialize_stack(stack)
    expressions = parser.parse(code, stack)

    print_fn = MagicMock()
    context = ExecutionContext(dict(print=print_fn, **stdlib.exec_globals))
    context.compile(expressions)
    context.execute(MockTracebackWriter())
    return_value = [x[0][0] for x in print_fn.call_args_list]
    assert return_value == [1, 2, 3, 4]


def test_exception():
    code = """
        func f()
            throw()
        end
        
        f()
    """

    stack = Stack()
    stack.add_global("throw", Function(([], Void)))
    expressions = parser.parse(code, stack)

    def throw_function():
        raise ValueError("~~error~~")

    writer = MockTracebackWriter()
    writer.print_traceback = MagicMock()

    context = ExecutionContext({"throw": throw_function})
    context.compile(expressions)
    context.execute(writer)

    error: RuntimeError = writer.print_traceback.call_args_list[0][0][0]
    assert str(error) == "~~error~~"
    assert tuple(error.stack_entries[0]) == ("f", 2)
    assert tuple(error.stack_entries[1]) == (None, 3)
    assert context.code_map[2] == 2
    assert context.code_map[3] == 5
