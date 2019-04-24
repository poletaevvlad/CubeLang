from libcube.compiler import Stack, ExecutionContext, parser
from libcube.compiler.types import Function, Integer, Void
from libcube.cube_runtime import CubeRuntime
from libcube.stdlib import stdlib

from unittest.mock import MagicMock


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
    cube_context = CubeRuntime(lambda action: None)
    cube_context.functions.initialize_stack(stack)
    stdlib.initialize_stack(stack)
    stack.add_global("out", Function(([Integer], Void)))

    globals = {"out": out_fn, **stdlib.exec_globals, **cube_context.functions.exec_globals}

    executor = ExecutionContext(globals)
    executor.compile(parser.parse(code, stack))
    executor.execute()

    out_fn.assert_called_once_with(6)
