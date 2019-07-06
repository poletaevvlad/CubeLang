from typing import List, Optional, Union, Tuple

from .code_map import CodeMap
from .codeio import CodeStream
from .types import Type, Void, Integer

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
    def __init__(self, line_number: int, expr_type: Type, text: Union[str, TemplateType] = None):
        self.line_number: int = line_number
        self.intermediates: List[Expression] = list()
        self.type: Type = expr_type
        if text is not None and isinstance(text, str):
            text = [text]
        self.expression: TemplateType = text

    def add_intermediate(self, expression: "Expression") -> int:
        self.intermediates.append(expression)
        return len(self.intermediates) - 1

    def generate_intermediates(self, vars: VariablesPool.Context, pool: VariablesPool, stream: CodeStream,
                               code_map: CodeMap):
        for var, expr in zip(vars, self.intermediates):
            temp_var_name = "tmp_" + str(var)
            expr.generate(pool, stream, code_map, temp_var_name)

    def generate_expression_line(self, vars: VariablesPool.Context) -> str:
        variables = list(vars)
        return "".join("tmp_" + str(variables[c]) if isinstance(c, int) else c
                       for c in self.expression)

    def generate_line(self, pool: VariablesPool, stream: CodeStream, code_map: CodeMap) -> str:
        with pool.allocate(len(self.intermediates)) as variables:
            self.generate_intermediates(variables, pool, stream, code_map)
            return self.generate_expression_line(variables)

    def generate(self, temp_pool: VariablesPool, stream: CodeStream, code_map: CodeMap, var_name: Optional[str] = None):
        if self.expression == [0]:
            self.intermediates[0].generate(temp_pool, stream, code_map, var_name)
            return
        expression = self.generate_line(temp_pool, stream, code_map)
        if var_name is not None:
            expression = var_name + " = " + expression
        code_map.add(stream.line_number, self.line_number)
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
        line_number = None if any(x is None for x in parts) else min(x.line_number for x in parts)
        result = Expression(line_number, expr_type)

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
        def __init__(self, line_number: int, returns_value: bool, actions: List[Tuple[Expression, List[Expression]]],
                     else_clause: List[Expression]):
            super(ConditionExpression.Intermediate, self).__init__(line_number, Void)
            self.returns_value = returns_value
            self.actions: List[Tuple[Expression, List[Expression]]] = actions
            self.else_clause: List[Expression] = else_clause

        @staticmethod
        def _generate_clause(clause: List[Expression], temp_pool: VariablesPool,
                             stream: CodeStream, code_map: CodeMap, var_name: Optional[str]):
            for line in clause[:-1]:
                line.generate(temp_pool, stream, code_map, None)
            clause[-1].generate(temp_pool, stream, code_map, var_name)

        def _generate_if(self, actions: List[Tuple[Expression, List[Expression]]], temp_pool: VariablesPool,
                         stream: CodeStream, code_map: CodeMap, var_name: Optional[str]):
            condition = actions[0][0].generate_line(temp_pool, stream, code_map)
            code_map.add(stream.line_number, actions[0][0].line_number)
            stream.push_line(f"if {condition}:")
            stream.indent()
            self._generate_clause(actions[0][1], temp_pool, stream, code_map, var_name)
            stream.unindent()
            if len(actions) > 1 or len(self.else_clause) > 0:
                stream.push_line("else:")
                stream.indent()
                if len(actions) > 1:
                    self._generate_if(actions[1:], temp_pool, stream, code_map, var_name)
                else:
                    self._generate_clause(self.else_clause, temp_pool, stream, code_map, var_name)
                stream.unindent()

        def generate(self, temp_pool: VariablesPool, stream: CodeStream, code_map: CodeMap,
                     var_name: Optional[str] = None):
            if not self.returns_value:
                var_name = None
            self._generate_if(self.actions, temp_pool, stream, code_map, var_name)

    def __init__(self, line_number: int, actions: List[Tuple[Expression, List[Expression]]],
                 else_clause: List[Expression]):
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

        super(ConditionExpression, self).__init__(line_number, res_type, [0])
        self.add_intermediate(ConditionExpression.Intermediate(line_number, res_type, actions, else_clause))


class WhileLoopExpression(Expression):
    def __init__(self, line_number: int, condition: Expression, actions: List[Expression]):
        super().__init__(line_number, Void)
        self.condition: Expression = condition
        self.actions: List[Expression] = actions

    def generate(self, temp_pool: VariablesPool, stream: CodeStream, code_map: CodeMap, var_name: Optional[str] = None):
        with temp_pool.allocate(len(self.condition.intermediates)) as cond_vars:
            self.condition.generate_intermediates(cond_vars, temp_pool, stream, code_map)
            code_map.add(stream.line_number, self.condition.line_number)
            stream.push_line("while " + self.condition.generate_expression_line(cond_vars) + ":")
            stream.indent()
            for action in self.actions:
                action.generate(temp_pool, stream, code_map, None)
            self.condition.generate_intermediates(cond_vars, temp_pool, stream, code_map)
            stream.unindent()


