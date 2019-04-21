from libcube.compiler.stack import Stack
from libcube.stdlib import Library
from libcube.compiler.types import Integer, Real, Void, Function


def test_library():
    lib = Library()

    @lib.function([Integer, Real], Void)
    def func():
        pass

    assert lib.exec_globals["func"] == func
    assert lib.global_functions["func"].overloads[0].arguments == [Integer, Real]
    assert lib.global_functions["func"].overloads[0].return_type == Void


def test_library_multiple():
    lib = Library()

    @lib.function([Integer], Void)
    @lib.function([Real], Integer)
    def func():
        pass

    assert lib.exec_globals["func"] == func

    overloads = lib.global_functions["func"].overloads
    assert overloads[0].arguments == [Integer]
    assert overloads[0].return_type == Void
    assert overloads[1].arguments == [Real]
    assert overloads[1].return_type == Integer


def test_library_init_stack():
    lib = Library()

    @lib.function([Integer], Integer)
    def func1(): pass

    @lib.function([Real], Real)
    def func2(): pass

    stack = Stack()
    lib.initialize_stack(stack)
    assert stack.get_variable("func1").type == Function(([Integer], Integer))
    assert stack.get_variable("func2").type == Function(([Real], Real))
