import lark
import pytest

from libcube.compiler.parser import parser, BinaryOperator
from libcube.compiler.expression import Expression, ConditionExpression, \
    WhileLoopExpression, DoWhileLoopExpression, RepeatLoopExpression, \
    ForLoopExpression, CubeTurningExpression, CubeRotationExpression, \
    FunctionDeclarationExpression
from libcube.compiler.stack import Stack
from libcube.compiler.errors import ValueTypeError, UnresolvedReferenceError, \
    FunctionArgumentsError, CompileTimeError
from libcube.compiler.types import Integer, Real, Type, Bool, List, Set, Void, \
    Function, Color, Side, Pattern
import typing


def test_operator_generation():
    operators = [
        [BinaryOperator("a", [], []), BinaryOperator("b", [], [])],
        [BinaryOperator("c", [], [])],
        [BinaryOperator("e", [], []), BinaryOperator("f", [], []), BinaryOperator("g", [], [])]
    ]
    actual = parser._generate_operators(operators)
    print(actual)
    assert actual == ("?op_0: op_1 | op_0 \"a\" op_1 -> op_0_0 | op_0 \"b\" op_1 -> op_0_1\n"
                      "?op_1: op_2 | op_1 \"c\" op_2 -> op_1_0\n"
                      "?op_2: op_if | op_2 \"e\" op_if -> op_2_0 | op_2 \"f\" op_if -> op_2_1 | "
                      "op_2 \"g\" op_if -> op_2_2\n")


def tr(name: str, *children: typing.Union[lark.Tree, str]) -> typing.Union[lark.Tree, lark.Token]:
    return lark.Tree(name, [lark.Token("", x) if isinstance(x, str) else x
                            for x in children])


@pytest.mark.parametrize("name, value, exp_type, exp_value", [
    ("int_literal", "1", Integer, "1"),
    ("float_literal", "1.4", Real, "1.4")
])
def test_literal(name: str, value: str, exp_type: Type, exp_value: str):
    tree = tr(name, value)
    expr = parser.handle(tree, Stack())
    assert isinstance(expr, Expression)
    assert expr.type == exp_type
    assert expr.expression == [exp_value]
    assert expr.intermediates == []


class TestOperators:
    @pytest.mark.parametrize("op1_type, op2_type, op_name, res_type, res_expr", [
        ("int_literal", "int_literal", "op_5_0", Integer, "(1) + (2)"),
        ("float_literal", "int_literal", "op_5_0", Real, "(1.0) + (2)"),
        ("int_literal", "float_literal", "op_5_0", Real, "(1) + (2.0)"),
        ("int_literal", "int_literal", "op_6_1", Real, "(1) / (2)")
    ])
    def test_operators(self, op1_type: str, op2_type: str, op_name: str, res_type: Type, res_expr: str):
        tree = tr(op_name, tr(op1_type, "1"), tr(op2_type, "2"))

        expr: Expression = parser.handle(tree, Stack())
        assert expr.type == res_type
        assert expr.intermediates == []
        assert "".join(expr.expression) == res_expr

    @pytest.mark.parametrize("operator, arg1, arg2", [
        ("op_5_0", tr("float_literal", "1"), tr("bool_literal_true")),
        ("op_5_0", tr("bool_literal_true"), tr("float_literal", "2"))
    ])
    def test_wrong_operand(self, operator, arg1, arg2):
        tree = tr(operator, arg1, arg2)
        with pytest.raises(CompileTimeError):
            parser.handle(tree, Stack())

    @pytest.mark.parametrize("arg1, arg2", [
        (Bool, Bool), (Integer, Integer), (List(Integer), List(Integer))
    ])
    def test_comparision_correct(self, arg1, arg2):
        tree = tr("op_3_0", tr("variable", "a"), tr("variable", "b"))
        stack = Stack()
        stack.add_global("a", arg1)
        stack.add_global("b", arg2)
        expr: Expression = parser.handle(tree, stack)
        assert expr.type == Bool

    @pytest.mark.parametrize("arg1, arg2", [
        (Bool, Void), (Void, Integer), (Void, Void), (Integer, Real),
        (Real, Integer), (List(Bool), Set(Bool)), (List(Integer), Set(Integer))
    ])
    def test_comparision_incorrect(self, arg1, arg2):
        tree = tr("op_3_0", tr("variable", "a"), tr("variable", "b"))
        stack = Stack()
        stack.add_global("a", arg1)
        stack.add_global("b", arg2)
        with pytest.raises(CompileTimeError):
            parser.handle(tree, stack)


