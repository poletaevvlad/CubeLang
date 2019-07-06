from typing import Dict, NamedTuple, Optional

from .expression import VariablesPool
from .types import Type


class VariableDefinition(NamedTuple):
    type: Type
    number: int


class StackFrame:
    def __init__(self, top_frame: Optional["StackFrame"]):
        self.variables: Dict[str, VariableDefinition] = dict()
        self.top_frame: Optional[StackFrame] = top_frame


class Stack:
    def __init__(self, return_type: Optional[Type] = None):
        self.globals: Dict[str, VariableDefinition] = {}
        self.stack_top: StackFrame = StackFrame(None)
        self.pool: VariablesPool = VariablesPool()
        self.context_return_type: Optional[Type] = return_type

    def add_frame(self) -> None:
        self.stack_top = StackFrame(self.stack_top)

    def pop_frame(self) -> None:
        self.pool.deallocate(len(self.stack_top.variables))
        self.stack_top = self.stack_top.top_frame

    def get_variable(self, name: str, ) -> Optional[VariableDefinition]:
        frame = self.stack_top
        while frame is not None:
            if name in frame.variables:
                return frame.variables[name]
            frame = frame.top_frame
        if name in self.globals:
            return self.globals[name]
        return None

    def add_variable(self, name: str, var_type: Type) -> int:
        number = self.pool.allocate_single()
        definition = VariableDefinition(var_type, number)
        self.stack_top.variables[name] = definition
        return number

    def add_global(self, name: str, var_type: Type) -> None:
        self.globals[name] = VariableDefinition(var_type, -1)

    def create_inner(self, return_type: Optional[Type]) -> "Stack":
        stack = Stack(return_type)
        stack.globals = self.globals
        return stack
