from termcolor import colored
from typing import IO, Iterable, Tuple, Optional, List
import textwrap
from ..compiler.types import Function, Void, Type
from ..compiler.code_map import CodeMap
from ..execution import RuntimeError
from ..execution.executor import ITracebackWriter


class ErrorsOutput(ITracebackWriter):
    def __init__(self, stream: IO, use_color: bool = False):
        self.stream = stream
        self.max_width = 80
        self.use_color = use_color
        self.line_number_margin = 2
        self.text_indent = 4

    def _echo(self, text: str, color: str = None, nl: bool = False) -> None:
        if self.use_color and color is not None:
            self.stream.write(colored(text, color))
        else:
            self.stream.write(text)
        if nl:
            self.stream.write("\n")

    def _write_lines(self, line_num: str, text: str) -> \
            Iterable[Tuple[int, int]]:
        offset = 0
        width = self.max_width - self.line_number_margin - len(line_num)
        while offset < len(text):
            if offset == 0:
                self._echo(line_num + " " * self.line_number_margin, "cyan")
            else:
                self._echo(" " * (len(line_num) + self.line_number_margin))
            substring = text[offset: offset + width]
            self._echo(substring, nl=True)
            yield offset, offset + len(substring)
            offset += len(substring)

    def _write_lines_with_error(self, line_num: str, text: str,
                                start_col: int, end_col: int) -> None:
        for first, last in self._write_lines(line_num, text):
            if start_col >= last or end_col < first:
                continue
            error_start = max(first, start_col) - first
            error_end = min(last, end_col + 1) - first
            self._echo(" " * (error_start + self.line_number_margin + len(line_num)))
            self._echo("^" * (error_end - error_start), "red", nl=True)

    def _write_lines_all(self, line_num: str, text: str) -> None:
        for _, _ in self._write_lines(line_num, text):
            continue

    def display_code(self, code: str, start_line: int, start_column: int,
                     end_line: int, end_column: int) -> None:
        line_num_width = len(str(end_line))
        code = code.split("\n")

        def write(ln: int) -> None:
            self._write_lines_all(f"{ln + 1:{line_num_width}}", code[ln])

        if end_line - start_line >= 5:
            for line in range(start_line, start_line + 2):
                write(line)
            self._echo("...", nl=True)
            for line in range(end_line - 1, end_line + 1):
                write(line)
        elif end_line != start_line:
            for line in range(start_line, end_line + 1):
                write(line)
        else:
            line_num = f"{start_line + 1:{line_num_width}}"
            self._write_lines_with_error(line_num, code[start_line],
                                         start_column, end_column)

    def write_function_overloads(self, func_name: str, function: Function):
        self._echo("Function arguments:", nl=True, color="yellow")
        for overload in function.overloads:
            indent = self.text_indent + len(func_name) + 1
            offset = indent
            self._echo(" " * self.text_indent + func_name + "(")
            for i, argument in enumerate(overload.arguments):
                string = str(argument)
                if i < len(overload.arguments) - 1:
                    string += ", "
                if offset + len(string) < self.max_width + 1:
                    self._echo(string)
                    offset += len(string)
                else:
                    self._echo("", nl=True)
                    self._echo(" " * indent + string)
                    offset = indent + len(string)
            if overload.return_type == Void:
                ending = ")"
            else:
                ending = f"): {overload.return_type}"
            if offset + len(ending) > self.max_width:
                self._echo("", nl=True)
                self._echo(" " * (indent - 1) + ending, nl=True)
            else:
                self._echo(ending, nl=True)
        self._echo("", nl=True)

    def write_supplied_arguments(self, arguments: List[Type]) -> None:
        self._echo("Supplied arguments:", nl=True, color="yellow")
        self._echo(" " * self.text_indent)
        offset = self.text_indent
        for i, argument in enumerate(arguments):
            string = str(argument)
            if i < len(arguments) - 1:
                string += ", "
            if offset + len(string) > self.max_width:
                self._echo("", nl=True)
                self._echo(" " * self.text_indent + string)
                offset = self.text_indent + len(string)
            else:
                self._echo(string)
                offset += len(string)
        self._echo("\n\n")

    def write_error(self, message: str,
                    line: Optional[int] = None,
                    column: Optional[int] = None):
        header = ["[error"]
        if line is not None or column is not None:
            header.append(" at")
            if line is not None:
                header.append(" line ")
                header.append(str(line + 1))
            if column is not None:
                header.append(" column ")
                header.append(str(column + 1))
        header.append("]")

        self._echo("".join(header), "red", nl=True)

        prefix = " " * self.text_indent
        for line in textwrap.wrap(message, self.max_width - self.text_indent):
            self._echo(prefix + line, nl=True)
        self._echo("", nl=True)

    def print_traceback(self, e: RuntimeError, code_map: CodeMap):
        self._echo("[runtime error]\n", "red", nl=True)
        for line in textwrap.wrap(str(e), self.max_width - self.text_indent):
            self._echo(" " * self.text_indent + line, nl=True)
        self._echo("\n")
        self._echo("Stack trace:", nl=True, color="yellow")
        for func, line in e.stack_entries:
            line_number = "?" if line is None else code_map[line] + 1
            self._echo(" " * self.text_indent + f"line {line_number:<5}")
            if func is None:
                self._echo("\n")
            else:
                self._echo(f": {func}", nl=True)