def test_variable_exist():
    tree = tr("variable", "a")
    stack = Stack()
    stack.add_variable("a", Integer)
    expression: Expression = parser.handle(tree, stack)
    assert expression.type == Integer
    assert expression.expression == ["var_0"]


def test_global_variable_exist():
    tree = tr("variable", "a")
    stack = Stack()
    stack.add_global("a", Real)
    expression: Expression = parser.handle(tree, stack)
    assert expression.type == Real
    assert expression.expression == ["a"]


def test_undefined_variable():
    tree = tr("variable", "a")
    with pytest.raises(UnresolvedReferenceError):
        parser.handle(tree, Stack())


@pytest.mark.parametrize("tree, expected", [
    (tr("type_int"), Integer),
    (tr("type_real"), Real),
    (tr("type_bool"), Bool),
    (tr("type_side"), Side),
    (tr("type_color"), Color),
    (tr("type_pattern"), Pattern),
    (tr("type_list", tr("type_bool")), List(Bool)),
    (tr("type_set", tr("type_real")), Set(Real)),
])
def test_type_handle(tree: lark.Tree, expected: Type):
    assert parser.handle(tree, Stack()) == expected


def test_var_declaration():
    tree = tr("var_decl", "a", "b", "c", tr("type_int"))
    stack = Stack()

    expressions = parser.handle(tree, stack)
    for i, value in enumerate(expressions):
        assert value.type == Void
        assert value.expression == ["var_" + str(i), " = ", "0"]

    assert stack.get_variable("a").type == Integer
    assert stack.get_variable("b").type == Integer
    assert stack.get_variable("c").type == Integer


def test_var_declaration_value():
    tree = tr("var_decl", "a", "b", "c", tr("type_int"), tr("int_literal", "1"))
    stack = Stack()

    values: typing.List[Expression] = parser.handle(tree, stack)
    for i, value in enumerate(values):
        assert value.type == Void
        assert value.expression == ["var_" + str(i), " = ", "1"]

    assert stack.get_variable("a").type == Integer
    assert stack.get_variable("b").type == Integer
    assert stack.get_variable("c").type == Integer


def test_var_declaration_wrong_type():
    tree = tr("var_decl", "a", tr("type_int"), tr("float_literal", "1"))
    with pytest.raises(ValueTypeError):
        parser.handle(tree, Stack())


def test_if_expression():
    tree = tr("if_expression",
              tr("bool_literal_true"),
              tr("clause", tr("int_literal", "1"), tr("float_literal", "2")))
    expression = parser.handle(tree, Stack())
    assert isinstance(expression, ConditionExpression)
    assert expression.type == Void

    intermediate = expression.intermediates[0]
    assert isinstance(intermediate, ConditionExpression.Intermediate)
    assert intermediate.actions[0][0].expression == ["True"]
    assert intermediate.actions[0][1][0].expression == ["1"]
    assert intermediate.actions[0][1][1].expression == ["2.0"]
    assert len(intermediate.else_clause) == 0


def test_if_elseif():
    tree = tr("if_expression",
              tr("bool_literal_true"),
              tr("int_literal", "1"),
              tr("bool_literal_false"),
              tr("int_literal", "2"))
    expression = parser.handle(tree, Stack())
    assert isinstance(expression, ConditionExpression)
    assert expression.type == Void

    intermediate = expression.intermediates[0]
    assert isinstance(intermediate, ConditionExpression.Intermediate)
    assert intermediate.actions[0][0].expression == ["True"]
    assert intermediate.actions[0][1][0].expression == ["1"]
    assert intermediate.actions[1][0].expression == ["False"]
    assert intermediate.actions[1][1][0].expression == ["2"]
    assert len(intermediate.else_clause) == 0


def test_if_elseif_else():
    tree = tr("if_expression",
              tr("bool_literal_true"),
              tr("int_literal", "1"),
              tr("bool_literal_false"),
              tr("int_literal", "2"),
              tr("float_literal", "3.1"))
    expression = parser.handle(tree, Stack())
    assert isinstance(expression, ConditionExpression)
    assert expression.type == Real

    intermediate = expression.intermediates[0]
    assert isinstance(intermediate, ConditionExpression.Intermediate)
    assert intermediate.actions[0][0].expression == ["True"]
    assert intermediate.actions[0][1][0].expression == ["1"]
    assert intermediate.actions[1][0].expression == ["False"]
    assert intermediate.actions[1][1][0].expression == ["2"]
    assert intermediate.else_clause[0].expression == ["3.1"]


