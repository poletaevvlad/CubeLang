from libcube.postprocessing.formatter import FormattingPostprocessor
from libcube.actions import Turn
from libcube.orientation import Side
from unittest.mock import patch, MagicMock, call


def test_formatting():
    with patch("libcube.postprocessing.formatter.get_action_representation") as mock_function:
        a1 = Turn(Side.LEFT, 1, 1)
        a2 = Turn(Side.TOP, 1, 1)

        fp = FormattingPostprocessor()
        fp.callback = MagicMock()
        mock_function.return_value = "A"
        fp.process(a1)
        mock_function.return_value = "B"
        fp.process(a2)
        fp.done()

        assert mock_function.call_args_list == [call(a1), call(a2)]
        assert fp.callback.call_args_list == [call("A"), call("B")]
