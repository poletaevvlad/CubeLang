from typing import Callable

from libcube.actions import Action, Turn, TurningType
from libcube.orientation import Side, Orientation
from libcube.cube_runtime import CubeRuntime
from libcube.cube import Cube
from unittest.mock import MagicMock
from unittest.mock import patch
import pytest


def test_runtime_globals():
    runtime = CubeRuntime(Cube((3, 3, 3)), Orientation(), lambda action: None, lambda: None)
    existing = set(runtime.functions.global_values.keys())
    assert existing.issuperset(set(CubeRuntime.COLOR_NAMES.keys()))
    assert existing.issuperset(set(CubeRuntime.SIDE_NAMES.keys()))
    assert "cube_turn" in existing


def test_action_callback():
    callback: Callable[[Action], None] = MagicMock()
    runtime = CubeRuntime(Cube((3, 3, 3)), Orientation(), callback, lambda: None)
    runtime.perform_turn(Side.LEFT, 2)

    callback: MagicMock
    action = callback.call_args_list[0][0][0]
    assert isinstance(action, Turn)
    assert action.type == TurningType.VERTICAL


@pytest.mark.parametrize("side, orientation", [
    (Side.FRONT, Orientation(Side.FRONT, Side.TOP)),
    (Side.LEFT, Orientation(Side.LEFT, Side.TOP)),
    (Side.RIGHT, Orientation(Side.RIGHT, Side.TOP)),
    (Side.BACK, Orientation(Side.BACK, Side.TOP)),
    (Side.TOP, Orientation(Side.TOP, Side.BACK)),
    (Side.BOTTOM, Orientation(Side.BOTTOM, Side.FRONT))
])
def test_get_color(side, orientation):
    class Colors:
        def __getitem__(self, item):
            pass

    class Side:
        def __init__(self):
            self.colors = Colors()

    with patch.object(Cube, 'get_side', return_value=Side()) as mock_method:
        runtime = CubeRuntime(Cube((3, 3, 3)), Orientation(), lambda action: None, lambda: None)
        runtime.get_color(side, 0, 0)
        mock_method.assert_called_once_with(orientation)