def test_if_else_expression():
    tree = tr("if_expression",
              tr("bool_literal_false"),
              tr("int_literal", "1"),
              tr("clause", tr("float_literal", "2")))
    expression = parser.handle(tree, Stack())
    assert isinstance(expression, ConditionExpression)
    assert expression.type == Real

    intermediate = expression.intermediates[0]
    assert isinstance(intermediate, ConditionExpression.Intermediate)
    assert intermediate.actions[0][0].expression == ["False"]
    assert intermediate.actions[0][1][0].expression == ["1"]
    assert intermediate.else_clause[0].expression == ["2.0"]


def test_if_wrong_type():
    tree = tr("if_expression",
              tr("int_literal", "1"),
              tr("float_literal", "2"),
              tr("float_literal", "3"))
    with pytest.raises(ValueTypeError):
        parser.handle(tree, Stack())


def test_while():
    tree = tr("while_expression",
              tr("bool_literal_true"),
              tr("int_literal", "1"))
    expression = parser.handle(tree, Stack())
    assert isinstance(expression, WhileLoopExpression)
    assert expression.type == Void

    intermediate = expression.intermediates[0]
    assert isinstance(intermediate, WhileLoopExpression.Intermediate)
    assert intermediate.condition.expression == ["True"]
    assert intermediate.actions[0].expression == ["1"]


def test_while_type_error():
    with pytest.raises(ValueTypeError):
        parser.handle(tr("while_expression",
                         tr("int_literal", "2"),
                         tr("int_literal", "1")), Stack())


def test_do_while():
    tree = tr("do_expression",
              tr("int_literal", "2"),
              tr("bool_literal_true"))
    expression = parser.handle(tree, Stack())
    assert isinstance(expression, DoWhileLoopExpression)
    assert expression.type == Void

    intermediate = expression.intermediates[0]
    assert isinstance(intermediate, DoWhileLoopExpression.Intermediate)
    assert intermediate.condition.expression == ["True"]
    assert intermediate.actions[0].expression == ["2"]


def test_do_while_type_error():
    with pytest.raises(ValueTypeError):
        parser.handle(tr("do_expression",
                         tr("int_literal", "2"),
                         tr("int_literal", "1")), Stack())


def test_repeat():
    tree = tr("repeat_expression",
              tr("int_literal", "2"),
              tr("bool_literal_true"))
    expression = parser.handle(tree, Stack())
    assert isinstance(expression, RepeatLoopExpression)
    assert expression.type == Void

    intermediate = expression.intermediates[0]
    assert isinstance(intermediate, RepeatLoopExpression.Intermediate)
    assert intermediate.times.expression == ["2"]
    assert intermediate.actions[0].expression == ["True"]


def test_repeat_error():
    with pytest.raises(ValueTypeError):
        parser.handle(tr("repeat_expression",
                         tr("float_literal", "2"),
                         tr("int_literal", "1")), Stack())


def test_for_loop_existing_var():
    stack = Stack()
    stack.add_variable("var", Real)
    stack.add_variable("range", List(Integer))
    tree = tr("for_expression",
              "var",
              tr("variable", "range"),
              tr("int_literal", "1"))
    expression = parser.handle(tree, stack)
    assert isinstance(expression, ForLoopExpression)
    intermediate = expression.intermediates[0]
    assert isinstance(intermediate, ForLoopExpression.Intermediate)
    assert intermediate.iterator == "var_0"
    assert intermediate.range.expression == ["var_1"]
    assert intermediate.actions[0].expression == ["1"]


def test_for_loop_new_var():
    stack = Stack()
    stack.add_variable("range", List(Integer))
    tree = tr("for_expression",
              "var",
              tr("variable", "range"),
              tr("clause", tr("int_literal", "1"), tr("variable", "var")))
    expression = parser.handle(tree, stack)
    assert isinstance(expression, ForLoopExpression)
    intermediate = expression.intermediates[0]
    assert isinstance(intermediate, ForLoopExpression.Intermediate)
    assert intermediate.iterator == "var_1"
    assert intermediate.range.expression == ["var_0"]
    assert intermediate.actions[0].expression == ["1"]
    assert intermediate.actions[1].expression == ["var_1"]
    assert intermediate.actions[1].type == Integer


