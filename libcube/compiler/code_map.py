from typing import Dict


class CodeMap:
    def __init__(self):
        self.line_numbers: Dict[int, int] = dict()

    def add(self, python_line: int, source_line: int) -> None:
        if source_line is not None and python_line is not None:
            self.line_numbers[python_line] = source_line

    def __getitem__(self, index: int):
        while index > 0 and index not in self.line_numbers:
            index -= 1
        if index in self.line_numbers:
            return self.line_numbers[index]
        else:
            return 0
