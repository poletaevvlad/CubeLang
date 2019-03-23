from lark import Lark, Transformer
from typing import IO, Union, NamedTuple, Tuple, List
from pathlib import Path

from .expression import Expression
from .types import Integer, Real, Type


class BinaryOperator(NamedTuple):
    symbol: str
    expression: Union[str, List[str]]
    arguments: List[Tuple[Tuple[Type, Type], Type]]


# noinspection PyMethodMayBeStatic
class CompilerTransformer(Transformer):
    BINARY_OPERATORS = [[
        BinaryOperator("+", "({0}) + ({1})", [((Integer, Integer), Integer), ((Real, Real), Real)]),
        BinaryOperator("-", "({0}) - ({1})", [((Integer, Integer), Integer), ((Real, Real), Real)]),
        BinaryOperator("*", "({0}) * ({1})", [((Integer, Integer), Integer), ((Real, Real), Real)]),
        BinaryOperator("/", "({0}) / ({1})", [((Real, Real), Real)]),
    ]]

    @staticmethod
    def operator_method(operator: BinaryOperator, args: List[Expression]):
        assert len(args) == 2
        arg_types = [x.type for x in args]
        for operand_types, result_type in operator.arguments:
            if all(ar1.is_assignable(ar2) for ar1, ar2 in zip(operand_types, arg_types)):
                return Expression.merge(result_type, operator.expression, *args)
        else:
            raise ValueError(f"Operator '{operator.symbol}' is not applicable to values "
                             f"of type {arg_types[0]} and {arg_types[1]}")

    def int_literal(self, values):
        value = int(values[0])
        return Expression(Integer, str(value))

    def float_literal(self, values):
        value = float(values[0])
        return Expression(Real, str(value))


for precedence, operators in enumerate(CompilerTransformer.BINARY_OPERATORS):
    for i, operator in enumerate(operators):
        setattr(CompilerTransformer, f"op_{precedence}_{i}",
                lambda self, args, op=operator: CompilerTransformer.operator_method(op, args))


class Compiler:
    def __init__(self):
        path = Path(__file__).parents[2] / "data" / "syntax.lark"
        with open(str(path)) as f:
            grammar = f.read()
        self.lark = Lark(grammar)

    def compile(self, file: Union[str, IO[str]]):
        if not isinstance(file, str):
            file = file.read()
        tree = self.lark.parse(file)
        return CompilerTransformer().transform(tree)
