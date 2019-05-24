from collections.abc import Iterable
from pathlib import Path
from typing import Union, List, Callable, Dict, IO, Iterator

from lark import Tree, Lark, Token

from .expression import Expression, ConditionExpression, WhileLoopExpression, \
    DoWhileLoopExpression, RepeatLoopExpression, ForLoopExpression, \
    CubeTurningExpression, CubeRotationExpression, FunctionDeclarationExpression
from .operators import BINARY_OPERATORS, BinaryOperator
from .stack import Stack
from .types import Integer, Real, Type, Bool, Set, List as ListType, Void, \
    CollectionType, Function, Color, Side, Pattern
from .errors import assert_type, ValueTypeError, UnresolvedReferenceError, \
    FunctionArgumentsError, CompileTimeError

TYPE_NAMES = {"type_int": Integer, "type_real": Real, "type_bool": Bool,
              "type_color": Color, "type_side": Side, "type_pattern": Pattern}

Callback = Callable[[Tree, Stack], Union[Type, Expression]]


class Parser:
    def __init__(self):
        path = Path(__file__).parents[2] / "data" / "syntax.lark"
        with open(str(path)) as f:
            grammar = Parser._generate_operators(BINARY_OPERATORS) + f.read()
        self.lark = Lark(grammar, start="clause", propagate_positions=True)
        self.callbacks: Dict[str, Callback] = dict()

    @staticmethod
    def _generate_operators(operator_groups: List[List[BinaryOperator]]) -> str:
        lines = []
        for op_index, op in enumerate(operator_groups):
            this_name = "op_" + str(op_index)
            next_name = "op_" + str(op_index + 1) if op_index < len(operator_groups) - 1 else "op_if"
            lines.append(f"?{this_name}: {next_name} | ")
            lines.append(" | ".join(f"{this_name} \"{op.symbol}\" {next_name} -> op_{op_index}_{index}"
                                    for index, op in enumerate(op)))
            lines.append("\n")
        return "".join(lines)

    def handler(self, *names: str) -> Callable[[Callback], Callback]:
        def wrapper(func: Callback) -> Callback:
            for name in names:
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
                message = f"Operator '{op.symbol}' is not applicable to values"\
                          f" of type {arg_types[0]} and {arg_types[1]}"
                raise CompileTimeError(tree, message)


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
        raise UnresolvedReferenceError(tree.children[0])
    var_name = "var_" + str(variable.number) if variable.number >= 0 else tree.children[0]
    return Expression(variable.type, var_name)


@parser.handler("type_int", "type_real", "type_bool", "type_color", "type_side", "type_pattern")
def handle_scalar_type(tree: Tree, _stack: Stack) -> Type:
    return TYPE_NAMES[tree.data]


@parser.handler("type_list", "type_set")
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
        assert_type(tree.children[index + 1], value, var_type)
        return [Expression.merge(Void, ["var_" + str(num), " = ", 0], value) for num in nums]
    return [Expression(Void, ["var_" + str(num), " = ", var_type.default_value()]) for num in nums]


def flatten(x):
    if isinstance(x, Iterable):
        for y in x:
            yield from flatten(y)
    else:
        yield x


def handle_clause(tree: Tree, stack: Stack) -> List[Expression]:
    if tree.data == "clause":
        stack.add_frame()
        expressions = list(flatten(parser.handle(subtree, stack) for subtree in tree.children))
        stack.pop_frame()
        return expressions
    else:
        stack.add_frame()
        expressions = list(flatten(parser.handle(tree, stack)))
        stack.pop_frame()
        return expressions


@parser.handler("if_expression")
def handle_if_expression(tree: Tree, stack: Stack) -> Expression:
    actions = []
    for j in range(0, len(tree.children) - 1, 2):
        condition = parser.handle(tree.children[j], stack)
        assert_type(tree.children[j], condition, Bool,
                    "Only expression of boolean type can be used as an if condition")
        then_clause = handle_clause(tree.children[j + 1], stack)
        actions.append((condition, then_clause))

    if len(tree.children) % 2 == 1:
        else_clause = handle_clause(tree.children[-1], stack)
    else:
        else_clause = []
    return ConditionExpression(actions, else_clause)


