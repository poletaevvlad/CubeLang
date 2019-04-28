import lark
from .types import Type
from .expression import Expression

from typing import Optional, Union


class CompileTimeError(Exception):
    def __init__(self, node: lark.Tree, message: str):
        super(CompileTimeError, self).__init__(message)
        if hasattr(node.meta, "line"):
            self.start_line = node.line
            self.start_column = node.column
            self.end_line = node.end_line
            self.end_column = node.end_column


class ValueTypeError(CompileTimeError):
    def __init__(self, node: lark.Tree, message: str, expected: Optional[Type], actual: Type):
        super(ValueTypeError, self).__init__(node, message)
        self.expected = expected
        self.actual = actual


def assert_type(node: lark.Tree, expression: Union[Expression, Type],
                required: Type, message: Optional[str] = None):
    val_type = expression if isinstance(expression, Type) else expression.type
    if required.is_assignable(val_type):
        return
    if message is None:
        message = f"Expected value of type {required} but a {val_type} was found."
    raise ValueTypeError(node, message, required, val_type)
