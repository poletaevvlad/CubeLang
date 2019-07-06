from cubelang.compiler.stack import Stack
from cubelang.compiler.types import Integer, Real, Bool, List


def test_globals():
    stack = Stack()
    stack.add_global("a", List(Integer))
    stack.add_variable("b", Real)

    g = stack.get_variable("a")
    assert g.type == List(Integer)
    assert g.number == -1

    stack.add_variable("a", Bool)
    g = stack.get_variable("a")
    assert g.type == Bool
    assert g.number == 1


def test_frames():
    stack = Stack()
    assert stack.add_variable("a", Integer) == 0
    assert stack.add_variable("b", Real) == 1

    stack.add_frame()
    assert stack.add_variable("b", List(Integer)) == 2
    assert stack.add_variable("c", Bool) == 3
    assert stack.get_variable("b").type == List(Integer)

    stack.pop_frame()
    assert stack.get_variable("b").type == Real
    assert stack.get_variable("c") is None
    assert stack.add_variable("c", List(Integer)) == 2
