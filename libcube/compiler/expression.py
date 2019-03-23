from typing import List, Optional, Match
import re

from compiler.codeio import CodeStream
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
    def __init__(self, expr_type: Type, text: str = ""):
        self.intermediates: List[Expression] = list()
        self.type: Type = expr_type
        self.expression: str = text

    def add_intermediate(self, expression: "Expression") -> int:
        self.intermediates.append(expression)
        return len(self.intermediates) - 1

    def generate(self, temp_pool: VariablesPool, stream: CodeStream, var_name: Optional[str]):
        with temp_pool.allocate(len(self.intermediates)) as variables:
            for var, expr in zip(variables, self.intermediates):
                temp_var_name = "tmp_" + str(var)
                expr.generate(temp_pool, stream, temp_var_name)
            variables = list(variables)

            def substitute(m: Match[str]) -> str:
                nonlocal variables
                index = int(m.group(1))
                return "tmp_" + str(variables[index])

            expression = re.sub("{(\d+)}", substitute, self.expression)

        if var_name is not None:
            stream.push_line(f"{var_name} = {expression}")
        else:
            stream.push_line(expression)