def test_for_loop_wrong_range():
    with pytest.raises(ValueTypeError):
        tree = tr("for_expression",
                  "var",
                  tr("int_literal", "1"),
                  tr("int_literal", "1"))
        parser.handle(tree, Stack())


def test_for_loop_wrong_iterator_type():
    with pytest.raises(ValueTypeError):
        stack = Stack()
        stack.add_variable("var", Bool)
        stack.add_variable("range", List(Integer))
        tree = tr("for_expression",
                  "var",
                  tr("variable", "range"),
                  tr("int_literal", "1"))
        parser.handle(tree, stack)


class TestFunctionCall:
    @pytest.mark.parametrize("is_global", [(True,), (False,)])
    def test_function_call(self, is_global):
        stack = Stack()
        stack.add_variable("array", List(Integer))
        func = Function(([Integer, Real, List(Integer)], Void))
        if is_global:
            stack.add_global("func", func)
        else:
            stack.add_variable("func", func)

        tree = tr("func_call",
                  "func",
                  tr("int_literal", "1"),
                  tr("int_literal", "2"),
                  tr("variable", "array"))
        expression = parser.handle(tree, stack)

        assert expression.type == Void
        func_name = "func" if is_global else "var_1"
        assert expression.expression == [func_name, "(", "1", ", ", "2", ", ", "var_0", ")"]

    def test_no_args(self):
        stack = Stack()
        stack.add_global("func", Function(([], Integer)))
        tree = tr("func_call", "func")
        expression = parser.handle(tree, stack)

        assert expression.type == Integer
        assert expression.expression == ["func", "()"]

    def test_invalid_name(self):
        with pytest.raises(UnresolvedReferenceError):
            tree = tr("func_call", "func")
            parser.handle(tree, Stack())

    def test_invalid_arguments_count_few(self):
        with pytest.raises(FunctionArgumentsError):
            stack = Stack()
            stack.add_variable("func", Function(([Integer, Integer], Integer)))
            tree = tr("func_call", "func", tr("int_literal", "1"))
            parser.handle(tree, stack)

    def test_invalid_arguments_count_many(self):
        with pytest.raises(FunctionArgumentsError):
            stack = Stack()
            stack.add_variable("func", Function(([Integer, Integer], Integer)))
            tree = tr("func_call", "func", tr("int_literal", "1"), tr("int_literal", "1"),
                      tr("int_literal", "1"))
            parser.handle(tree, stack)

    def test_invalid_argument_types(self):
        with pytest.raises(FunctionArgumentsError):
            stack = Stack()
            stack.add_variable("var", Set(Real))
            stack.add_variable("func", Function((([Integer, List(Integer)]), Integer)))
            tree = tr("func_call", "func", tr("int_literal", "1"), tr("variable", "var"))
            parser.handle(tree, stack)


class TestVarAssignment:
    def test_var_assignment(self):
        stack = Stack()
        stack.add_variable("var", Real)
        tree = tr("var_assignment", "var", tr("int_literal", "42"))
        expression = parser.handle(tree, stack)
        assert expression.expression == ["var_0", " = ", "42"]

    def test_readonly(self):
        stack = Stack()
        stack.add_global("var", Real)
        tree = tr("var_assignment", "var", tr("int_literal", "0"))
        with pytest.raises(CompileTimeError):
            parser.handle(tree, stack)

    def test_undefined(self):
        tree = tr("var_assignment", "var", tr("int_literal", "0"))
        with pytest.raises(UnresolvedReferenceError):
            parser.handle(tree, Stack())

    def test_type_error(self):
        stack = Stack()
        stack.add_global("var", List(Integer))
        tree = tr("var_assignment", "var", tr("int_literal", "0"))
        with pytest.raises(CompileTimeError):
            parser.handle(tree, stack)

    def test_list(self):
        stack = Stack()
        stack.add_global("a", List(Real))
        tree = tr("var_assignment",
                  tr("collection_item", tr("variable", "a"), tr("int_literal", "2")),
                  tr("int_literal", "42"))
        expression = parser.handle(tree, stack)
        assert expression.expression == ["(", "a", ")[", "2", "]", " = ", "42"]

    def test_list_type_error(self):
        stack = Stack()
        stack.add_global("a", List(Bool))
        tree = tr("var_assignment",
                  tr("collection_item", tr("variable", "a"), tr("int_literal", "2")),
                  tr("int_literal", "42"))
        with pytest.raises(ValueTypeError):
            parser.handle(tree, stack)


