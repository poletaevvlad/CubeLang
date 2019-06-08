import traceback
from typing import Optional, NamedTuple, List


class RuntimeError(Exception):
    ACCEPTED_EXCEPTIONS = [ValueError, IndexError]

    class StackEntry(NamedTuple):
        function_name: Optional[str]
        line_number: int

    def __init__(self, message: Optional[str]):
        super().__init__(message)
        self.stack_entries: List[RuntimeError.StackEntry] = []

    def add_stack_entry(self, func_name: Optional[str], line_number: int):
        entry = RuntimeError.StackEntry(func_name, line_number)
        self.stack_entries.append(entry)

    @staticmethod
    def get_exception_line(e: Exception) -> int:
        for frame in reversed(traceback.extract_tb(e.__traceback__)):
            if frame.filename == "<string>":
                return frame.lineno - 1

    @staticmethod
    def update_error(func_name: Optional[str], e: Exception) -> "RuntimeError":
        if isinstance(e, RuntimeError):
            exp = RuntimeError(str(e))
            exp.stack_entries = e.stack_entries[::]
        else:
            if not any(isinstance(e, Exp) for Exp in RuntimeError.ACCEPTED_EXCEPTIONS):
                raise e
            exp = RuntimeError(str(e))
        exp.add_stack_entry(func_name, RuntimeError.get_exception_line(e))
        return exp