class RepeatLoopExpression(Expression):
    def __init__(self, line_number: int, times: Expression, actions: List[Expression]):
        super().__init__(line_number, Void)
        self.times: Expression = times
        self.actions: List[Expression] = actions

    def generate(self, temp_pool: VariablesPool, stream: CodeStream, code_map: CodeMap, var_name: Optional[str] = None):
        with temp_pool.allocate(1) as ctr:
            counter, = ctr
            line = self.times.generate_line(temp_pool, stream, code_map)
            code_map.add(stream.line_number, self.times.line_number)
            stream.push_line(f"for tmp_{counter} in range({line}):")
            stream.indent()
            for action in self.actions:
                action.generate(temp_pool, stream, code_map, None)
            stream.unindent()


class DoWhileLoopExpression(Expression):
    def __init__(self, line_number: int, condition: Expression, actions: List[Expression]):
        super().__init__(line_number, Void)
        self.condition = condition
        self.actions = actions

    def generate(self, temp_pool: VariablesPool, stream: CodeStream, code_map: CodeMap, var_name: Optional[str] = None):
        stream.push_line("while True:")
        stream.indent()
        for action in self.actions:
            action.generate(temp_pool, stream, code_map, None)

        condition = self.condition.generate_line(temp_pool, stream, code_map)
        code_map.add(stream.line_number, self.condition.line_number)
        stream.push(f"if not ({condition}):")
        stream.indent()
        stream.push("break")
        stream.unindent(2)


class ForLoopExpression(Expression):
    def __init__(self, line_number: int, iterator: str, loop_range: Expression, actions: List[Expression]):
        super().__init__(line_number, Void)
        self.iterator: str = iterator
        self.range: Expression = loop_range
        self.actions: List[Expression] = actions

    def generate(self, temp_pool: VariablesPool, stream: CodeStream, code_map: CodeMap, var_name: Optional[str] = None):
        range_expression = self.range.generate_line(temp_pool, stream, code_map)
        code_map.add(stream.line_number, self.range.line_number)
        stream.push(f"for {self.iterator} in {range_expression}:")
        stream.indent()
        for action in self.actions:
            action.generate(temp_pool, stream, code_map, None)
        stream.unindent()


class CubeTurningExpression(Expression):
    def __init__(self, line_number: int, side: str, amount: int):
        super().__init__(line_number, Void)
        self.side: str = side
        self.amount: int = amount
        self.indices: List[Union[Expression, type(Ellipsis)]] = [Expression(line_number, Integer, "1")]

    def generate(self, temp_pool: VariablesPool, stream: CodeStream, code_map: CodeMap,
                 var_name: Optional[str] = None):
        code_map.add(stream.line_number, self.line_number)
        expression = [f"cube_turn({self.side}, {self.amount}, ["]
        for i in range(len(self.indices)):
            expression.append(i)
            expression.append(", ")
        expression[-1] = "])"

        Expression.merge(self.type, expression, *self.indices).generate(temp_pool, stream, code_map, var_name)


class CubeRotationExpression(Expression):
    def __init__(self, line_number: int, side: str, twice: bool = False):
        super().__init__(line_number, Void)
        self.side: str = side
        self.twice: bool = twice

    def generate(self, temp_pool: VariablesPool, stream: CodeStream, code_map: CodeMap, var_name: Optional[str] = None):
        code_map.add(stream.line_number, self.line_number)
        stream.push_line(f"cube_rotate({self.side}, {self.twice})")


class FunctionDeclarationExpression(Expression):
    def __init__(self, line_number: int, name: str, symbol_name: str,
                 return_type: Type, arguments: List[str], clause: List[Expression]):
        super().__init__(line_number, Void)
        self.name: str = name
        self.symbol_name: str = symbol_name
        self.return_type: Type = return_type
        self.arguments: List[str] = arguments
        self.clause: List[Expression] = clause

    def generate(self, temp_pool: VariablesPool, stream: CodeStream, code_map: CodeMap, var_name: Optional[str] = None):
        arguments = ", ".join(self.arguments)
        stream.push_line(f"@runtime_function(\"{self.symbol_name}\")")
        stream.push_line(f"def {self.name}({arguments}):")
        stream.indent()
        for expression in self.clause:
            expression.generate(temp_pool, stream, code_map, None)
        if self.return_type != Void:
            stream.push_line("return " + self.return_type.default_value())
        elif len(self.clause) == 0:
            stream.push_line("pass")
        stream.unindent()
