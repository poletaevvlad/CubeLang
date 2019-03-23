from libcube.compiler.expression import VariablesPool, Expression
from libcube.compiler.types import Integer, Real
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
