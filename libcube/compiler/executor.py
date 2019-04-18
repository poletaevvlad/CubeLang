from typing import Iterator, Dict, Any, Optional
from .expression import Expression
from .codeio import CodeStream
from .stack import VariablesPool


class ExecutionContext:
    def __init__(self, globals: Dict[str, Any]):
        self.source: Optional[str] = None
        self.globals: Dict[str, Any] = globals

    def compile(self, program: Iterator[Expression]):
        stream = CodeStream()
        variables = VariablesPool()

        for expression in program:
            expression.generate(variables, stream)

        self.source = stream.get_contents()

    def execute(self):
        if self.source is None:
            raise RuntimeError("Illegal state: program must be compiled first")
        exec(self.source, self.globals)