@parser.handler("while_expression")
def handle_while_expression(tree: Tree, stack: Stack) -> Expression:
    condition = parser.handle(tree.children[0], stack)
    assert_type(tree.children[0], condition, Bool,
                "Only expression of boolean type can be used as a while condition")
    actions = handle_clause(tree.children[1], stack)
    return WhileLoopExpression(condition, actions)


@parser.handler("do_expression")
def handle_do_expression(tree: Tree, stack: Stack) -> Expression:
    condition = parser.handle(tree.children[1], stack)
    assert_type(tree.children[1], condition, Bool,
                "Only expression of boolean type can be used as a do-while condition")
    actions = handle_clause(tree.children[0], stack)
    return DoWhileLoopExpression(condition, actions)


@parser.handler("repeat_expression")
def handle_repeat_expression(tree: Tree, stack: Stack) -> Expression:
    iterations = parser.handle(tree.children[0], stack)
    assert_type(tree.children[0], iterations, Integer,
                "Iterations count must be integer")
    actions = handle_clause(tree.children[1], stack)
    return RepeatLoopExpression(iterations, actions)


@parser.handler("for_expression")
def handle_repeat_expression(tree: Tree, stack: Stack) -> Expression:
    var_name = tree.children[0]
    range_expression = parser.handle(tree.children[1], stack)
    range_type: CollectionType = range_expression.type

    if not isinstance(range_type, CollectionType):
        raise ValueTypeError(tree.children[1], "For loop range must be a list or a set", None, range_type)

    in_stack = stack.get_variable(var_name)
    if in_stack is not None:
        if in_stack.number >= 0:
            var_name = "var_" + str(in_stack.number)
        assert_type(tree.children[1], range_type.item_type, in_stack.type,
                    f"Value of type {range_type.item_type} cannot be assigned to a for "
                    f"loop iterator of type {in_stack.type}")
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

    function_name = tree.children[0]
    func_data = stack.get_variable(function_name)
    if func_data is None:
        raise UnresolvedReferenceError(function_name)

    func_type: Function = func_data.type
    if not isinstance(func_type, Function):
        raise ValueTypeError(function_name, f"{function_name} is not a function", None, func_type)

    if func_data.number >= 0:
        function_name = "var_" + str(func_data.number)

    arguments = [parser.handle(x, stack) for x in tree.children[1:]]
    arg_types = [x.type for x in arguments]
    return_type = func_type.takes_arguments(arg_types)
    if return_type is None:
        raise FunctionArgumentsError(tree, function_name, func_type, arg_types)
    return Expression.merge(return_type, [function_name, "(", *create_arg_list(len(arguments)), ")"], *arguments)


@parser.handler("var_assignment")
def handle_var_assignment(tree: Tree, stack: Stack):
    var_name = tree.children[0]
    expression: Expression = parser.handle(tree.children[1], stack)

    if isinstance(var_name, Token):
        var_data = stack.get_variable(var_name)
        if var_data is None:
            raise UnresolvedReferenceError(var_name)
        elif var_data.number < 0:
            raise CompileTimeError(tree, f"Attempting to write to readonly value {var_data}")
        var_type = var_data.type
        result = Expression.merge(Void, ["var_" + str(var_data.number), " = ", 0], expression)
    else:
        # var_name is an array item reference
        var_expression = parser.handle(var_name, stack)
        var_type = var_expression.type
        result = Expression.merge(Void, [0, " = ", 1], var_expression, expression)

    assert_type(tree.children[1], expression, var_type,
                f"Value of type {expression.type} cannot be assigned to a varaible "
                f"of type {var_type}")
    return result


@parser.handler("collection_item")
def handle_collection_item(tree: Tree, stack: Stack):
    list_reference: Expression = parser.handle(tree.children[0], stack)
    list_type = list_reference.type
    if not isinstance(list_type, ListType):
        raise ValueTypeError(tree.children[0], f"{list_reference.type} is not a list",
                             None, tree.children)

    index: Expression = parser.handle(tree.children[1], stack)
    assert_type(tree.children[1], index, Integer,
                f"List index must be of type int, not {index.type}")
    return Expression.merge(list_type.item_type, ["(", 0, ")[", 1, "]"], list_reference, index)


@parser.handler("cube_right", "cube_left", "cube_top", "cube_bottom", "cube_front", "cube_back")
def handle_cube_turning(tree: Tree, _stack: Stack):
    side = tree.data[5:]
    return CubeTurningExpression(side, 1)


