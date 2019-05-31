from typing import IO, Optional, List

import click
from click.exceptions import BadOptionUsage
from lark.exceptions import LarkError, UnexpectedCharacters

from ..compiler.codeio import CodeStream
from ..compiler.expression import VariablesPool
from .error_display import ErrorsOutput
from .options import CubeFormulaParamType, SideConfigurationType
from ..compiler.errors import CompileTimeError, FunctionArgumentsError
from ..compiler.executor import ExecutionContext
from ..compiler.parser import parser, Stack
from ..cube_runtime import CubeRuntime
from ..stdlib import stdlib
from ..actions import Action
from ..parser import get_action_representation
from ..cube import Cube
from ..orientation import Orientation, Color


def display_action(action: Action):
    print(get_action_representation(action), end="")


def apply_side(cube: Cube, orientation: Orientation,
               colors: Optional[List[List[Color]]], option_name: str):
    if colors is None:
        return
    side = cube.get_side(orientation)
    if side.rows != len(colors):
        raise BadOptionUsage(option_name, "Incorrect number of lines")
    elif side.columns != len(colors[0]):
        raise BadOptionUsage(option_name, "Incorrect number of columns")

    for i, line in enumerate(colors):
        for j, color in enumerate(line):
            side.colors[i, j] = color


def init_cube(cube, shuffle, front, left, top, right, bottom, back):
    orientation = Orientation()
    apply_side(cube, orientation, front, "front")
    apply_side(cube, orientation.to_right, right, "right")
    apply_side(cube, orientation.to_left, left, "left")
    apply_side(cube, orientation.to_right.to_right, back, "back")
    apply_side(cube, orientation.to_top, top, "top")
    apply_side(cube, orientation.to_bottom, bottom, "bottom")

    for shuffle_action in shuffle:
        orientation = shuffle_action.perform(cube, orientation)


@click.command()
@click.argument("source", type=click.File("r"))
@click.option("-s", "--shuffle", type=CubeFormulaParamType(), default=[])
@click.option("--front", type=SideConfigurationType(), default=None)
@click.option("--left", type=SideConfigurationType(), default=None)
@click.option("--top", type=SideConfigurationType(), default=None)
@click.option("--right", type=SideConfigurationType(), default=None)
@click.option("--bottom", type=SideConfigurationType(), default=None)
@click.option("--back", type=SideConfigurationType(), default=None)
@click.option("--pycode", is_flag=True)
def main(source: IO,
         shuffle: Optional[List[Action]],
         front: Optional[List[List[Color]]],
         left: Optional[List[List[Color]]],
         top: Optional[List[List[Color]]],
         right: Optional[List[List[Color]]],
         bottom: Optional[List[List[Color]]],
         back: Optional[List[List[Color]]],
         pycode: bool):
    cube = Cube((3, 3, 3))
    init_cube(cube, shuffle, front, left, top, right, bottom, back)

    runtime = CubeRuntime(cube, display_action)

    stack = Stack()
    stdlib.initialize_stack(stack)
    runtime.functions.initialize_stack(stack)

    exec_globals = {**stdlib.exec_globals, **runtime.functions.exec_globals}
    context = ExecutionContext(exec_globals)

    text = source.read()

    errors = ErrorsOutput(click.get_text_stream("stderr"))

    try:
        program = parser.parse(text, stack)
        if pycode:
            stream = CodeStream()
            variables = VariablesPool()
            for expression in program:
                expression.generate(variables, stream)
            print(stream.get_contents())
        else:
            context.compile(program)
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
            errors.write_supplied_arguments(e.arguments)
            errors.write_function_overloads(e.function_name, e.function)

        end_line = e.end_line if e.end_line is not None else e.start_line
        end_column = e.end_column if e.end_column is not None else e.start_column
        errors.display_code(text, e.start_line - 1, e.start_column - 1, end_line - 1, end_column - 1)
        return

    if not pycode:
        context.execute()
