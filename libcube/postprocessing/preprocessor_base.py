from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Callable, Optional

TIn = TypeVar("TIn")
TOut = TypeVar("TOut")


class PreprocessorBase(ABC, Generic[TIn, TOut]):
    def __init__(self):
        self.callback: Optional[Callable[[TOut], None]] = None

    @abstractmethod
    def process(self, value: TIn):
        pass

    def done(self):
        pass

    def _return(self, value: TOut):
        if self.callback is not None:
            self.callback(value)
