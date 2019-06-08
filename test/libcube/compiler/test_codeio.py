from libcube.compiler.codeio import CodeStream


def test_simple_push():
    with CodeStream() as stream:
        stream.push_line("Hello")
        assert stream.line_number == 1
        stream.push_line("world")
        assert stream.line_number == 2
        assert stream.get_contents() == "Hello\nworld\n"


def test_push_indent():
    with CodeStream() as stream:
        stream.push_line("a")
        stream.indent()
        stream.push_line("b")
        stream.unindent()
        stream.push_line("c")
        assert stream.line_number == 3
        assert stream.get_contents() == "a\n    b\nc\n"


def test_batch_push():
    with CodeStream() as stream:
        stream.indent(2)
        stream.push("a\nb\nc")
        assert stream.get_contents() == "        a\n        b\n        c\n"
