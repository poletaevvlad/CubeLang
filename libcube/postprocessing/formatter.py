from .base import PostprocessorBase
from ..actions import Action


class FormattingPostprocessor(PostprocessorBase[Action, str]):
    def process(self, value: Action):
        self._return(str(value))
