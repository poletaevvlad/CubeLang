from typing import List, Optional, Union, Tuple

from compiler.codeio import CodeStream
from .types import Type, Void

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

    def allocate_single(self):
        self._allocated += 1
        return self._allocated - 1

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

    def generate_intermediates(self, vars: VariablesPool.Context, pool: VariablesPool, stream: CodeStream):
        for var, expr in zip(vars, self.intermediates):
            temp_var_name = "tmp_" + str(var)
            expr.generate(pool, stream, temp_var_name)

    def generate_expression_line(self, vars: VariablesPool.Context) -> str:
        variables = list(vars)
        return "".join("tmp_" + str(variables[c]) if isinstance(c, int) else c
                       for c in self.expression)

    def generate_line(self, pool: VariablesPool, stream: CodeStream) -> str:
        with pool.allocate(len(self.intermediates)) as variables:
            self.generate_intermediates(variables, pool, stream)
            return self.generate_expression_line(variables)

    def generate(self, temp_pool: VariablesPool, stream: CodeStream, var_name: Optional[str] = None):
        if self.expression == [0]:
            self.intermediates[0].generate(temp_pool, stream, var_name)
            return
        expression = self.generate_line(temp_pool, stream)
        if var_name is not None:
            expression = var_name + " = " + expression
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


class ConditionExpression(Expression):
    class Intermediate(Expression):
        def __init__(self, returns_value: bool, actions: List[Tuple[Expression, List[Expression]]],
                     else_clause: List[Expression]):
            super(ConditionExpression.Intermediate, self).__init__(Void, [])
            self.returns_value = returns_value
            self.actions: List[Tuple[Expression, List[Expression]]] = actions
            self.else_clause: List[Expression] = else_clause

        @staticmethod
        def _generate_clause(clause: List[Expression], temp_pool: VariablesPool,
                             stream: CodeStream, var_name: Optional[str]):
            for line in clause[:-1]:
                line.generate(temp_pool, stream, None)
            clause[-1].generate(temp_pool, stream, var_name)

        def _generate_if(self, actions: List[Tuple[Expression, List[Expression]]], temp_pool: VariablesPool,
                         stream: CodeStream, var_name: Optional[str]):
            condition = actions[0][0].generate_line(temp_pool, stream)
            stream.push_line(f"if {condition}:")
            stream.indent()
            self._generate_clause(actions[0][1], temp_pool, stream, var_name)
            stream.unindent()
            if len(actions) > 1 or len(self.else_clause) > 0:
                stream.push_line("else:")
                stream.indent()
                if len(actions) > 1:
                    self._generate_if(actions[1:], temp_pool, stream, var_name)
                else:
                    self._generate_clause(self.else_clause, temp_pool, stream, var_name)
                stream.unindent()

        def generate(self, temp_pool: VariablesPool, stream: CodeStream, var_name: Optional[str] = None):
            if not self.returns_value:
                var_name = None
            self._generate_if(self.actions, temp_pool, stream, var_name)

    def __init__(self, actions: List[Tuple[Expression, List[Expression]]], else_clause: List[Expression]):
        if len(else_clause) > 0:
            res_type = else_clause[-1].type
            for action in actions:
                action_type = action[1][-1].type
                if action_type.is_assignable(res_type):
                    res_type = action_type
                elif not res_type.is_assignable(action_type):
                    res_type = Void
                    break
        else:
            res_type = Void

        super(ConditionExpression, self).__init__(res_type, [0])
        self.add_intermediate(ConditionExpression.Intermediate(res_type, actions, else_clause))


class WhileLoopExpression(Expression):
    class Intermediate(Expression):
        def __init__(self, condition: Expression, actions: List[Expression]):
            self.condition: Expression = condition
            self.actions: List[Expression] = actions
            super().__init__(Void, [])

        def generate(self, temp_pool: VariablesPool, stream: CodeStream, var_name: Optional[str] = None):
            with temp_pool.allocate(len(self.condition.intermediates)) as cond_vars:
                self.condition.generate_intermediates(cond_vars, temp_pool, stream)
                stream.push_line("while " + self.condition.generate_expression_line(cond_vars) + ":")
                stream.indent()
                for action in self.actions:
                    action.generate(temp_pool, stream, None)
                self.condition.generate_intermediates(cond_vars, temp_pool, stream)
                stream.unindent()

    def __init__(self, condition: Expression, actions: List[Expression]):
        super().__init__(Void, [0])
        self.add_intermediate(WhileLoopExpression.Intermediate(condition, actions))


class RepeatLoopExpression(Expression):
    class Intermediate(Expression):
        def __init__(self, times: Expression, actions: List[Expression]):
            self.times: Expression = times
            self.actions: List[Expression] = actions
            super().__init__(Void, [])

        def generate(self, temp_pool: VariablesPool, stream: CodeStream, var_name: Optional[str] = None):
            with temp_pool.allocate(1) as ctr:
                counter, = ctr
                line = self.times.generate_line(temp_pool, stream)
                stream.push_line(f"for tmp_{counter} in range({line}):")
                stream.indent()
                for action in self.actions:
                    action.generate(temp_pool, stream, None)
                stream.unindent()

    def __init__(self, times: Expression, actions: List[Expression]):
        super().__init__(Void, [0])
        self.add_intermediate(RepeatLoopExpression.Intermediate(times, actions))


class DoWhileLoopExpression(Expression):
    class Intermediate(Expression):
        def __init__(self, condition: Expression, actions: List[Expression]):
            self.condition: Expression = condition
            self.actions: List[Expression] = actions
            super(DoWhileLoopExpression.Intermediate, self).__init__(Void, [])

        def generate(self, temp_pool: VariablesPool, stream: CodeStream, var_name: Optional[str] = None):
            stream.push_line("while True:")
            stream.indent()
            for action in self.actions:
                action.generate(temp_pool, stream, None)

            condition = self.condition.generate_line(temp_pool, stream)
            stream.push(f"if not ({condition}):")
            stream.indent()
            stream.push("break")
            stream.unindent(2)

    def __init__(self, condition: Expression, actions: List[Expression]):
        super().__init__(Void, [0])
        self.add_intermediate(DoWhileLoopExpression.Intermediate(condition, actions))


class ForLoopExpression(Expression):
    class Intermediate(Expression):
        def __init__(self, iterator: str, loop_range: Expression, actions: List[Expression]):
            self.iterator: str = iterator
            self.range: Expression = loop_range
            self.actions: List[Expression] = actions
            super().__init__(Void, [])

        def generate(self, temp_pool: VariablesPool, stream: CodeStream, var_name: Optional[str] = None):
            range_expression = self.range.generate_line(temp_pool, stream)
            stream.push(f"for {self.iterator} in {range_expression}:")
            stream.indent()
            for action in self.actions:
                action.generate(temp_pool, stream, None)
            stream.unindent()

    def __init__(self, iterator: str, loop_range: Expression, actions: List[Expression]):
        super().__init__(Void, [0])
        self.add_intermediate(ForLoopExpression.Intermediate(iterator, loop_range, actions))


class CubeTurningExpression(Expression):
    def __init__(self, side: str, amount: int):
        super(CubeTurningExpression, self).__init__(Void, [])
        self.side: str = side
        self.amount: int = amount

    def generate(self, temp_pool: VariablesPool, stream: CodeStream, var_name: Optional[str] = None):
        stream.push_line(f"cube_turn({self.side}, {self.amount})")