def test_list_reference():
    stack = Stack()
    stack.add_global("a", List(Bool))
    tree = tr("collection_item",
              tr("variable", "a"),
              tr("int_literal", "12"))
    expression = parser.handle(tree, stack)
    assert expression.expression == ["(", "a", ")[", "12", "]"]
    assert expression.type == Bool


def test_list_reference_not_array():
    stack = Stack()
    stack.add_global("a", Real)
    tree = tr("collection_item", tr("variable", "a"), tr("int_literal", "12"))
    with pytest.raises(ValueTypeError):
        parser.handle(tree, stack)


def test_list_reference_wrong_index_type():
    stack = Stack()
    stack.add_global("a", List(Integer))
    tree = tr("collection_item", tr("variable", "a"), tr("float_literal", "12.2"))
    with pytest.raises(ValueTypeError):
        parser.handle(tree, stack)


class TestCubeTurns:
    @pytest.mark.parametrize("data, side", [
        ("cube_top", "top"), ("cube_bottom", "bottom"),
        ("cube_left", "left"), ("cube_right", "right"),
        ("cube_front", "front"), ("cube_back", "back")
    ])
    def test_cube_turning(self, data, side):
        tree = tr(data)
        expr = parser.handle(tree, Stack())
        assert isinstance(expr, CubeTurningExpression)
        assert expr.side == side
        assert expr.amount == 1

    @pytest.mark.parametrize("data, amount", [
        ("cube_double", 2), ("cube_opposite", 3)
    ])
    def test_cube_turning_amount(self, data, amount):
        tree = tr(data, tr("cube_front"))
        expr = parser.handle(tree, Stack())
        assert isinstance(expr, CubeTurningExpression)
        assert expr.side == "front"
        assert expr.amount == amount

    def test_indices_single(self):
        tree = tr("cube_turn_range", tr("cube_left"), tr("range_value", tr("int_literal", "1")))
        expr = parser.handle(tree, Stack())
        assert isinstance(expr, CubeTurningExpression)
        assert expr.side == "left"
        assert len(expr.indices) == 1
        assert expr.indices[0].expression == ["1"]

    def test_indices_left(self):
        tree = tr("cube_turn_range", tr("cube_left"), tr("range_open_left", tr("int_literal", "1")))
        expr = parser.handle(tree, Stack())
        assert isinstance(expr, CubeTurningExpression)
        assert len(expr.indices) == 2
        assert expr.indices[0].expression == ["..."]
        assert expr.indices[1].expression == ["1"]

    def test_indices_right(self):
        tree = tr("cube_turn_range", tr("cube_left"), tr("range_open_right", tr("int_literal", "1")))
        expr = parser.handle(tree, Stack())
        assert isinstance(expr, CubeTurningExpression)
        assert len(expr.indices) == 2
        assert expr.indices[0].expression == ["1"]
        assert expr.indices[1].expression == ["..."]

    def test_indices_both(self):
        tree = tr("cube_turn_range", tr("cube_left"), tr("range_closed", tr("int_literal", "1"), tr("int_literal", "3")))
        expr = parser.handle(tree, Stack())
        assert isinstance(expr, CubeTurningExpression)
        assert len(expr.indices) == 3
        assert expr.indices[0].expression == ["1"]
        assert expr.indices[1].expression == ["..."]
        assert expr.indices[2].expression == ["3"]

    def test_indices_multiple(self):
        tree = tr("cube_turn_range", tr("cube_left"),
                  tr("range_open_left", tr("int_literal", "1")),
                  tr("range_value", tr("int_literal", "2")))
        expr = parser.handle(tree, Stack())
        assert isinstance(expr, CubeTurningExpression)
        assert len(expr.indices) == 3
        assert expr.indices[0].expression == ["..."]
        assert expr.indices[1].expression == ["1"]
        assert expr.indices[2].expression == ["2"]

    def test_wrong_type_1(self):
        tree = tr("cube_turn_range", tr("cube_left"),
                  tr("range_left", tr("float_literal", "2")))
        with pytest.raises(ValueTypeError):
            parser.handle(tree, Stack())

    def test_wrong_type_2(self):
        tree = tr("cube_turn_range", tr("cube_left"),
                  tr("range_close", tr("int_literal", "1"), tr("float_literal", "2")))
        with pytest.raises(ValueTypeError):
            parser.handle(tree, Stack())


