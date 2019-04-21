from typing import Callable

from libcube.actions import Action, Turn
from libcube.orientation import Side
from libcube.cube_runtime import CubeRuntime
from unittest.mock import MagicMock


def test_runtime_globals():
    runtime = CubeRuntime(lambda action: None)
    existing = set(runtime.functions.global_values.keys())
    assert existing.issuperset(set(CubeRuntime.COLOR_NAMES.keys()))
    assert existing.issuperset(set(CubeRuntime.SIDE_NAMES.keys()))
    assert "cube_turn" in existing


def test_action_callback():
    callback: Callable[[Action], None] = MagicMock()
    runtime = CubeRuntime(callback)
    runtime.perform_turn(Side.LEFT, 2)

    callback: MagicMock
    action = callback.call_args_list[0][0][0]
    assert isinstance(action, Turn)
    assert action.side == Side.LEFT
