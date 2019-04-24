from typing import NamedTuple, List, Tuple
from .types import Type, Bool, Real, Integer, Color, Side
from .expression import TemplateType


class BinaryOperator(NamedTuple):
    symbol: str
    expression: TemplateType
    arguments: List[Tuple[Tuple[Type, Type], Type]]


BINARY_OPERATORS = [[
    BinaryOperator("xor", ["(", 0, ") != (", 1, ")"], [((Bool, Bool), Bool)]),
], [
    BinaryOperator("or", ["(", 0, ") or (", 1, ")"], [((Bool, Bool), Bool)]),
], [
    BinaryOperator("and", ["(", 0, ") and (", 1, ")"], [((Bool, Bool), Bool)]),
], [
    BinaryOperator("==", ["(", 0, ") == (", 1, ")"], [
        ((Real, Real), Bool), ((Bool, Bool), Bool), ((Color, Color), Bool), ((Side, Side), Bool)]),
    BinaryOperator("!=", ["(", 0, ") != (", 1, ")"], [
        ((Real, Real), Bool), ((Bool, Bool), Bool), ((Color, Color), Bool), ((Side, Side), Bool)])
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