@parser.handler("cube_rotate_right", "cube_rotate_top", "cube_rotate_front")
def handle_cube_rotation(tree: Tree, _stack: Stack):
    side = tree.data[12:]
    return CubeRotationExpression(side, False)


@parser.handler("cube_double", "cube_opposite")
def handle_cube_turning_double(tree: Tree, stack: Stack):
    expression = parser.handle(tree.children[0], stack)
    if isinstance(expression, CubeTurningExpression):
        expression.amount = 2 if tree.data == "cube_double" else 3
    else:
        assert isinstance(expression, CubeRotationExpression)
        if tree.data == "cube_double":
            expression.twice = True
        else:
            opposites = ("front", "back"), ("left", "right"), ("top", "bottom")
            for a, b in opposites:
                if expression.side == a:
                    expression.side = b
                    break
                elif expression.side == b:
                    expression.side = a
                    break
    return expression


@parser.handler("cube_color_reference")
def handle_dereference(tree: Tree, stack: Stack):
    side_expression: Expression = parser.handle(tree.children[0], stack)
    assert_type(tree.children[0], side_expression, Side)

    index1: Expression = parser.handle(tree.children[1], stack)
    assert_type(tree.children[1], index1, Integer, "Cube side indices must be integers")

    index2: Expression = parser.handle(tree.children[2], stack)
    assert_type(tree.children[2], index2, Integer, "Cube side indices must be integers")

    return Expression.merge(Color, ["cube_get_color(", 0, ", ", 1, ", ", 2, ")"],
                            side_expression, index1, index2)


@parser.handler("cube_instruction")
def handle_cube_instruction(tree: Tree, stack: Stack):
    return [parser.handle(m, stack) for m in tree.children]


@parser.handler("pattern")
def handle_pattern(tree: Tree, _stack: Stack):
    colors = {"G": "green", "R": "red", "O": "orange", "Y": "yellow",
              "W": "white", "B": "blue", "-": "None"}

    text = tree.children[0].split("/")
    pattern_lines = []
    for line in text:
        pattern_line = []
        if len(line) != len(text[0]):
            raise CompileTimeError(tree, "Inconsistent line length in pattern literal")
        for char in line:
            if char in colors:
                pattern_line.append(colors[char])
            else:
                pattern_line.append('"' + char + '"')
        pattern_lines.append("[" + ", ".join(pattern_line) + "]")

    pattern_array = ', '.join(pattern_lines)
    return Expression(Pattern, [f"Pattern([{pattern_array}])"])


@parser.handler("orient_params")
def handle_orient_params(tree: Tree, stack: Stack):
    assert len(tree.children) % 2 == 0
    expression = ["orient("]
    merging = []
    previous_keys = set()
    patterns_present = False

    for j in range(0, len(tree.children), 2):
        key = tree.children[j]
        expression.append(key + "=")
        expression.append(j // 2)
        argument = parser.handle(tree.children[j + 1], stack)
        merging.append(argument)
        if key in previous_keys:
            raise CompileTimeError(key, f"Key {key} has already been specified")
        elif key == "keeping":
            assert_type(tree.children[j + 1], argument, Side)
        else:
            patterns_present = True
            assert_type(tree.children[j + 1], argument, Pattern)
        previous_keys.add(key)
        expression.append(", ")

    expression[-1] = ")"
    if not patterns_present:
        raise CompileTimeError(tree, "No side patterns are present")
    return Expression.merge(Bool, expression, *merging)


@parser.handler("func_decl")
def handle_function_declaration(tree: Tree, stack: Stack):
    func_name = tree.children[0]
    inner_stack = stack.create_inner()

    argument_names: List[str] = []
    argument_types: List[Type] = []
    i = 1
    while tree.children[i].data == "argument":
        arg_node = tree.children[i]
        argument_names.append(arg_node.children[0])
        type = parser.handle(arg_node.children[1], stack)
        argument_types.append(type)
        inner_stack.add_variable(arg_node.children[0], type)
        i += 1

    if tree.children[i].data == "clause":
        return_type = Void
    else:
        return_type = parser.handle(tree.children[i], stack)

    func_type = Function((argument_types, return_type))
    var_num = stack.add_variable(func_name, func_type)
    clause = handle_clause(tree.children[-1], inner_stack)
    return FunctionDeclarationExpression(f"var_{var_num}", return_type, argument_names, clause)
