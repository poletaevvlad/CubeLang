from libcube.compiler.expression import VariablesPool, Expression
from libcube.compiler.types import Integer
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
    t1 = expression.add_intermediate(Expression(Integer, "2 + 3"))
    t2 = expression.add_intermediate(Expression(Integer, "4 + 6"))
    expression.expression = "{{{0}}} * {{{1}}}".format(t1, t2)

    stream = CodeStream()
    pool = VariablesPool()
    pool.allocate(2)
    expression.generate(pool, stream, None)

    assert stream.get_contents() == "tmp_2 = 2 + 3\ntmp_3 = 4 + 6\ntmp_2 * tmp_3\n"

