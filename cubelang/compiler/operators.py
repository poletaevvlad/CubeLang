from typing import NamedTuple, List, Tuple, Union, Callable, Optional

from .expression import TemplateType
from .types import Type, Bool, Real, Integer, Void

ArgumentsType = Union[List[Tuple[Tuple[Type, Type], Type]],
                      Callable[[Type, Type], Optional[Type]]]


class BinaryOperator(NamedTuple):
    symbol: str
    expression: TemplateType
    arguments: ArgumentsType


def _operator_equals(a: Type, b: Type) -> Optional[Type]:
    if a == Void or a != b:
        return None
    else:
        return Bool


BINARY_OPERATORS = [[
    BinaryOperator("xor", ["(", 0, ") != (", 1, ")"], [((Bool, Bool), Bool)]),
], [
    BinaryOperator("or", ["(", 0, ") or (", 1, ")"], [((Bool, Bool), Bool)]),
], [
    BinaryOperator("and", ["(", 0, ") and (", 1, ")"], [((Bool, Bool), Bool)]),
], [
    BinaryOperator("==", ["(", 0, ") == (", 1, ")"], _operator_equals),
    BinaryOperator("!=", ["(", 0, ") != (", 1, ")"], _operator_equals)
], [
    BinaryOperator("<", ["(", 0, ") < (", 1, ")"], [((Real, Real), Bool)]),
    BinaryOperator(">", ["(", 0, ") > (", 1, ")"], [((Real, Real), Bool)]),
    BinaryOperator("<=", ["(", 0, ") <= (", 1, ")"], [((Real, Real), Bool)]),
    BinaryOperator(">=", ["(", 0, ") >= (", 1, ")"], [((Real, Real), Bool)])
], [
    BinaryOperator("+", ["(", 0, ") + (", 1, ")"], [((Integer, Integer), Integer), ((Real, Real), Real)]),
    BinaryOperator("-", ["(", 0, ") - (", 1, ")"], [((Integer, Integer), Integer), ((Real, Real), Real)])
], [
    BinaryOperator("*", ["(", 0, ") * (", 1, ")"], [((Integer, Integer), Integer), ((Real, Real), Real)]),
    BinaryOperator("/", ["(", 0, ") / (", 1, ")"], [((Real, Real), Real)]),
    BinaryOperator("%", ["(", 0, ") % (", 1, ")"], [((Integer, Integer), Integer)])
]]


def operator_applicable(actual_types: List[Type],
                        operator_types: ArgumentsType) -> Optional[Type]:
    if isinstance(operator_types, list):
        for operand_types, result_type in operator_types:
            if all(ar1.is_assignable(ar2) for ar1, ar2 in zip(operand_types, actual_types)):
                return result_type
        else:
            return None
    else:
        return operator_types(*actual_types)
