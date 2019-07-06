import railroad
import os
from io import StringIO
import re

RUNTIME = {"Diagram": railroad.Diagram,
           "Terminal": railroad.Terminal,
           "NonTerminal": railroad.NonTerminal,
           "Comment": railroad.Comment,
           "Skip": railroad.Skip,
           "Start": railroad.Start,
           "End": railroad.End,
           "Sequence": railroad.Sequence,
           "Stack": railroad.Stack,
           "OptionalSequence": railroad.OptionalSequence,
           "Choice": railroad.Choice,
           "MultipleChoice": railroad.MultipleChoice,
           "HorizontalChoice": railroad.HorizontalChoice,
           "Optional": railroad.Optional,
           "OneOrMore": railroad.OneOrMore,
           "ZeroOrMore": railroad.ZeroOrMore}


def main():
    dir = os.path.dirname(os.path.abspath(__file__))
    for file in os.listdir(dir):
        if not file.endswith(".railroad"):
            continue
        with open(file) as f:
            file_contents = f.read()

        value: railroad.Diagram = eval(file_contents, RUNTIME)
        svg = StringIO()
        value.writeSvg(svg.write)

        with open(dir + "/out/" + file[:-9] + ".svg", "w") as f:
            f.write("""<?xml version="1.0" encoding="utf-8"?>\n""")
            svg_text = svg.getvalue()
            svg_text = svg_text.replace("<svg", "<svg  xmlns=\"http://www.w3.org/2000/svg\"", 1)
            f.write(re.sub(r"&#\d+", r"\g<0>;", svg_text))
        print(file)


if __name__ == "__main__":
    main()
