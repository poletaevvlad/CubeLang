import lark
from .types import Type, Function
from .expression import Expression

from typing import Optional, Union, List


class CompileTimeError(Exception):
    def __init__(self, node: lark.Tree, message: str):
        super(CompileTimeError, self).__init__(message)
        if isinstance(node, lark.Token) or hasattr(node.meta, "line"):
            self.start_line = node.line
            self.start_column = node.column
            self.end_line = node.end_line
            self.end_column = node.end_column


class ValueTypeError(CompileTimeError):
    def __init__(self, node: lark.Tree, message: str, expected: Optional[Type], actual: Type):
        super(ValueTypeError, self).__init__(node, message)
        self.expected = expected
        self.actual = actual


class UnresolvedReferenceError(CompileTimeError):
    def __init__(self, node: lark.Tree, name: Optional[str] = None):
        if name is None:
            name = str(node)
        message = f"Unresolved symbol: `{name}`"
        super(UnresolvedReferenceError, self).__init__(node, message)


class FunctionArgumentsError(CompileTimeError):
    def __init__(self, node: lark.Tree, function_name: str,
                 function: Function, arguments: List[Type]):
        super(FunctionArgumentsError, self).__init__(node, "Invalid function arguments")
        self.function_name = function_name
        self.function: Function = function
        self.arguments = arguments


def assert_type(node: lark.Tree, expression: Union[Expression, Type],
                required: Type, message: Optional[str] = None):
    val_type = expression if isinstance(expression, Type) else expression.type
    if required.is_assignable(val_type):
        return
    if message is None:
        message = f"Expected value of type {required} but a {val_type} was found."
    raise ValueTypeError(node, message, required, val_type)
