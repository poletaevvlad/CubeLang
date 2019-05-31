from typing import Iterable, Deque
from collections import deque
from ..actions import Action, Rotate, Turn


def optimizer_postprocessor(actions: Iterable[Action]) -> Iterable[Action]:
    stack: Deque[Action] = deque()
    for action in actions:
        if len(stack) == 0 or type(stack[-1]) != type(action):
            stack.append(action)
            continue
        on_top = stack[-1]
        if isinstance(action, Rotate):
            on_top: Rotate = on_top
            turns = 2 if on_top.twice else 1
            if on_top.axis_side == action.axis_side:
                turns += 2 if action.twice else 1
            elif on_top.axis_side == action.axis_side.opposite():
                turns -= 2 if action.twice else 1
            else:
                stack.append(action)
                continue

            stack.pop()
            turns = (4 + turns) % 4
            if turns != 0:
                if turns == 3:
                    stack.append(Rotate(on_top.axis_side.opposite(), False))
                else:
                    stack.append(Rotate(on_top.axis_side, turns == 2))
        elif isinstance(action, Turn):
            stack.append(action)
        else:
            stack.append(action)

    return stack
