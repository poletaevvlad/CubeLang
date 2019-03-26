from pathlib import Path
from typing import IO, Union, NamedTuple, Tuple, List, Callable, Dict

from lark import Lark, Tree

from .expression import Expression, TemplateType, ConditionExpression
from .types import Integer, Real, Type, Bool, Set, List as ListType, Void
from .stack import Stack


class BinaryOperator(NamedTuple):
    symbol: str
    expression: TemplateType
    arguments: List[Tuple[Tuple[Type, Type], Type]]


Callback = Callable[[Tree, Stack], Union[Type, Expression]]


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

    def handle(self, tree: Tree, stack: Stack) -> Union[Expression, Type]:
        return self.callbacks[tree.data](tree, stack)


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
        def handler(tree: Tree, stack: Stack, op=operator) -> Expression:
            assert len(tree.children) == 2
            expr1: Expression = compiler.handle(tree.children[0], stack)
            expr2: Expression = compiler.handle(tree.children[1], stack)
            arg_types = [expr1.type, expr2.type]
            for operand_types, result_type in op.arguments:
                if all(ar1.is_assignable(ar2) for ar1, ar2 in zip(operand_types, arg_types)):
                    return Expression.merge(result_type, op.expression, expr1, expr2)
            else:
                raise ValueError(f"Operator '{op.symbol}' is not applicable to values "
                                 f"of type {arg_types[0]} and {arg_types[1]}")


@compiler.handler("int_literal")
def handle_int_literal(tree: Tree, _stack: Stack) -> Expression:
    return Expression(Integer, str(int(tree.children[0])))


@compiler.handler("float_literal")
def handle_float_literal(tree: Tree, _stack: Stack) -> Expression:
    return Expression(Real, str(float(tree.children[0])))


@compiler.handler("bool_literal_true")
def handle_bool_literal_true(_tree: Tree, _stack: Stack) -> Expression:
    return Expression(Bool, "True")


@compiler.handler("bool_literal_false")
def handle_bool_literal_false(_tree: Tree, _stack: Stack) -> Expression:
    return Expression(Bool, "False")


@compiler.handler("variable")
def handle_variable(tree: Tree, stack: Stack) -> Expression:
    variable = stack.get_variable(tree.children[0])
    if variable is None:
        raise ValueError(f"Undefined symbol: 'f{tree.children[0]}'")
    var_name = "var_" + str(variable.number) if variable.number >= 0 else tree.children[0]
    return Expression(variable.type, var_name)


@compiler.handler("type_int")
@compiler.handler("type_real")
@compiler.handler("type_bool")
def handle_scalar_type(tree: Tree, _stack: Stack) -> Type:
    return {"type_int": Integer, "type_real": Real, "type_bool": Bool}[tree.data]


@compiler.handler("type_list")
@compiler.handler("type_set")
def handle_compound_type(tree: Tree, stack: Stack) -> Type:
    constructor = {"type_list": ListType, "type_set": Set}[tree.data]
    inner_type: Type = compiler.handle(tree.children[0], stack)
    return constructor(inner_type)


@compiler.handler("var_decl")
def handle_variable_declaration(tree: Tree, stack: Stack) -> List[Expression]:
    var_names: List[str] = []
    i = 0
    while isinstance(tree.children[i], str):
        var_names.append(tree.children[i])
        i += 1
    var_type: Type = compiler.handle(tree.children[i], stack)
    nums = [stack.add_variable(name, var_type) for name in var_names]

    if i != len(tree.children) - 1:
        value: Expression = compiler.handle(tree.children[i + 1], stack)
        if not (var_type.is_assignable(value.type)):
            raise ValueError(f"Value of type {value.type} cannot be assigned to variable of type {var_type}")
        return [Expression.merge(Void, ["var_" + str(num), " = ", 0], value) for num in nums]
    return []


def handle_clause(tree: Tree, stack: Stack) -> List[Expression]:
    if tree.data == "clause":
        stack.add_frame()
        expressions = [compiler.handle(subtree, stack) for subtree in tree.children]
        stack.pop_frame()
        return expressions
    else:
        return [compiler.handle(tree, stack)]


@compiler.handler("if_expression")
def handle_if_expression(tree: Tree, stack: Stack) -> Expression:
    condition = compiler.handle(tree.children[0], stack)
    if not Bool.is_assignable(condition.type):
        raise ValueError("Only expression of boolean type can be used as if condition")
    then_clause = handle_clause(tree.children[1], stack)
    if len(tree.children) > 2:
        else_clause = handle_clause(tree.children[2], stack)
    else:
        else_clause = []
    return ConditionExpression(condition, then_clause, else_clause)
