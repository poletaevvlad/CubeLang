from typing import List, Optional, Union

from compiler.codeio import CodeStream
from .types import Type

TemplateType = List[Union[str, int]]


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
    def __init__(self, expr_type: Type, text: Union[str, TemplateType] = None):
        self.intermediates: List[Expression] = list()
        self.type: Type = expr_type
        if text is not None and isinstance(text, str):
            text = [text]
        self.expression: TemplateType = text

    def add_intermediate(self, expression: "Expression") -> int:
        self.intermediates.append(expression)
        return len(self.intermediates) - 1

    def generate(self, temp_pool: VariablesPool, stream: CodeStream, var_name: Optional[str]):
        with temp_pool.allocate(len(self.intermediates)) as variables:
            for var, expr in zip(variables, self.intermediates):
                temp_var_name = "tmp_" + str(var)
                expr.generate(temp_pool, stream, temp_var_name)
            variables = list(variables)
            expression = "".join("tmp_" + str(variables[c]) if isinstance(c, int) else c
                                 for c in self.expression)

        if var_name is not None:
            stream.push_line(f"{var_name} = {expression}")
        else:
            stream.push_line(expression)

    @staticmethod
    def _from_template(template: TemplateType, expressions: List[TemplateType]) -> TemplateType:
        for component in template:
            if isinstance(component, int):
                yield from expressions[component]
            else:
                yield component

    @staticmethod
    def merge(expr_type: Type, template: TemplateType, *parts: "Expression") -> "Expression":
        result = Expression(expr_type)

        expressions = [parts[0].expression]
        for inter in parts[0].intermediates:
            result.add_intermediate(inter)
        offset = len(parts[0].intermediates)

        for expr in parts[1:]:
            this_expression = expr.expression[::]
            for i, component in enumerate(this_expression):
                if isinstance(component, int):
                    this_expression[i] += offset
            expressions.append(this_expression)
            for inter in expr.intermediates:
                result.add_intermediate(inter)
            offset += len(expr.intermediates)

        result.expression = list(Expression._from_template(template, expressions))
        return result

