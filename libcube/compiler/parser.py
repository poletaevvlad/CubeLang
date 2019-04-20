from pathlib import Path
from typing import Union, NamedTuple, Tuple, List, Callable, Dict, IO, Iterator

from lark import Tree, Lark

from .expression import Expression, TemplateType, ConditionExpression, WhileLoopExpression, DoWhileLoopExpression, \
    RepeatLoopExpression, ForLoopExpression
from .stack import Stack
from .types import Integer, Real, Type, Bool, Set, List as ListType, Void, CollectionType, Function, Color, Side


TYPE_NAMES = {"type_int": Integer, "type_real": Real, "type_bool": Bool, "type_color": Color, "type_side": Side}


class BinaryOperator(NamedTuple):
    symbol: str
    expression: TemplateType
    arguments: List[Tuple[Tuple[Type, Type], Type]]


Callback = Callable[[Tree, Stack], Union[Type, Expression]]

BINARY_OPERATORS = [[
    BinaryOperator("xor", ["(", 0, ") != (", 1, ")"], [((Bool, Bool), Bool)]),
], [
    BinaryOperator("or", ["(", 0, ") or (", 1, ")"], [((Bool, Bool), Bool)]),
], [
    BinaryOperator("and", ["(", 0, ") and (", 1, ")"], [((Bool, Bool), Bool)]),
], [
    BinaryOperator("==", ["(", 0, ") == (", 1, ")"], [((Real, Real), Bool), ((Bool, Bool), Bool)]),
    BinaryOperator("!=", ["(", 0, ") != (", 1, ")"], [((Real, Real), Bool), ((Bool, Bool), Bool)]),
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
    BinaryOperator("mod", ["(", 0, ") % (", 1, ")"], [((Integer, Integer), Integer)])
]]


class Parser:
    def __init__(self):
        path = Path(__file__).parents[2] / "data" / "syntax.lark"
        with open(str(path)) as f:
            grammar = Parser._generate_operators(BINARY_OPERATORS) + f.read()
        self.lark = Lark(grammar, start="clause")
        self.callbacks: Dict[str, Callback] = dict()

    @staticmethod
    def _generate_operators(operators: List[List[BinaryOperator]]) -> str:
        lines = []
        for op_index, op in enumerate(operators):
            this_name = "op_" + str(op_index)
            next_name = "op_" + str(op_index + 1) if op_index < len(operators) - 1 else "atom"
            lines.append(f"?{this_name}.{len(operators) - op_index}: {next_name} | ")
            lines.append(" | ".join(f"{this_name} \"{operator.symbol}\" {next_name} -> op_{op_index}_{index}"
                                    for index, operator in enumerate(op)))
            lines.append("\n")
        return "".join(lines)

    def handler(self, name: str) -> Callable[[Callback], Callback]:
        def wrapper(func: Callback) -> Callback:
            self.callbacks[name] = func
            return func
        return wrapper

    def handle(self, tree: Tree, stack: Stack) -> Union[Expression, Type]:
        return self.callbacks[tree.data](tree, stack)

    def parse(self, file: Union[IO, str], stack: Stack) -> Iterator[Expression]:
        if not isinstance(file, str):
            file = file.read()
        tree = self.lark.parse(file)
        for subtree in tree.children:
            expr = self.handle(subtree, stack)
            if isinstance(expr, Expression):
                yield expr
            else:
                yield from expr


parser = Parser()

for precedence, operators in enumerate(BINARY_OPERATORS):
    for i, operator in enumerate(operators):
        @parser.handler(f"op_{precedence}_{i}")
        def handler(tree: Tree, stack: Stack, op=operator) -> Expression:
            assert len(tree.children) == 2
            expr1: Expression = parser.handle(tree.children[0], stack)
            expr2: Expression = parser.handle(tree.children[1], stack)
            arg_types = [expr1.type, expr2.type]
            for operand_types, result_type in op.arguments:
                if all(ar1.is_assignable(ar2) for ar1, ar2 in zip(operand_types, arg_types)):
                    return Expression.merge(result_type, op.expression, expr1, expr2)
            else:
                raise ValueError(f"Operator '{op.symbol}' is not applicable to values "
                                 f"of type {arg_types[0]} and {arg_types[1]}")


@parser.handler("int_literal")
def handle_int_literal(tree: Tree, _stack: Stack) -> Expression:
    return Expression(Integer, str(int(tree.children[0])))


@parser.handler("float_literal")
def handle_float_literal(tree: Tree, _stack: Stack) -> Expression:
    return Expression(Real, str(float(tree.children[0])))


@parser.handler("bool_literal_true")
def handle_bool_literal_true(_tree: Tree, _stack: Stack) -> Expression:
    return Expression(Bool, "True")


@parser.handler("bool_literal_false")
def handle_bool_literal_false(_tree: Tree, _stack: Stack) -> Expression:
    return Expression(Bool, "False")


@parser.handler("variable")
def handle_variable(tree: Tree, stack: Stack) -> Expression:
    variable = stack.get_variable(tree.children[0])
    if variable is None:
        raise ValueError(f"Undefined symbol: '{tree.children[0]}'")
    var_name = "var_" + str(variable.number) if variable.number >= 0 else tree.children[0]
    return Expression(variable.type, var_name)


@parser.handler("type_int")
@parser.handler("type_real")
@parser.handler("type_bool")
@parser.handler("type_color")
@parser.handler("type_side")
def handle_scalar_type(tree: Tree, _stack: Stack) -> Type:
    return TYPE_NAMES[tree.data]


@parser.handler("type_list")
@parser.handler("type_set")
def handle_compound_type(tree: Tree, stack: Stack) -> Type:
    constructor = {"type_list": ListType, "type_set": Set}[tree.data]
    inner_type: Type = parser.handle(tree.children[0], stack)
    return constructor(inner_type)


