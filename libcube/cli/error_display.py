from click import secho
from typing import IO, Iterable, Tuple, Optional
import textwrap


class ErrorsOutput:
    def __init__(self, stream: IO):
        self.stream = stream
        self.max_width = 80
        self.use_color = True
        self.line_number_margin = 2
        self.text_indent = 4

    def _echo(self, text: str, color: str = None, nl: bool = False) -> None:
        if self.use_color and color is not None:
            secho(text, self.stream, nl, fg=color)
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
            self._echo("^" * (error_end - error_start), "bright_red", nl=True)

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

        self._echo("".join(header), "bright_red", nl=True)

        prefix = " " * self.text_indent
        for line in textwrap.wrap(message, self.max_width - self.text_indent):
            self._echo(prefix + line, nl=True)
        self._echo("", nl=True)
