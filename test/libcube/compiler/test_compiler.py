import lark
import pytest

from libcube.compiler.compiler import CompilerTransformer
from libcube.compiler.expression import Expression
from libcube.compiler.types import Integer, Real, Type, Bool


# noinspection PyMethodMayBeStatic
class TestTransformer:
    @pytest.fixture()
    def transform(self) -> CompilerTransformer:
        return CompilerTransformer()

    @pytest.mark.parametrize("name, value, exp_type, exp_value", [
        ("int_literal", "1", Integer, "1"),
        ("float_literal", "1.4", Real, "1.4")
    ])
    def test_literal(self, name: str, value: str, exp_type: Type, exp_value: str, transform: CompilerTransformer):
        tree = lark.Tree(name, [value])
        expr = transform.transform(tree)
        assert isinstance(expr, Expression)
        assert expr.type == exp_type
        assert expr.expression == exp_value
        assert expr.intermediates == []

    @pytest.mark.parametrize("op1_type, op2_type, op_name, res_type, res_expr", [
        (Integer, Integer, "op_0_0", Integer, "(a) + (b)"),
        (Real, Integer, "op_0_0", Real, "(a) + (b)"),
        (Integer, Real, "op_0_0", Real, "(a) + (b)"),
        (Integer, Integer, "op_0_3", Real, "(a) / (b)")
    ])
    def test_operators(self, op1_type: Type, op2_type: Type, op_name: str, res_type: Type,
                       res_expr: str, transform: CompilerTransformer):
        a_expr = Expression(op1_type, "a")
        b_expr = Expression(op2_type, "b")
        tree = lark.Tree(op_name, [a_expr, b_expr])

        expr: Expression = transform.transform(tree)
        assert expr.type == res_type
        assert expr.intermediates == []
        assert expr.expression == res_expr

    @pytest.mark.parametrize("op1_type, op2_type, op_name", [
        (Bool, Integer, "op_0_0"),
    ])
    def test_operators_invalid(self, op1_type: Type, op2_type: Type, op_name: str, transform: CompilerTransformer):
        a_expr = Expression(op1_type, "a")
        b_expr = Expression(op2_type, "b")
        tree = lark.Tree(op_name, [a_expr, b_expr])
        with pytest.raises(Exception):
            transform.transform(tree)
