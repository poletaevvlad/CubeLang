from argparse import ArgumentParser
from libcube.cli.postprocessors_builder import init_postprocessors_args_parser, \
    build_postprocessors_chain, print_action
from libcube.postprocessing import OptimizingPostprocessor, FormattingPostprocessor, \
    OrientationFreezePostprocessor
import pytest
from unittest import mock


@pytest.fixture
def parser():
    arg_parser = ArgumentParser()
    init_postprocessors_args_parser(arg_parser)
    return arg_parser


@pytest.mark.parametrize("args, types", [
    ([], [OptimizingPostprocessor, FormattingPostprocessor]),
    (["--not-optimize"], [FormattingPostprocessor]),
    (["--no-rotations"], [OrientationFreezePostprocessor, OptimizingPostprocessor, FormattingPostprocessor]),
    (["-ro"], [OrientationFreezePostprocessor, FormattingPostprocessor])
])
@mock.patch("libcube.cli.postprocessors_builder.chain")
def test_default(chain_mock: mock.MagicMock, parser, args, types):
    args = parser.parse_args(args)
    pp = build_postprocessors_chain(args)

    assert isinstance(pp, types[0])
    for expected, real in zip(chain_mock.call_args_list[0][0], types):
        assert isinstance(expected, real)
    assert chain_mock.call_args_list[0][0][-1] == print_action