class TestCubeRotations:
    @pytest.mark.parametrize("data, side", [
        ("cube_rotate_right", "right"), ("cube_rotate_top", "top"),
        ("cube_rotate_front", "front")
    ])
    def test_cube_rotation(self, data, side):
        tree = tr(data)
        expr = parser.handle(tree, Stack())
        assert isinstance(expr, CubeRotationExpression)
        assert expr.side == side
        assert not expr.twice

    def test_cube_rotation_amount(self):
        tree = tr("cube_double", tr("cube_rotate_top"))
        expr = parser.handle(tree, Stack())
        assert isinstance(expr, CubeRotationExpression)
        assert expr.side == "top"
        assert expr.twice

    @pytest.mark.parametrize("data, side", [
        ("cube_rotate_right", "left"), ("cube_rotate_top", "bottom"),
        ("cube_rotate_front", "back")
    ])
    def test_cube_rotation_opposite(self, data, side):
        tree = tr("cube_opposite", tr(data))
        expr = parser.handle(tree, Stack())
        assert isinstance(expr, CubeRotationExpression)
        assert expr.side == side


class TestColorReference:
    tree = tr("cube_color_reference",
              tr("variable", "a"),
              tr("variable", "b"),
              tr("variable", "c"))

    @staticmethod
    def create_stack(a: Type, b: Type, c: Type) -> Stack:
        stack = Stack()
        stack.add_global("a", a)
        stack.add_global("b", b)
        stack.add_global("c", c)
        return stack

    def test_normal(self):
        stack = self.create_stack(Side, Integer, Integer)
        expr = parser.handle(TestColorReference.tree, stack)
        assert expr.type == Color
        assert "".join(expr.expression) == "cube_get_color(a, b, c)"

    def test_side_invalid_type_1(self):
        stack = self.create_stack(Color, Integer, Integer)
        with pytest.raises(ValueTypeError):
            parser.handle(TestColorReference.tree, stack)

    def test_side_invalid_type_2(self):
        stack = self.create_stack(Side, Real, Integer)
        with pytest.raises(ValueTypeError):
            parser.handle(TestColorReference.tree, stack)

    def test_side_invalid_type_3(self):
        stack = self.create_stack(Side, Integer, Real)
        with pytest.raises(ValueTypeError):
            parser.handle(TestColorReference.tree, stack)


class TestPatterns:
    def test_valid(self):
        tree = tr("pattern", "-RG/-rg/rrO")
        expr: Expression = parser.handle(tree, Stack())
        assert expr.type == Pattern
        assert expr.expression == ['Pattern([[None, red, green], [None, "r", "g"], ["r", "r", orange]])']

    def test_inconsisted_line_lengths(self):
        tree = tr("pattern", "-RG/-/rrO")
        with pytest.raises(CompileTimeError):
            parser.handle(tree, Stack())


class TestOrientParameters:
    @staticmethod
    def create_stack():
        stack = Stack()
        stack.add_global("a", Pattern)
        stack.add_global("b", Pattern)
        stack.add_global("c", Side)
        return stack

    def test_valid(self):
        tree = tr("orient_params",
                  "front", tr("variable", "a"),
                  "left", tr("variable", "b"),
                  "keeping", tr("variable", "c"))
        expr = parser.handle(tree, self.create_stack())

        assert expr.expression == ["orient(", "front=", "a", ", ", "left=", "b", ", ", "keeping=", "c", ")"]
        assert expr.type == Bool

    def test_invalid_keeping_type(self):
        tree = tr("orient_params",
                  "front", tr("variable", "a"),
                  "keeping", tr("variable", "a"))
        with pytest.raises(ValueTypeError):
            parser.handle(tree, self.create_stack())

    def test_invalid_pattern_type(self):
        tree = tr("orient_params",
                  "front", tr("variable", "c"),
                  "keeping", tr("variable", "c"))
        with pytest.raises(ValueTypeError):
            parser.handle(tree, self.create_stack())

    def test_no_pattern_params(self):
        tree = tr("orient_params", "keeping", tr("variable", "c"))
        with pytest.raises(CompileTimeError):
            parser.handle(tree, self.create_stack())

    def test_duplicate_params(self):
        tree = tr("orient_params",
                  "front", tr("variable", "a"),
                  "front", tr("variable", "b"))
        with pytest.raises(CompileTimeError):
            parser.handle(tree, self.create_stack())


