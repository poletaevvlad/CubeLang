from types import CodeType
from typing import Iterator, Dict, Any
from compiler.expression import Expression
from compiler.codeio import CodeStream
from compiler.stack import VariablesPool


class ExecutionContext:
    def __init__(self, globals: Dict[str, Any]):
        self.source: CodeType = None
        self.globals: Dict[str, Any] = globals

    def compile(self, program: Iterator[Expression]):
        source = self.compile_source(program)
        self.source = compile(source, "<string>", "exec")

    def compile_source(self, program: Iterator[Expression]) -> str:
        stream = CodeStream()
        variables = VariablesPool()

        for expression in program:
            expression.generate(variables, stream)
        return stream.get_contents()

    def execute(self):
        if self.source is None:
            raise RuntimeError("Illegal state: program must be compiled first")
        exec(self.source, self.globals)
