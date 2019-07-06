import sys
from argparse import ArgumentParser

from lark import UnexpectedCharacters
from lark.exceptions import LarkError

from .cube_builder import init_cube_args_parser, build_cube
from .error_display import ErrorsOutput
from .options import file_contents_type
from .postprocessors_builder import init_postprocessors_args_parser, build_postprocessors_chain
from ..compiler import Stack, parser
from ..compiler.errors import CompileTimeError, FunctionArgumentsError
from ..cube_runtime import CubeRuntime
from ..execution import ExecutionContext
from ..stdlib import stdlib
from .. import __version__


def main():
    args_parser = ArgumentParser()
    args_parser.add_argument("source", type=file_contents_type,
                             help="program's source")
    args_parser.add_argument("-v", "--version", action="version", version="%(prog)s " + __version__)

    init_cube_args_parser(args_parser)
    init_postprocessors_args_parser(args_parser)
    args = args_parser.parse_args()

    cube, orientation = build_cube(args)
    postprocessor = build_postprocessors_chain(args)
    runtime = CubeRuntime(cube, orientation, postprocessor.process, postprocessor.done)

    stack = Stack()
    stdlib.initialize_stack(stack)
    runtime.functions.initialize_stack(stack)
    exec_globals = {**stdlib.exec_globals, **runtime.functions.exec_globals}
    context = ExecutionContext(exec_globals)

    errors = ErrorsOutput(sys.stderr, use_color=True)
    try:
        program = parser.parse(args.source, stack)
        context.compile(program)
    except UnexpectedCharacters as e:
        errors.write_error(f"Unexpected character: `{args.source[e.pos_in_stream]}`", e.line - 1, e.column - 1)
        errors.display_code(args.source, e.line - 1, e.column - 1, e.line - 1, e.column - 1)
        return
    except LarkError as e:
        errors.write_error(str(e))
        return
    except CompileTimeError as e:
        message = str(e)
        errors.write_error(message, e.start_line, e.start_column)
        if isinstance(e, FunctionArgumentsError):
            errors.write_supplied_arguments(e.arguments)
            errors.write_function_overloads(e.function_name, e.function)

        end_line = e.end_line if e.end_line is not None else e.start_line
        end_column = e.end_column if e.end_column is not None else e.start_column
        errors.display_code(args.source, e.start_line - 1, e.start_column - 1, end_line - 1, end_column - 1)
        return

    # if not pycode:
    context.execute(errors)
    runtime.finished()
