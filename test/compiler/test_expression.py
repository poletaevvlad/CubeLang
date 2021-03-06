from cubelang.compiler.expression import VariablesPool, Expression, ConditionExpression, WhileLoopExpression, \
    RepeatLoopExpression, DoWhileLoopExpression, ForLoopExpression, CubeTurningExpression, CubeRotationExpression, \
    FunctionDeclarationExpression
from cubelang.compiler.types import Integer, Real, Bool, Void, Set, List
from cubelang.compiler.codeio import CodeStream
from cubelang.compiler.code_map import CodeMap


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
    expression = Expression(0, Integer)
    t1 = expression.add_intermediate(Expression(0, Integer, ["2 + 3"]))
    t2 = expression.add_intermediate(Expression(0, Integer, ["4 + 6"]))
    expression.expression = [t1, " * ", t2]

    stream = CodeStream()
    pool = VariablesPool()
    pool.allocate(2)
    expression.generate(pool, stream, CodeMap(), None)

    assert stream.get_contents() == "tmp_2 = 2 + 3\ntmp_3 = 4 + 6\ntmp_2 * tmp_3\n"


def test_merge():
    intermediates = [Expression(0, Integer) for _ in range(7)]

    ex1 = Expression(0, Integer, [0, "/", 1])
    ex1.add_intermediate(intermediates[0])
    ex1.add_intermediate(intermediates[1])

    ex2 = Expression(0, Integer, [0, "*", 1, "*", 2])
    ex2.add_intermediate(intermediates[2])
    ex2.add_intermediate(intermediates[3])
    ex2.add_intermediate(intermediates[4])

    ex3 = Expression(0, Integer, [1, "+", 0])
    ex3.add_intermediate(intermediates[5])
    ex3.add_intermediate(intermediates[6])

    merged = Expression.merge(Real, ["(", 1, ")--(", 2, ")--(", 0, ")"], ex1, ex2, ex3)
    assert merged.intermediates == intermediates
    assert merged.type == Real
    assert merged.expression == ["(", 2, "*", 3, "*", 4, ")--(", 6, "+", 5, ")--(", 0, "/", 1, ")"]


class TestConditions:
    def test_simple(self):
        expr = ConditionExpression(0, [(Expression(0, Bool, ["a"]), [Expression(0, Integer, "b"),
                                                                     Expression(0, Integer, "c")])], [])
        pool = VariablesPool()
        stream = CodeStream()
        expr.generate(pool, stream, CodeMap(), None)

        res = stream.get_contents()
        assert res == "if a:\n    b\n    c\n"
        assert expr.type == Void

    def test_else(self):
        expr = ConditionExpression(0, [(Expression(0, Bool, ["a"]), [Expression(0, Integer, "b")])],
                                      [Expression(0, Real, "c"), Expression(0, Bool, "d")])
        pool = VariablesPool()
        stream = CodeStream()
        expr.generate(pool, stream, CodeMap(), None)
        res = stream.get_contents()
        assert res == "if a:\n    b\nelse:\n    c\n    d\n"
        assert expr.type == Void

    def test_elseif(self):
        expr = ConditionExpression(0, [(Expression(0, Bool, ["a"]), [Expression(0, Integer, "b")]),
                                       (Expression(0, Bool, ["c"]), [Expression(0, Integer, "d")])],
                                   [Expression(0, Real, "e")])
        pool = VariablesPool()
        stream = CodeStream()
        expr.generate(pool, stream, CodeMap(), None)
        res = stream.get_contents()
        assert res == "if a:\n    b\nelse:\n    if c:\n        d\n    else:\n        e\n"

    def test_expression(self):
        expr = ConditionExpression(0, [(Expression(0, Bool, ["a"]), [Expression(0, Integer, "b")])],
                                      [Expression(0, Real, "c"), Expression(0, Integer, "d")])
        pool = VariablesPool()
        stream = CodeStream()
        expr.generate(pool, stream, CodeMap(), "res")

        res = stream.get_contents()
        assert res == "if a:\n    res = b\nelse:\n    c\n    res = d\n"
        assert expr.type == Integer

    def test_merge(self):
        expr1 = Expression(0, Integer, ["a"])
        expr2 = ConditionExpression(0, [(Expression(0, Bool, ["a"]), [Expression(0, Integer, "b")])],
                                    [Expression(0, Integer, "d")])
        merged = Expression.merge(Bool, [0, " -- ", 1], expr1, expr2)

        pool = VariablesPool()
        stream = CodeStream()
        merged.generate(pool, stream, CodeMap(), "x")

        res = stream.get_contents()
        assert res == "if a:\n    tmp_0 = b\nelse:\n    tmp_0 = d\nx = a -- tmp_0\n"


class TestWhileLoop:
    def test_loop(self):
        condition = Expression(0, Bool, ["a ", 0])
        condition.add_intermediate(Expression(0, Integer, "b"))

        action = Expression(0, Void, ["action ", 0])
        action.add_intermediate(Expression(0, Integer, "A"))

        expr = WhileLoopExpression(0, condition, [Expression(0, Integer, "b"), action])
        stream = CodeStream()
        expr.generate(VariablesPool(), stream, CodeMap(), None)

        res = stream.get_contents()
        assert res == "tmp_0 = b\nwhile a tmp_0:\n    b\n    tmp_1 = A\n    action tmp_1\n    tmp_0 = b\n"

    def test_loop_variable(self):
        condition = Expression(0, Bool, ["a ", 0])
        condition.add_intermediate(Expression(0, Integer, "b"))

        expr = WhileLoopExpression(0, condition, [Expression(0, Integer, "b"), Expression(0, Integer, "c")])
        stream = CodeStream()
        expr.generate(VariablesPool(), stream, CodeMap(), None)

        res = stream.get_contents()
        assert res == "tmp_0 = b\nwhile a tmp_0:\n    b\n    c\n    tmp_0 = b\n"


