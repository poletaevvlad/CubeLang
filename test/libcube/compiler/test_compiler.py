import lark
import pytest

from libcube.compiler.compiler import compiler
from libcube.compiler.expression import Expression, ConditionExpression, WhileLoopExpression, DoWhileLoopExpression, \
    RepeatLoopExpression, ForLoopExpression
from libcube.compiler.stack import Stack
from libcube.compiler.types import Integer, Real, Type, Bool, List, Set, Void, Function
import typing


# noinspection PyMethodMayBeStatic
class TestTransformer:

    @pytest.mark.parametrize("name, value, exp_type, exp_value", [
        ("int_literal", "1", Integer, "1"),
        ("float_literal", "1.4", Real, "1.4")
    ])
    def test_literal(self, name: str, value: str, exp_type: Type, exp_value: str):
        tree = lark.Tree(name, [value])
        expr = compiler.handle(tree, Stack())
        assert isinstance(expr, Expression)
        assert expr.type == exp_type
        assert expr.expression == [exp_value]
        assert expr.intermediates == []

    @pytest.mark.parametrize("op1_type, op2_type, op_name, res_type, res_expr", [
        ("int_literal", "int_literal", "op_0_0", Integer, "(1) + (2)"),
        ("float_literal", "int_literal", "op_0_0", Real, "(1.0) + (2)"),
        ("int_literal", "float_literal", "op_0_0", Real, "(1) + (2.0)"),
        ("int_literal", "int_literal", "op_0_3", Real, "(1) / (2)")
    ])
    def test_operators(self, op1_type: str, op2_type: str, op_name: str, res_type: Type, res_expr: str):
        tree = lark.Tree(op_name, [lark.Tree(op1_type, ["1"]), lark.Tree(op2_type, ["2"])])

        expr: Expression = compiler.handle(tree, Stack())
        assert expr.type == res_type
        assert expr.intermediates == []
        assert "".join(expr.expression) == res_expr

    @pytest.mark.parametrize("operator, arg1, arg2", [
        ("op_0_0", lark.Tree("float_literal", ["1"]), lark.Tree("bool_literal_true", [])),
        ("op_0_0", lark.Tree("bool_literal_true", []), lark.Tree("float_literal", ["2"]))
    ])
    def test_wrong_operand(self, operator, arg1, arg2):
        tree = lark.Tree(operator, [arg1, arg2])
        with pytest.raises(ValueError):
            compiler.handle(tree, Stack())

    def test_variable_exist(self):
        tree = lark.Tree("variable", "a")
        stack = Stack()
        stack.add_variable("a", Integer)
        expression: Expression = compiler.handle(tree, stack)
        assert expression.type == Integer
        assert expression.expression == ["var_0"]

    def test_global_variable_exist(self):
        tree = lark.Tree("variable", "a")
        stack = Stack()
        stack.add_global("a", Real)
        expression: Expression = compiler.handle(tree, stack)
        assert expression.type == Real
        assert expression.expression == ["a"]

    def test_undefined_variable(self):
        tree = lark.Tree("variable", "a")
        with pytest.raises(ValueError):
            compiler.handle(tree, Stack())

    @pytest.mark.parametrize("tree, expected", [
        (lark.Tree("type_int", []), Integer),
        (lark.Tree("type_real", []), Real),
        (lark.Tree("type_bool", []), Bool),
        (lark.Tree("type_list", [lark.Tree("type_bool", [])]), List(Bool)),
        (lark.Tree("type_set", [lark.Tree("type_real", [])]), Set(Real)),
    ])
    def test_type_handle(self, tree: lark.Tree, expected: Type):
        assert compiler.handle(tree, Stack()) == expected

    def test_var_declaration(self):
        tree = lark.Tree("var_decl", ["a", "b", "c", lark.Tree("type_int", [])])
        stack = Stack()

        expressions = compiler.handle(tree, stack)
        for i, value in enumerate(expressions):
            assert value.type == Void
            assert value.expression == ["var_" + str(i), " = ", "0"]

        assert stack.get_variable("a").type == Integer
        assert stack.get_variable("b").type == Integer
        assert stack.get_variable("c").type == Integer

    def test_var_declaration_value(self):
        tree = lark.Tree("var_decl", ["a", "b", "c", lark.Tree("type_int", []), lark.Tree("int_literal", "1")])
        stack = Stack()

        values: typing.List[Expression] = compiler.handle(tree, stack)
        for i, value in enumerate(values):
            assert value.type == Void
            assert value.expression == ["var_" + str(i), " = ", "1"]

        assert stack.get_variable("a").type == Integer
        assert stack.get_variable("b").type == Integer
        assert stack.get_variable("c").type == Integer

    def test_var_declaration_wrong_type(self):
        tree = lark.Tree("var_decl", ["a", lark.Tree("type_int", []), lark.Tree("float_literal", "1")])
        with pytest.raises(ValueError):
            compiler.handle(tree, Stack())

    def test_if_expression(self):
        tree = lark.Tree("if_expression", [
            lark.Tree("bool_literal_true", []),
            lark.Tree("clause", [
                lark.Tree("int_literal", "1"),
                lark.Tree("float_literal", "2")
            ])
        ])
        expression = compiler.handle(tree, Stack())
        assert isinstance(expression, ConditionExpression)
        assert expression.type == Void

        intermediate = expression.intermediates[0]
        assert isinstance(intermediate, ConditionExpression.Intermediate)
        assert intermediate.condition.expression == ["True"]
        assert intermediate.then_clause[0].expression == ["1"]
        assert intermediate.then_clause[1].expression == ["2.0"]
        assert len(intermediate.else_clause) == 0

    def test_if_else_expression(self):
        tree = lark.Tree("if_expression", [
            lark.Tree("bool_literal_false", []),
            lark.Tree("int_literal", "1"),
            lark.Tree("clause", [
                lark.Tree("float_literal", "2")
            ])
        ])
        expression = compiler.handle(tree, Stack())
        assert isinstance(expression, ConditionExpression)
        assert expression.type == Real

        intermediate = expression.intermediates[0]
        assert isinstance(intermediate, ConditionExpression.Intermediate)
        assert intermediate.condition.expression == ["False"]
        assert intermediate.then_clause[0].expression == ["1"]
        assert intermediate.else_clause[0].expression == ["2.0"]

    def test_if_wrong_type(self):
        tree = lark.Tree("if_expression", [
            lark.Tree("int_literal", ["1"]),
            lark.Tree("float_literal", ["2"]),
            lark.Tree("float_literal", ["3"])
        ])
        with pytest.raises(ValueError):
            compiler.handle(tree, Stack())

    def test_while(self):
        tree = lark.Tree("while_expression", [
            lark.Tree("bool_literal_true", []),
            lark.Tree("int_literal", "1")
        ])
        expression = compiler.handle(tree, Stack())
        assert isinstance(expression, WhileLoopExpression)
        assert expression.type == Integer

        intermediate = expression.intermediates[0]
        assert isinstance(intermediate, WhileLoopExpression.Intermediate)
        assert intermediate.condition.expression == ["True"]
        assert intermediate.actions[0].expression == ["1"]

    def test_while_type_error(self):
        with pytest.raises(ValueError):
            compiler.handle(lark.Tree("while_expression", [
                lark.Tree("int_literal", "2"),
                lark.Tree("int_literal", "1")
            ]), Stack())

    def test_do_while(self):
        tree = lark.Tree("do_expression", [
            lark.Tree("int_literal", "2"),
            lark.Tree("bool_literal_true", [])
        ])
        expression = compiler.handle(tree, Stack())
        assert isinstance(expression, DoWhileLoopExpression)
        assert expression.type == Integer

        intermediate = expression.intermediates[0]
        assert isinstance(intermediate, DoWhileLoopExpression.Intermediate)
        assert intermediate.condition.expression == ["True"]
        assert intermediate.actions[0].expression == ["2"]

    def test_do_while_type_error(self):
        with pytest.raises(ValueError):
            compiler.handle(lark.Tree("do_expression", [
                lark.Tree("int_literal", "2"),
                lark.Tree("int_literal", "1")
            ]), Stack())

    def test_repeat(self):
        tree = lark.Tree("repeat_expression", [
            lark.Tree("int_literal", ["2"]),
            lark.Tree("bool_literal_true", [])
        ])
        expression = compiler.handle(tree, Stack())
        assert isinstance(expression, RepeatLoopExpression)
        assert expression.type == Bool

        intermediate = expression.intermediates[0]
        assert isinstance(intermediate, RepeatLoopExpression.Intermediate)
        assert intermediate.times.expression == ["2"]
        assert intermediate.actions[0].expression == ["True"]

    def test_repeat_error(self):
        with pytest.raises(ValueError):
            compiler.handle(lark.Tree("repeat_expression", [
                lark.Tree("float_literal", "2"),
                lark.Tree("int_literal", "1")
            ]), Stack())

    def test_for_loop_existing_var(self):
        stack = Stack()
        stack.add_variable("var", Real)
        stack.add_variable("range", List(Integer))
        tree = lark.Tree("for_expression", [
            "var",
            lark.Tree("variable", ["range"]),
            lark.Tree("int_literal", ["1"])
        ])
        expression = compiler.handle(tree, stack)
        assert isinstance(expression, ForLoopExpression)
        intermediate = expression.intermediates[0]
        assert isinstance(intermediate, ForLoopExpression.Intermediate)
        assert intermediate.iterator == "var_0"
        assert intermediate.range.expression == ["var_1"]
        assert intermediate.actions[0].expression == ["1"]

    def test_for_loop_new_var(self):
        stack = Stack()
        stack.add_variable("range", List(Integer))
        tree = lark.Tree("for_expression", [
            "var",
            lark.Tree("variable", ["range"]),
            lark.Tree("clause", [
                lark.Tree("int_literal", ["1"]),
                lark.Tree("variable", ["var"])
            ])
        ])
        expression = compiler.handle(tree, stack)
        assert isinstance(expression, ForLoopExpression)
        intermediate = expression.intermediates[0]
        assert isinstance(intermediate, ForLoopExpression.Intermediate)
        assert intermediate.iterator == "var_1"
        assert intermediate.range.expression == ["var_0"]
        assert intermediate.actions[0].expression == ["1"]
        assert intermediate.actions[1].expression == ["var_1"]
        assert intermediate.actions[1].type == Integer

    def test_for_loop_wrong_range(self):
        with pytest.raises(ValueError):
            tree = lark.Tree("for_expression", [
                "var",
                lark.Tree("int_literal", ["1"]),
                lark.Tree("int_literal", ["1"])
            ])
            compiler.handle(tree, Stack())

    def test_for_loop_wrong_iterator_type(self):
        with pytest.raises(ValueError):
            stack = Stack()
            stack.add_variable("var", Bool)
            stack.add_variable("range", List(Integer))
            tree = lark.Tree("for_expression", [
                "var",
                lark.Tree("variable", ["range"]),
                lark.Tree("int_literal", ["1"])
            ])
            compiler.handle(tree, stack)

    @pytest.mark.parametrize("is_global", [(True,), (False,)])
    def test_function_call(self, is_global):
        stack = Stack()
        stack.add_variable("array", List(Integer))
        func = Function([Integer, Real, List(Integer)], Void)
        if is_global:
            stack.add_global("func", func)
        else:
            stack.add_variable("func", func)

        tree = lark.Tree("func_call", [
            "func",
            lark.Tree("int_literal", ["1"]),
            lark.Tree("int_literal", ["2"]),
            lark.Tree("variable", ["array"]),
        ])
        expression = compiler.handle(tree, stack)

        assert expression.type == Void
        func_name = "func" if is_global else "var_1"
        assert expression.expression == [func_name, "(", "1", ", ", "2", ", ", "var_0", ")"]

    def test_function_call_invalid_name(self):
        with pytest.raises(ValueError):
            tree = lark.Tree("func_call", ["func"])
            compiler.handle(tree, Stack())

    def test_function_call_invalid_arguments_count_few(self):
        with pytest.raises(ValueError):
            stack = Stack()
            stack.add_variable("func", Function([Integer, Integer], Integer))
            tree = lark.Tree("func_call", ["func", lark.Tree("int_literal", ["1"])])
            compiler.handle(tree, stack)

    def test_function_call_invalid_arguments_count_many(self):
        with pytest.raises(ValueError):
            stack = Stack()
            stack.add_variable("func", Function([Integer, Integer], Integer))
            tree = lark.Tree("func_call", ["func", lark.Tree("int_literal", ["1"]), lark.Tree("int_literal", ["1"]),
                                           lark.Tree("int_literal", ["1"])])
            compiler.handle(tree, stack)

    def test_function_call_invalid_argument_types(self):
        with pytest.raises(ValueError):
            stack = Stack()
            stack.add_variable("var", Set(Real))
            stack.add_variable("func", Function([Integer, List(Integer)], Integer))
            tree = lark.Tree("func_call", ["func", lark.Tree("int_literal", ["1"]), lark.Tree("variable", ["var"])])
            compiler.handle(tree, stack)

    def test_var_assignment(self):
        stack = Stack()
        stack.add_variable("var", Real)
        tree = lark.Tree("var_assignment", ["var", lark.Tree("int_literal", ["42"])])
        expression = compiler.handle(tree, stack)
        assert expression.expression == ["var_0", " = ", "42"]

    def test_var_assignment_readonly(self):
        stack = Stack()
        stack.add_global("var", Real)
        tree = lark.Tree("var_assignment", ["var", lark.Tree("int_literal", ["0"])])
        with pytest.raises(ValueError):
            compiler.handle(tree, stack)

    def test_var_assignment_undefined(self):
        tree = lark.Tree("var_assignment", ["var", lark.Tree("int_literal", ["0"])])
        with pytest.raises(ValueError):
            compiler.handle(tree, Stack())

    def test_var_assignment_type_error(self):
        stack = Stack()
        stack.add_global("var", List(Integer))
        tree = lark.Tree("var_assignment", ["var", lark.Tree("int_literal", ["0"])])
        with pytest.raises(ValueError):
            compiler.handle(tree, stack)
