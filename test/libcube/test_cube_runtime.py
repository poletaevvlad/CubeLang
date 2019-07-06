from typing import Callable
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from cubelang.actions import Action, Turn, TurningType
from cubelang.cube import Cube
from cubelang.cube_runtime import CubeRuntime
from cubelang.orientation import Side, Orientation


def test_runtime_globals():
    runtime = CubeRuntime(Cube((3, 3, 3)), Orientation(), lambda action: None, lambda: None)
    existing = set(runtime.functions.global_values.keys())
    assert existing.issuperset(set(CubeRuntime.COLOR_NAMES.keys()))
    assert existing.issuperset(set(CubeRuntime.SIDE_NAMES.keys()))
    assert "push_orientation" in existing


def test_action_callback():
    callback: Callable[[Action], None] = MagicMock()
    runtime = CubeRuntime(Cube((3, 3, 3)), Orientation(), callback, lambda: None)
    runtime.perform_turn(Side.LEFT, 2, [1])

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


def test_state_stack():
    actions = []
    runtime = CubeRuntime(Cube((2, 2, 2)), Orientation(), actions.append, lambda: None)

    runtime.perform_turn(Side.FRONT, 1, [1])
    runtime.perform_rotate(Side.TOP, False)
    runtime.push_orientation()
    for _ in range(3):
        runtime.perform_turn(Side.FRONT, 1, [1])
        runtime.perform_rotate(Side.TOP, False)
    runtime.pop_orientation()

    assert "FYFYFYFYY" == "".join(map(str, actions))


def test_suspend_rotations():
    actions = []
    runtime = CubeRuntime(Cube((2, 2, 2)), Orientation(), actions.append, lambda: None)
    runtime.perform_turn(Side.FRONT, 1, [1])
    runtime.perform_rotate(Side.TOP, False)
    runtime.suspend_rotations()
    for _ in range(3):
        runtime.perform_turn(Side.FRONT, 1, [1])
        runtime.perform_rotate(Side.TOP, False)
    runtime.resume_rotations()

    assert "FYFRBY'" == "".join(map(str, actions))
