from typing import IO

import click
from lark.exceptions import LarkError, UnexpectedCharacters

from .error_display import ErrorsOutput
from ..compiler.errors import CompileTimeError, FunctionArgumentsError
from ..compiler.executor import ExecutionContext
from ..compiler.parser import parser, Stack
from ..cube_runtime import CubeRuntime
from ..stdlib import stdlib


@click.command()
@click.argument("source", type=click.File("r"))
def main(source: IO):
    runtime = CubeRuntime(lambda: None)

    stack = Stack()
    stdlib.initialize_stack(stack)
    runtime.functions.initialize_stack(stack)

    exec_globals = {**stdlib.exec_globals, **runtime.functions.exec_globals}
    context = ExecutionContext(exec_globals)

    text = source.read()

    errors = ErrorsOutput(click.get_text_stream("stderr"))

    try:
        context.compile(parser.parse(text, stack))
    except UnexpectedCharacters as e:
        errors.write_error(f"Unexpected character: `{text[e.pos_in_stream]}`", e.line - 1, e.column - 1)
        errors.display_code(text, e.line - 1, e.column - 1, e.line - 1, e.column - 1)
        return
    except LarkError as e:
        errors.write_error(str(e))
        return
    except CompileTimeError as e:
        message = str(e)
        errors.write_error(message, e.start_line, e.start_column)
        if isinstance(e, FunctionArgumentsError):
            errors.write_function_overloads(e.function_name, e.function)

        end_line = e.end_line if e.end_line is not None else e.start_line
        end_column = e.end_column if e.end_column is not None else e.start_column
        errors.display_code(text, e.start_line - 1, e.start_column - 1, end_line - 1, end_column - 1)
        return

    context.execute()
