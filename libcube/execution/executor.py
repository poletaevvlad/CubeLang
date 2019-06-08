from types import CodeType
from typing import Iterator, Dict, Any
from ..compiler.expression import Expression
from ..compiler.codeio import CodeStream
from ..compiler.stack import VariablesPool
from ..compiler.code_map import CodeMap
from .rt_function import runtime_function


class ExecutionContext:
    def __init__(self, globals: Dict[str, Any]):
        self.source: CodeType = None
        self.globals: Dict[str, Any] = globals
        self.globals["runtime_function"] = runtime_function
        self.code_map = CodeMap()

    def compile(self, program: Iterator[Expression]):
        source = self.compile_source(program)
        self.source = compile(source, "<string>", "exec")

    def compile_source(self, program: Iterator[Expression]) -> str:
        stream = CodeStream()
        variables = VariablesPool()

        for expression in program:
            expression.generate(variables, stream, self.code_map)
        return stream.get_contents()

    def execute(self):
        if self.source is None:
            raise RuntimeError("Illegal state: program must be compiled first")
        exec(self.source, self.globals)
