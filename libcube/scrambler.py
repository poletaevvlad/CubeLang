from typing import Optional

import click
import random

from libcube.actions import Turn
from libcube.cube import Cube
from libcube.orientation import Orientation, Side
from libcube.parser import get_action_representation

# noinspection PyTypeChecker
SIDES = tuple(Side)


@click.command()
@click.option("-n", "turns_num", type=int, default=20)
@click.option("-o", "output_type", type=click.Choice(["turns", "colors"]),
              default="turns")
@click.option("-s", "seed")
def main(turns_num: int, output_type: str, seed: Optional[str]):
    if seed is not None:
        random.seed(seed)

    actions = (Turn(random.choice(SIDES), 1, random.randint(1, 3))
               for _ in range(turns_num))
    if output_type == "turns":
        for action in actions:
            print(get_action_representation(action), end="")
        print()
    else:
        cube = Cube((3, 3, 3))
        orientation = Orientation()
        for action in actions:
            action.perform(cube, orientation)

        print("--front", repr(cube.get_side(orientation).colors))
        print("--right", repr(cube.get_side(orientation.to_right).colors))
        print("--left", repr(cube.get_side(orientation.to_left).colors))
        print("--back", repr(cube.get_side(orientation.to_right.to_right).colors))
        print("--top", repr(cube.get_side(orientation.to_top).colors))
        print("--bottom", repr(cube.get_side(orientation.to_bottom).colors))


if __name__ == "__main__":
    main()
