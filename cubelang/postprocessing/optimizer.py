from typing import Deque
from collections import deque

from ..actions import Action, Rotate, Turn
from .base import PostprocessorBase


class OptimizingPostprocessor(PostprocessorBase[Action, Action]):
    def __init__(self):
        super().__init__()
        self.stack: Deque[Action] = deque()

    def process(self, action: Action):
        if len(self.stack) == 0 or type(self.stack[-1]) != type(action):
            self.stack.append(action)
            return
        on_top = self.stack[-1]
        if isinstance(action, Rotate):
            on_top: Rotate = on_top
            turns = 2 if on_top.twice else 1
            if on_top.axis_side == action.axis_side:
                turns += 2 if action.twice else 1
            elif on_top.axis_side == action.axis_side.opposite():
                turns -= 2 if action.twice else 1
            else:
                self.stack.append(action)
                return

            self.stack.pop()
            turns = (4 + turns) % 4
            if turns != 0:
                if turns == 3:
                    self.stack.append(Rotate(on_top.axis_side.opposite(), False))
                else:
                    self.stack.append(Rotate(on_top.axis_side, turns == 2))
        elif isinstance(action, Turn):
            on_top: Turn = on_top
            if on_top.type != action.type or on_top.indices != action.indices:
                self.stack.append(action)
                return
            self.stack.pop()
            turns = (action.turns + on_top.turns) % 4
            if turns != 0:
                self.stack.append(Turn(action.type, action.indices, turns))
        else:
            self.stack.append(action)

    def done(self):
        for item in self.stack:
            self._return(item)
        super(OptimizingPostprocessor, self).done()
