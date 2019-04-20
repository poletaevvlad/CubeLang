from libcube.compiler.parser import parser
from libcube.compiler.stack import Stack
from libcube.compiler.types import Integer, Function, Void
from libcube.compiler.executor import ExecutionContext

from unittest.mock import MagicMock


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
    assert context.source == "var_0 = -15\nvar_1 = (var_0) * (abs((var_0) + (a)))\nprint((var_0) * (var_1))\n"

    context.execute()
    assert tuple(globals["print"].call_args[0]) == (1125,)


# def test_execution_gcd():
#     code = """
#         let a: int = 15
#         let b: int = 6
#         while a != 0 and b != 0 do
#             if a > b then
#                 a = a - b
#             else
#                 b = b - a
#             end
#         end
#         print (a + b)
#     """
#
#     stack = Stack()
#     stack.add_global("print", Function(([Integer], Void)))
#     expressions = parser.parse(code, stack)
#
#     context = ExecutionContext(dict(print=MagicMock()))
#     context.compile(expressions)
#     context.execute()
#     assert tuple(context.globals["print"].call_args[0]) == (3,)
