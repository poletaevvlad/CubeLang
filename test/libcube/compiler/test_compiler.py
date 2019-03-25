import lark
import pytest

from libcube.compiler.compiler import compiler
from libcube.compiler.expression import Expression
from libcube.compiler.types import Integer, Real, Type, Bool


# noinspection PyMethodMayBeStatic
class TestTransformer:

    @pytest.mark.parametrize("name, value, exp_type, exp_value", [
        ("int_literal", "1", Integer, "1"),
        ("float_literal", "1.4", Real, "1.4")
    ])
    def test_literal(self, name: str, value: str, exp_type: Type, exp_value: str):
        tree = lark.Tree(name, [value])
        expr = compiler.handle(tree)
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

        expr: Expression = compiler.handle(tree)
        assert expr.type == res_type
        assert expr.intermediates == []
        assert "".join(expr.expression) == res_expr

    @pytest.mark.parametrize("op1_type, op2_type, op_name", [
        (Bool, Integer, "op_0_0"),
    ])
    def test_operators_invalid(self, op1_type: Type, op2_type: Type, op_name: str):
        a_expr = Expression(op1_type, ["a"])
        b_expr = Expression(op2_type, ["b"])
        tree = lark.Tree(op_name, [a_expr, b_expr])
        with pytest.raises(Exception):
            compiler.handle(tree)
