from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Callable, Optional, Union, Any

TIn = TypeVar("TIn")
TOut = TypeVar("TOut")


class PostprocessorBase(ABC, Generic[TIn, TOut]):
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


def chain(*stages: Union[PostprocessorBase, Callable[[Any], None]]):
    if len(stages) < 2:
        return
    for i in range(1, len(stages)):
        if isinstance(stages[i], PostprocessorBase):
            stages[i - 1].callback = stages[i].process
        else:
            stages[i - 1].callback = stages[i]
            if i != len(stages) - 1:
                raise ValueError("A callable can only be supplied into the "
                                 "chain function if it is the last argument")
