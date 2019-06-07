from unittest.mock import MagicMock, call

from libcube.actions import Turn
from libcube.orientation import Side
from libcube.postprocessing.formatter import FormattingPostprocessor


def test_formatting():
    a1 = Turn(Side.LEFT, 1, 1)
    a2 = Turn(Side.TOP, 1, 1)

    fp = FormattingPostprocessor()
    fp.callback = MagicMock()
    fp.process(a1)
    fp.process(a2)
    fp.done()

    assert fp.callback.call_args_list == [call("L"), call("U")]
