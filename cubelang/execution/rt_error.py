import traceback
from typing import Optional, NamedTuple, List


class TerminateExecutionError(Exception):
    pass


class RuntimeError(Exception):
    ACCEPTED_EXCEPTIONS = [ValueError, IndexError]

    class StackEntry(NamedTuple):
        function_name: Optional[str]
        line_number: int

    def __init__(self, message: Optional[str]):
        super().__init__(message)
        self.stack_entries: List[RuntimeError.StackEntry] = []
        self.next_name: Optional[str] = None

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
            exp.next_name = e.next_name
        else:
            if not any(isinstance(e, Exp) for Exp in RuntimeError.ACCEPTED_EXCEPTIONS):
                raise e
            exp = RuntimeError(str(e))
        line_num = RuntimeError.get_exception_line(e)
        if line_num is not None:
            exp.add_stack_entry(exp.next_name if func_name is None else func_name,
                                line_num)
        else:
            exp.next_name = func_name
        return exp