class TestFunctionDeclaration:
    def test_default(self):
        tree = tr("func_decl", "func_name",
                  tr("argument", "a", tr("type_int")),
                  tr("argument", "b", tr("type_real")),
                  tr("type_bool"),
                  tr("clause", tr("variable", "a"), tr("variable", "b")))
        stack = Stack()
        expression = parser.handle(tree, stack)
        assert isinstance(expression, FunctionDeclarationExpression)
        assert expression.name == "var_0"
        assert expression.symbol_name == "func_name"
        assert expression.arguments == ["var_0", "var_1"]
        assert expression.return_type == Bool
        assert expression.clause[0].expression == ["var_0"]
        assert expression.clause[0].type == Integer
        assert expression.clause[1].expression == ["var_1"]
        assert expression.clause[1].type == Real
        assert stack.get_variable("func_name").type == Function(([Integer, Real], Bool))

    def test_no_return(self):
        tree = tr("func_decl", "func_name",
                  tr("argument", "a", tr("type_int")),
                  tr("clause", tr("variable", "a")))
        stack = Stack()
        expression = parser.handle(tree, stack)
        assert isinstance(expression, FunctionDeclarationExpression)
        assert expression.name == "var_0"
        assert expression.symbol_name == "func_name"
        assert expression.arguments == ["var_0"]
        assert expression.return_type == Void
        assert expression.clause[0].expression == ["var_0"]
        assert expression.clause[0].type == Integer
        assert stack.get_variable("func_name").type == Function(([Integer], Void))

    def test_no_arguments(self):
        tree = tr("func_decl", "func_name",
                  tr("type_bool"),
                  tr("clause"))
        stack = Stack()
        expression = parser.handle(tree, stack)
        assert isinstance(expression, FunctionDeclarationExpression)
        assert expression.name == "var_0"
        assert expression.symbol_name == "func_name"
        assert expression.arguments == []
        assert expression.return_type == Bool
        assert stack.get_variable("func_name").type == Function(([], Bool))

    def test_no_arguments_no_return(self):
        tree = tr("func_decl", "func_name", tr("clause"))
        stack = Stack()
        expression = parser.handle(tree, stack)
        assert isinstance(expression, FunctionDeclarationExpression)
        assert expression.name == "var_0"
        assert expression.symbol_name == "func_name"
        assert expression.arguments == []
        assert expression.return_type == Void
        assert stack.get_variable("func_name").type == Function(([], Void))


class TestReturnStatement:
    def test_return(self):
        tree = tr("return_statement", tr("int_literal", "1"))
        stack = Stack()
        stack.context_return_type = Real
        expression = parser.handle(tree, stack)
        assert expression.type == Void
        assert expression.expression == ["return ", "1"]

    def test_return_wrong_type(self):
        tree = tr("return_statement", tr("int_literal", "1"))
        stack = Stack()
        stack.context_return_type = Bool
        with pytest.raises(ValueTypeError):
            parser.handle(tree, stack)

    def test_return_wrong_context(self):
        tree = tr("return_statement", tr("int_literal", "1"))
        stack = Stack()
        with pytest.raises(CompileTimeError):
            parser.handle(tree, stack)

    def test_return_void(self):
        tree = tr("return_statement")
        stack = Stack()
        stack.context_return_type = Void
        expression = parser.handle(tree, stack)
        assert expression.expression == ["return"]


class TestUnaryOperations:
    @pytest.mark.parametrize("type", [Integer, Real])
    def test_negation_correct_type(self, type):
        tree = tr("negation", tr("variable", "a"))
        stack = Stack()
        stack.add_global("a", type)
        expression = parser.handle(tree, stack)
        assert expression.expression == ["-(", "a", ")"]
        assert expression.type == type

    def test_negation_illegal_type(self):
        tree = tr("negation", tr("variable", "a"))
        stack = Stack()
        stack.add_global("a", Bool)
        with pytest.raises(ValueTypeError):
            parser.handle(tree, stack)


def test_noop():
    tree = tr("noop_expression")
    expression = parser.handle(tree, Stack())
    assert expression.type == Void
    assert expression.expression == ["pass"]
