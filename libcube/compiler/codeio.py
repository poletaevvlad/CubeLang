from io import StringIO


class CodeStream:
    INDENTATION = "    "

    def __init__(self):
        self.io = StringIO()
        self.indentation: int = 0
        self.line_number: int = 0

    def push_line(self, text: str) -> None:
        self.io.write((CodeStream.INDENTATION * self.indentation) + text + "\n")
        self.line_number += 1

    def push(self, text: str) -> None:
        for line in text.split("\n"):
            self.push_line(line)

    def indent(self, by: int = 1) -> None:
        self.indentation += by

    def unindent(self, by: int = 1) -> None:
        self.indentation -= by

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is None:
            self.io.close()

    def get_contents(self):
        self.io.seek(0)
        return self.io.read()
