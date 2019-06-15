from types import CodeType
from typing import Iterator, Dict, Any
from ..compiler.expression import Expression
from ..compiler.codeio import CodeStream
from ..compiler.stack import VariablesPool
from ..compiler.code_map import CodeMap
from .rt_error import RuntimeError, TerminateExecutionError
from .rt_function import runtime_function
from abc import ABC, abstractmethod


class ITracebackWriter(ABC):
    @abstractmethod
    def print_traceback(self, error: RuntimeError, code_map: CodeMap) -> None:
        pass


class ExecutionContext:
    def __init__(self, globals: Dict[str, Any]):
        self.source: CodeType = None
        self.globals: Dict[str, Any] = globals
        self.globals["runtime_function"] = runtime_function
        self.code_map = CodeMap()

    def compile(self, program: Iterator[Expression]):
        source = self.compile_source(program)
        # print(source)
        self.source = compile(source, "<string>", "exec")

    def compile_source(self, program: Iterator[Expression]) -> str:
        stream = CodeStream()
        variables = VariablesPool()

        for expression in program:
            expression.generate(variables, stream, self.code_map)
        return stream.get_contents()

    def execute(self, error: ITracebackWriter) -> bool:
        if self.source is None:
            raise RuntimeError("Illegal state: program must be compiled first")
        try:
            exec(self.source, self.globals)
            return True
        except TerminateExecutionError:
            return True
        except Exception as e:
            e = RuntimeError.update_error(None, e)
            error.print_traceback(e, self.code_map)
            return False
