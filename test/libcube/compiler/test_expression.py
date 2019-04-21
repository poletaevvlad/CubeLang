from libcube.compiler.expression import VariablesPool, Expression, ConditionExpression, WhileLoopExpression, \
    RepeatLoopExpression, DoWhileLoopExpression, ForLoopExpression, CubeTurningExpression
from libcube.compiler.types import Integer, Real, Bool, Void, Set
from libcube.compiler.codeio import CodeStream


def test_allocation():
    pool = VariablesPool()

    indices = list(pool.allocate(5))
    assert indices == [0, 1, 2, 3, 4]

    indices = list(pool.allocate(3))
    assert indices == [5, 6, 7]

    pool.deallocate(8)
    indices = list(pool.allocate(4))
    assert indices == [0, 1, 2, 3]


def test_context_manager():
    pool = VariablesPool()
    with pool.allocate(3) as indices:
        assert list(indices) == [0, 1, 2]
        with pool.allocate(2) as indices2:
            assert list(indices2) == [3, 4]
    with pool.allocate(4) as indices:
        assert list(indices) == [0, 1, 2, 3]


def test_generating():
    expression = Expression(Integer)
    t1 = expression.add_intermediate(Expression(Integer, ["2 + 3"]))
    t2 = expression.add_intermediate(Expression(Integer, ["4 + 6"]))
    expression.expression = [t1, " * ", t2]

    stream = CodeStream()
    pool = VariablesPool()
    pool.allocate(2)
    expression.generate(pool, stream, None)

    assert stream.get_contents() == "tmp_2 = 2 + 3\ntmp_3 = 4 + 6\ntmp_2 * tmp_3\n"


def test_merge():
    intermediates = [Expression(Integer) for _ in range(7)]

    ex1 = Expression(Integer, [0, "/", 1])
    ex1.add_intermediate(intermediates[0])
    ex1.add_intermediate(intermediates[1])

    ex2 = Expression(Integer, [0, "*", 1, "*", 2])
    ex2.add_intermediate(intermediates[2])
    ex2.add_intermediate(intermediates[3])
    ex2.add_intermediate(intermediates[4])

    ex3 = Expression(Integer, [1, "+", 0])
    ex3.add_intermediate(intermediates[5])
    ex3.add_intermediate(intermediates[6])

    merged = Expression.merge(Real, ["(", 1, ")--(", 2, ")--(", 0, ")"], ex1, ex2, ex3)
    assert merged.intermediates == intermediates
    assert merged.type == Real
    assert merged.expression == ["(", 2, "*", 3, "*", 4, ")--(", 6, "+", 5, ")--(", 0, "/", 1, ")"]


class TestConditions:
    def test_simple(self):
        expr = ConditionExpression(Expression(Bool, ["a"]),
                                   [Expression(Integer, "b"), Expression(Integer, "c")],
                                   [])
        pool = VariablesPool()
        stream = CodeStream()
        expr.generate(pool, stream, None)

        res = stream.get_contents()
        assert res == "if a:\n    b\n    c\n"
        assert expr.type == Void

    def test_else(self):
        expr = ConditionExpression(Expression(Bool, ["a"]),
                                   [Expression(Integer, "b")],
                                   [Expression(Real, "c"), Expression(Bool, "d")])
        pool = VariablesPool()
        stream = CodeStream()
        expr.generate(pool, stream, None)
        res = stream.get_contents()
        assert res == "if a:\n    b\nelse:\n    c\n    d\n"
        assert expr.type == Void

    def test_expression(self):
        expr = ConditionExpression(Expression(Bool, ["a"]),
                                   [Expression(Integer, "b")],
                                   [Expression(Real, "c"), Expression(Integer, "d")])
        pool = VariablesPool()
        stream = CodeStream()
        expr.generate(pool, stream, "res")

        res = stream.get_contents()
        assert res == "if a:\n    res = b\nelse:\n    c\n    res = d\n"
        assert expr.type == Integer

    def test_merge(self):
        expr1 = Expression(Integer, ["a"])
        expr2 = ConditionExpression(Expression(Bool, ["a"]), [Expression(Integer, "b")], [Expression(Integer, "d")])
        merged = Expression.merge(Bool, [0, " -- ", 1], expr1, expr2)

        pool = VariablesPool()
        stream = CodeStream()
        merged.generate(pool, stream, "x")

        res = stream.get_contents()
        assert res == "if a:\n    tmp_0 = b\nelse:\n    tmp_0 = d\nx = a -- tmp_0\n"


class TestWhileLoop:
    def test_loop(self):
        condition = Expression(Bool, ["a ", 0])
        condition.add_intermediate(Expression(Integer, "b"))

        action = Expression(Void, ["action ", 0])
        action.add_intermediate(Expression(Integer, "A"))

        expr = WhileLoopExpression(condition, [Expression(Integer, "b"), action])
        stream = CodeStream()
        expr.generate(VariablesPool(), stream, None)

        res = stream.get_contents()
        assert res == "tmp_0 = b\nwhile a tmp_0:\n    b\n    tmp_1 = A\n    action tmp_1\n    tmp_0 = b\n"

    def test_loop_variable(self):
        condition = Expression(Bool, ["a ", 0])
        condition.add_intermediate(Expression(Integer, "b"))

        expr = WhileLoopExpression(condition, [Expression(Integer, "b"), Expression(Integer, "c")])
        stream = CodeStream()
        expr.generate(VariablesPool(), stream, None)

        res = stream.get_contents()
        assert res == "tmp_0 = b\nwhile a tmp_0:\n    b\n    c\n    tmp_0 = b\n"


class TestRepeatLoop:
    def test_loop(self):
        iterations = Expression(Bool, ["a ", 0])
        iterations.add_intermediate(Expression(Void, ["b"]))
        expr = RepeatLoopExpression(iterations, [Expression(Void, "a"), Expression(Void, "b")])
        stream = CodeStream()
        expr.generate(VariablesPool(), stream, None)

        res = stream.get_contents()
        assert res == "tmp_1 = b\nfor tmp_0 in range(a tmp_1):\n    a\n    b\n"


class TestDoWhileLoop:
    def test_loop(self):
        conditon = Expression(Bool, ["a ", 0])
        conditon.add_intermediate(Expression(Void, ["b"]))
        expr = DoWhileLoopExpression(conditon, [Expression(Void, "a"), Expression(Void, "b")])
        stream = CodeStream()
        expr.generate(VariablesPool(), stream, None)

        res = stream.get_contents()
        assert res == "while True:\n    a\n    b\n    tmp_0 = b\n    if not (a tmp_0):\n        break\n"


class TestForLoop:
    def test_loop(self):
        range_expression = Expression(Set(Integer), ["range(", 0, ")"])
        range_expression.add_intermediate(Expression(Bool, ["x"]))
        expr = ForLoopExpression("i", range_expression, [Expression(Void, "x"), Expression(Integer, "y")])

        stream = CodeStream()
        expr.generate(VariablesPool(), stream, None)
        res = stream.get_contents()
        assert res == "tmp_0 = x\nfor i in range(tmp_0):\n    x\n    y\n"


def test_cube_rotation():
    expression = CubeTurningExpression("left", 1)
    stream = CodeStream()
    expression.generate(VariablesPool(), stream, None)
    assert stream.get_contents() == "cube_turn(left, 1)\n"

    expression.amount = 2
    stream = CodeStream()
    expression.generate(VariablesPool(), stream, None)
    assert stream.get_contents() == "cube_turn(left, 2)\n"