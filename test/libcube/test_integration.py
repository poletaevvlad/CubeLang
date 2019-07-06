from cubelang.compiler.code_map import CodeMap
from cubelang.compiler import Stack, parser
from cubelang.execution import ExecutionContext
from cubelang.compiler.types import Function, Integer, Void, Color
from cubelang.cube_runtime import CubeRuntime
from cubelang.stdlib import stdlib
from cubelang.cube import Cube
from cubelang import orientation
from cubelang.orientation import Orientation
from cubelang.execution.executor import ITracebackWriter

from unittest.mock import MagicMock


class MockTracebackWriter(ITracebackWriter):
    def print_traceback(self, error: RuntimeError, code_map: CodeMap) -> None:
        raise RuntimeError()


def test_flip_flops():
    code = """
        let count: int
        while top[1, 1] != top[2, 2] or count == 0 do 
            RUR'U'
            count = count + 1
        end
        out(count)
    """

    out_fn = MagicMock()

    stack = Stack()
    finish_function = MagicMock()
    cube_runtime = CubeRuntime(Cube((3, 3, 3)), Orientation(), lambda action: None, finish_function)
    cube_runtime.functions.initialize_stack(stack)
    stdlib.initialize_stack(stack)
    stack.add_global("out", Function(([Integer], Void)))

    globals = {"out": out_fn, **stdlib.exec_globals, **cube_runtime.functions.exec_globals}

    executor = ExecutionContext(globals)
    executor.compile(parser.parse(code, stack))
    executor.execute(MockTracebackWriter())
    cube_runtime.finished()

    out_fn.assert_called_once_with(6)
    finish_function.assert_called_once()


def test_orient():
    code = """
        orient top: {G--/---/---}, bottom: {--Y/---/---} then
            out(red)
        else-orient top: {-W-/---/---}, right: {---/---/-O-} then
            out(top[1, 1])
        end
    """

    out_fn = MagicMock()
    stack = Stack()
    cube_runtime = CubeRuntime(Cube((3, 3, 3)), Orientation(), lambda action: None, lambda: None)
    cube_runtime.functions.initialize_stack(stack)
    stdlib.initialize_stack(stack)
    stack.add_global("out", Function(([Color], Void)))

    globals = {"out": out_fn, **stdlib.exec_globals, **cube_runtime.functions.exec_globals}

    executor = ExecutionContext(globals)
    executor.compile(parser.parse(code, stack))
    executor.execute(MockTracebackWriter())
    cube_runtime.finished()
    out_fn.assert_called_once_with(orientation.Color.WHITE)