class TestRepeatLoop:
    def test_loop(self):
        iterations = Expression(0, Bool, ["a ", 0])
        iterations.add_intermediate(Expression(0, Void, ["b"]))
        expr = RepeatLoopExpression(0, iterations, [Expression(0, Void, "a"), Expression(0, Void, "b")])
        stream = CodeStream()
        expr.generate(VariablesPool(), stream, CodeMap(), None)

        res = stream.get_contents()
        assert res == "tmp_1 = b\nfor tmp_0 in range(a tmp_1):\n    a\n    b\n"


class TestDoWhileLoop:
    def test_loop(self):
        conditon = Expression(0, Bool, ["a ", 0])
        conditon.add_intermediate(Expression(0, Void, ["b"]))
        expr = DoWhileLoopExpression(0, conditon, [Expression(0, Void, "a"), Expression(0, Void, "b")])
        stream = CodeStream()
        expr.generate(VariablesPool(), stream, CodeMap(), None)

        res = stream.get_contents()
        assert res == "while True:\n    a\n    b\n    tmp_0 = b\n    if not (a tmp_0):\n        break\n"


class TestForLoop:
    def test_loop(self):
        range_expression = Expression(0, Set(Integer), ["range(", 0, ")"])
        range_expression.add_intermediate(Expression(0, Bool, ["x"]))
        expr = ForLoopExpression(0, "i", range_expression, [Expression(0, Void, "x"), Expression(0, Integer, "y")])

        stream = CodeStream()
        expr.generate(VariablesPool(), stream, CodeMap(), None)
        res = stream.get_contents()
        assert res == "tmp_0 = x\nfor i in range(tmp_0):\n    x\n    y\n"


class TestTurning:
    def test_single(self):
        expression = CubeTurningExpression(0, "left", 1)
        stream = CodeStream()
        expression.generate(VariablesPool(), stream, CodeMap(), None)
        assert stream.get_contents() == "cube_turn(left, 1, [1])\n"

    def test_double(self):
        expression = CubeTurningExpression(0, "left", 2)
        stream = CodeStream()
        expression.generate(VariablesPool(), stream, CodeMap(), None)
        assert stream.get_contents() == "cube_turn(left, 2, [1])\n"

    def test_indices(self):
        expression = CubeTurningExpression(0, "left", 2)
        expression.indices = [Expression(0, Integer, x) for x in "abc"]
        stream = CodeStream()
        expression.generate(VariablesPool(), stream, CodeMap(), None)
        assert stream.get_contents() == "cube_turn(left, 2, [a, b, c])\n"


def test_cube_rotation():
    expression = CubeRotationExpression(0, "front", False)
    stream = CodeStream()
    expression.generate(VariablesPool(), stream, CodeMap(), None)
    assert stream.get_contents() == "cube_rotate(front, False)\n"


class TestFunctionDeclaration:
    def test_declaration(self):
        expression = FunctionDeclarationExpression(0, "func_name", "func", Integer, ["x", "y", "z"],
                                                   [Expression(0, Void, "a"), Expression(0, Void, "b")])
        stream = CodeStream()
        expression.generate(VariablesPool(), stream, CodeMap(), None)
        assert stream.get_contents() == "@runtime_function(\"func\")\n" \
                                        "def func_name(x, y, z):\n" \
                                        "    a\n    b\n" \
                                        "    return 0\n"

    def test_no_arguments(self):
        expression = FunctionDeclarationExpression(0, "func2", "func2", List(Integer), [],
                                                   [Expression(0, Void, "a")])
        stream = CodeStream()
        expression.generate(VariablesPool(), stream, CodeMap(), None)
        assert stream.get_contents() == "@runtime_function(\"func2\")\n" \
                                        "def func2():\n    a\n    return list()\n"

    def test_no_return(self):
        expression = FunctionDeclarationExpression(0, "func3", "func3", Void, [],
                                                   [Expression(0, Void, "a")])
        stream = CodeStream()
        expression.generate(VariablesPool(), stream, CodeMap(), None)
        assert stream.get_contents() == "@runtime_function(\"func3\")\ndef func3():\n    a\n"

    def test_no_body(self):
        expression = FunctionDeclarationExpression(0, "func2", "func2", List(Integer), [], [])
        stream = CodeStream()
        expression.generate(VariablesPool(), stream, CodeMap(), None)
        assert stream.get_contents() == "@runtime_function(\"func2\")\n" \
                                        "def func2():\n    return list()\n"

    def test_no_body_no_return(self):
        expression = FunctionDeclarationExpression(0, "func2", "func2", Void, [], [])
        stream = CodeStream()
        expression.generate(VariablesPool(), stream, CodeMap(), None)
        assert stream.get_contents() == "@runtime_function(\"func2\")\ndef func2():\n    pass\n"
