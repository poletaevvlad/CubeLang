from typing import List

from .types import Type


class VariablesPool:
    class Context:
        def __init__(self, pool: "VariablesPool", allocated: int):
            self.pool = pool
            self._allocated: int = allocated

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.pool.deallocate(self._allocated)
            return False

        def __iter__(self):
            return range(self.pool._allocated - self._allocated, self.pool._allocated).__iter__()

    def __init__(self):
        self._allocated = 0

    def allocate(self, count: int) -> Context:
        self._allocated += count
        return VariablesPool.Context(self, count)

    def deallocate(self, count: int):
        self._allocated -= count


class Expression:
    def __init__(self, expr_type: Type):
        self.intermediates: List[Expression] = list()
        self.type: Type = expr_type
        self.expression: str = ""

    def add_intermediate(self, expression: "Expression") -> int:
        self.intermediates.append(expression)
        return len(self.intermediates) - 1
