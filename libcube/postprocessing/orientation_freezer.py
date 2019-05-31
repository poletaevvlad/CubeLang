from typing import Optional

from ..actions import Action, Turn, Rotate
from .base import PostprocessorBase
from ..orientation import Orientation


class OrientationFreezePostprocessor(PostprocessorBase[Action, Turn]):
    def __init__(self, origin: Optional[Orientation] = None):
        super().__init__()
        if origin is not None:
            self.origin = origin
        else:
            self.origin = Orientation()
        self.current = self.origin

    def process(self, action: Action):
        if isinstance(action, Rotate):
            self.current = action.perform(None, self.current)
        else:
            assert isinstance(action, Turn)
            action = action.from_orientation(self.current, self.origin)
            self._return(action)
