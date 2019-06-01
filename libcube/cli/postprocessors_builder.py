from argparse import ArgumentParser, Namespace

from ..postprocessing import OptimizingPostprocessor, FormattingPostprocessor, \
    OrientationFreezePostprocessor, chain, PostprocessorBase


def init_postprocessors_args_parser(parser: ArgumentParser) -> None:
    parser.add_argument("-o", "--not-optimize", dest="optimize", action='store_false',
                        help="do not eliminate redundant turns and rotations")
    parser.add_argument("-r", "--no-rotations", dest="freeze_orientation", action="store_true",
                        help="do not produce rotations")


def print_action(action: str):
    print(action, end="")


def build_postprocessors_chain(args: Namespace) -> PostprocessorBase:
    postprocessors = []

    if args.freeze_orientation:
        postprocessors.append(OrientationFreezePostprocessor())
    if args.optimize:
        postprocessors.append(OptimizingPostprocessor())
    postprocessors.append(FormattingPostprocessor())

    chain(*postprocessors, print_action)
    return postprocessors[0]
