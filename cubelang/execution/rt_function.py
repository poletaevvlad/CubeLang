from typing import Callable
from .rt_error import RuntimeError


class RuntimeFunction:
    def __init__(self, name: str, function: Callable):
        self._function = function
        self.name = name

    def __call__(self, *args, **kwargs):
        try:
            return self._function(*args, **kwargs)
        except Exception as e:
            raise RuntimeError.update_error(self.name, e)


def runtime_function(name: str):
    return lambda func: RuntimeFunction(name, func)
