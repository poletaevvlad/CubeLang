from argparse import ArgumentParser

from ..compiler import Stack, ExecutionContext
from ..stdlib import stdlib
from .cube_builder import init_cube_args_parser, build_cube
from .options import file_contents_type
from ..actions import Action
from ..cube_runtime import CubeRuntime
from ..parser import get_action_representation


def display_action(action: Action):
    print(get_action_representation(action), end="")


def main():
    args_parser = ArgumentParser()
    args_parser.add_argument("source", type=file_contents_type,
                             help="program's source")
    init_cube_args_parser(args_parser)
    args = args_parser.parse_args()

    cube, orientation = build_cube(args)
    runtime = CubeRuntime(cube, display_action, orientation)

    stack = Stack()
    stdlib.initialize_stack(stack)
    runtime.functions.initialize_stack(stack)
    exec_globals = {**stdlib.exec_globals, **runtime.functions.exec_globals}
    context = ExecutionContext(exec_globals)

    # errors = ErrorsOutput(click.get_text_stream("stderr"))
    #
    # try:
    #     program = parser.parse(text, stack)
    #     if pycode:
    #         stream = CodeStream()
    #         variables = VariablesPool()
    #         for expression in program:
    #             expression.generate(variables, stream)
    #         print(stream.get_contents())
    #     else:
    #         context.compile(program)
    # except UnexpectedCharacters as e:
    #     errors.write_error(f"Unexpected character: `{text[e.pos_in_stream]}`", e.line - 1, e.column - 1)
    #     errors.display_code(text, e.line - 1, e.column - 1, e.line - 1, e.column - 1)
    #     return
    # except LarkError as e:
    #     errors.write_error(str(e))
    #     return
    # except CompileTimeError as e:
    #     message = str(e)
    #     errors.write_error(message, e.start_line, e.start_column)
    #     if isinstance(e, FunctionArgumentsError):
    #         errors.write_supplied_arguments(e.arguments)
    #         errors.write_function_overloads(e.function_name, e.function)
    #
    #     end_line = e.end_line if e.end_line is not None else e.start_line
    #     end_column = e.end_column if e.end_column is not None else e.start_column
    #     errors.display_code(text, e.start_line - 1, e.start_column - 1, end_line - 1, end_column - 1)
    #     return
    #
    # if not pycode:
    #     context.execute()
