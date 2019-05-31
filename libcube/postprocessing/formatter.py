from .preprocessor_base import PreprocessorBase
from ..actions import Action
from ..parser import get_action_representation


class FormattingPreprocessor(PreprocessorBase[Action, str]):
    def process(self, value: Action):
        self._return(get_action_representation(value))