@parser.handler("var_decl")
def handle_variable_declaration(tree: Tree, stack: Stack) -> List[Expression]:
    var_names: List[str] = []
    index = 0
    while isinstance(tree.children[index], str):
        var_names.append(tree.children[index])
        index += 1
    var_type: Type = parser.handle(tree.children[index], stack)
    nums = [stack.add_variable(name, var_type) for name in var_names]

    if index != len(tree.children) - 1:
        value: Expression = parser.handle(tree.children[index + 1], stack)
        if not (var_type.is_assignable(value.type)):
            raise ValueError(f"Value of type {value.type} cannot be assigned to variable of type {var_type}")
        return [Expression.merge(Void, ["var_" + str(num), " = ", 0], value) for num in nums]
    return [Expression(Void, ["var_" + str(num), " = ", var_type.default_value()]) for num in nums]


def handle_clause(tree: Tree, stack: Stack) -> List[Expression]:
    if tree.data == "clause":
        stack.add_frame()
        expressions = [parser.handle(subtree, stack) for subtree in tree.children]
        stack.pop_frame()
        return expressions
    else:
        stack.add_frame()
        expressions = [parser.handle(tree, stack)]
        stack.pop_frame()
        return expressions


@parser.handler("if_expression")
def handle_if_expression(tree: Tree, stack: Stack) -> Expression:
    condition = parser.handle(tree.children[0], stack)
    if not Bool.is_assignable(condition.type):
        raise ValueError("Only expression of boolean type can be used as an if condition")
    then_clause = handle_clause(tree.children[1], stack)
    if len(tree.children) > 2:
        else_clause = handle_clause(tree.children[2], stack)
    else:
        else_clause = []
    return ConditionExpression(condition, then_clause, else_clause)


@parser.handler("while_expression")
def handle_while_expression(tree: Tree, stack: Stack) -> Expression:
    condition = parser.handle(tree.children[0], stack)
    if not Bool.is_assignable(condition.type):
        raise ValueError("Only expression of boolean type can be used as a while condition")
    actions = handle_clause(tree.children[1], stack)
    return WhileLoopExpression(condition, actions)


@parser.handler("do_expression")
def handle_do_expression(tree: Tree, stack: Stack) -> Expression:
    condition = parser.handle(tree.children[1], stack)
    if not Bool.is_assignable(condition.type):
        raise ValueError("Only expression of boolean type can be used as a do-while condition")
    actions = handle_clause(tree.children[0], stack)
    return DoWhileLoopExpression(condition, actions)


@parser.handler("repeat_expression")
def handle_repeat_expression(tree: Tree, stack: Stack) -> Expression:
    iterations = parser.handle(tree.children[0], stack)
    if not Integer.is_assignable(iterations.type):
        raise ValueError("Iterations count must be integer")
    actions = handle_clause(tree.children[1], stack)
    return RepeatLoopExpression(iterations, actions)


@parser.handler("for_expression")
def handle_repeat_expression(tree: Tree, stack: Stack) -> Expression:
    var_name = tree.children[0]
    range_expression = parser.handle(tree.children[1], stack)
    range_type = range_expression.type
    if not isinstance(range_type, CollectionType):
        raise ValueError("For loop range must be a list or a set")

    in_stack = stack.get_variable(var_name)
    if in_stack is not None:
        if in_stack.number >= 0:
            var_name = "var_" + str(in_stack.number)
        if not in_stack.type.is_assignable(range_type.item_type):
            raise ValueError(f"Value of type {range_type} cannot be assigned to a for loop iterator of type "
                             f"{in_stack.type}")
        stack.add_frame()
    else:
        stack.add_frame()
        var_num = stack.add_variable(var_name, range_type.item_type)
        var_name = "var_" + str(var_num)

    if tree.children[2].data == "clause":
        actions = [parser.handle(subtree, stack) for subtree in tree.children[2].children]
    else:
        actions = [parser.handle(tree.children[2], stack)]
    stack.pop_frame()
    return ForLoopExpression(var_name, range_expression, actions)


@parser.handler("func_call")
def handle_func_call(tree: Tree, stack: Stack):
    def create_arg_list(count):
        if count > 0:
            yield 0
            for index in range(1, count):
                yield ", "
                yield index

    function_name: str = tree.children[0]
    func_data = stack.get_variable(function_name)
    if func_data is None:
        raise ValueError(f"Undefined symbol: {function_name}")

    func_type: Function = func_data.type
    if not isinstance(func_type, Function):
        raise ValueError(f"{function_name} is not a function")

    if func_data.number >= 0:
        function_name = "var_" + str(func_data.number)

    arguments = [parser.handle(x, stack) for x in tree.children[1:]]
    arg_types = [x.type for x in arguments]
    return_type = func_type.takes_arguments(arg_types)
    if return_type is None:
        raise ValueError(f"Function {function_name} does not accept arguments: {arg_types!r}")

    return Expression.merge(return_type, [function_name, "(", *create_arg_list(len(arguments)), ")"], *arguments)


@parser.handler("var_assignment")
def handle_var_assignment(tree: Tree, stack: Stack):
    var_name: str = tree.children[0]
    var_data = stack.get_variable(var_name)
    if var_data is None:
        raise ValueError(f"Undefined symbol: {var_data}")
    elif var_data.number < 0:
        raise ValueError(f"Attempting to read to readonly value {var_data}")

    expression: Expression = parser.handle(tree.children[1], stack)
    if not var_data.type.is_assignable(expression.type):
        raise ValueError(f"Value of type {expression.type} cannot be assigned to a varaible of type "
                         f"{var_data.type}")

    return Expression.merge(Void, ["var_" + str(var_data.number), " = ", 0], expression)
