from libcube.compiler.expression import VariablesPool


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
