from pathlib import Path
from typing import IO, Union, NamedTuple, Tuple, List, Callable, Dict

from lark import Lark, Tree

from .expression import Expression, TemplateType
from .types import Integer, Real, Type


class BinaryOperator(NamedTuple):
    symbol: str
    expression: TemplateType
    arguments: List[Tuple[Tuple[Type, Type], Type]]


Callback = Callable[[Tree], Union[Type, Expression]]


class Compiler:
    def __init__(self):
        path = Path(__file__).parents[2] / "data" / "syntax.lark"
        with open(str(path)) as f:
            grammar = f.read()
        self.lark = Lark(grammar)
        self.callbacks: Dict[str, Callback] = dict()

    def compile(self, file: Union[str, IO[str]]):
        if not isinstance(file, str):
            file = file.read()
        tree = self.lark.parse(file)
        pass

    def handler(self, name: str) -> Callable[[Callback], Callback]:
        def wrapper(func: Callback) -> Callback:
            self.callbacks[name] = func
            return func
        return wrapper

    def handle(self, tree: Tree) -> Union[Expression, Type]:
        return self.callbacks[tree.data](tree)


compiler = Compiler()
BINARY_OPERATORS = [[
    BinaryOperator("+", ["(", 0, ") + (", 1, ")"], [((Integer, Integer), Integer), ((Real, Real), Real)]),
    BinaryOperator("-", ["(", 0, ") - (", 1, ")"], [((Integer, Integer), Integer), ((Real, Real), Real)]),
    BinaryOperator("*", ["(", 0, ") * (", 1, ")"], [((Integer, Integer), Integer), ((Real, Real), Real)]),
    BinaryOperator("/", ["(", 0, ") / (", 1, ")"], [((Real, Real), Real)]),
]]

for precedence, operators in enumerate(BINARY_OPERATORS):
    for i, operator in enumerate(operators):
        @compiler.handler(f"op_{precedence}_{i}")
        def handler(tree: Tree, op=operator) -> Expression:
            assert len(tree.children) == 2
            expr1: Expression = compiler.handle(tree.children[0])
            expr2: Expression = compiler.handle(tree.children[1])
            arg_types = [expr1.type, expr2.type]
            for operand_types, result_type in op.arguments:
                if all(ar1.is_assignable(ar2) for ar1, ar2 in zip(operand_types, arg_types)):
                    return Expression.merge(result_type, op.expression, expr1, expr2)
            else:
                raise ValueError(f"Operator '{op.symbol}' is not applicable to values "
                                 f"of type {arg_types[0]} and {arg_types[1]}")


@compiler.handler("int_literal")
def handle_int_literal(tree: Tree) -> Expression:
    return Expression(Integer, str(int(tree.children[0])))


@compiler.handler("float_literal")
def handle_float_literal(tree: Tree) -> Expression:
    return Expression(Real, str(float(tree.children[0])))
