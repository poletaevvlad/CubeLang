from .base import PostprocessorBase
from ..actions import Action
from ..parser import get_action_representation


class FormattingPostprocessor(PostprocessorBase[Action, str]):
    def process(self, value: Action):
        self._return(get_action_representation(value))
