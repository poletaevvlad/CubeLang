from click import secho
from typing import IO, Iterable, Tuple


class ErrorsOutput:
    def __init__(self, stream: IO):
        self.stream = stream
        self.max_width = 80
        self.use_color = True
        self.line_number_margin = 2

    def _echo(self, text: str, color: str = None, nl: bool = False) -> None:
        if self.use_color and color is not None:
            self.stream.write(text)
            if nl:
                self.stream.write("\n")
        else:
            secho(text, self.stream, nl, color=color)

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
            self._echo("~" * (error_end - error_start), nl=True)

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
