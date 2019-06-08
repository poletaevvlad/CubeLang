from libcube.compiler import Stack, parser
from libcube.execution import ExecutionContext
from libcube.compiler.types import Function, Integer, Void, Color
from libcube.cube_runtime import CubeRuntime
from libcube.stdlib import stdlib
from libcube.cube import Cube
from libcube import orientation

from unittest.mock import MagicMock

from libcube.orientation import Orientation


def test_flip_flops():
    code = """
        let count: int
        do
            RUR'U'
            count = count + 1
        while top[1, 1] != top[2, 2]
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
    executor.execute()
    cube_runtime.finished()

    out_fn.assert_called_once_with(6)
    finish_function.assert_called_once()


def test_orient():
    code = """
        orient top: G--/---/---, bottom: --Y/---/--- then
            out(red)
        else-orient top: (-W-/---/---), right: (---/---/-O-) then
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
    executor.execute()
    cube_runtime.finished()
    out_fn.assert_called_once_with(orientation.Color.WHITE)
