import random
from argparse import ArgumentParser
from typing import List

from cubelang.actions import Turn
from cubelang.cli.options import integer_type
from cubelang.cube import Cube
from cubelang.orientation import Orientation, Side

# noinspection PyTypeChecker
SIDES = tuple(Side)


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-d", dest="dimension", help="dimensions of a cube",
                            default=3, metavar="N", type=integer_type(2))
    arg_parser.add_argument("-n", dest="turns_num", help="number of turns",
                            type=integer_type(1), default=20)
    arg_parser.add_argument("-a", dest="output_args", action="store_true",
                            help="display the state of the cube after the turns instead of the formula")
    arg_parser.add_argument("-s", dest="seed", help="the seed for the pseudorandom number generator")
    args = arg_parser.parse_args()
    dim = args.dimension

    if args.seed is not None:
        random.seed(args.seed)

    actions: List[Turn] = []
    prev_side = None
    for i in range(args.turns_num):
        if prev_side is None:
            sides = SIDES
        else:
            sides = [x for x in SIDES if x != prev_side]

        prev_side = random.choice(sides)

        first_index = random.randint(1, dim // 2)
        last_index = random.randint(1, first_index)
        if first_index == last_index:
            indices = [first_index]
        else:
            indices = [last_index, ..., first_index]

        turn = Turn(prev_side, indices, random.randint(1, 3))
        actions.append(turn)

    if not args.output_args:
        for action in actions:
            print(str(action), end="")
        print()
    else:
        cube = Cube((dim,) * 3)
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
