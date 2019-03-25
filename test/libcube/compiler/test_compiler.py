import lark
import pytest

from libcube.compiler.compiler import compiler
from libcube.compiler.expression import Expression
from libcube.compiler.stack import Stack
from libcube.compiler.types import Integer, Real, Type, Bool, List, Set


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

    # TODO: test invalid operand types

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
