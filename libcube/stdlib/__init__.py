from typing import Dict, Any, List, Callable

from ..compiler.types import Type, Function, Bool
from ..compiler.stack import Stack
from ..execution.rt_function import RuntimeFunction


class Library:
    def __init__(self):
        self.global_values: Dict[str, Type] = dict()
        self.exec_globals: Dict[str, Any] = dict()

    def add_function(self, name: str, function: Callable, arguments: List[Type], return_type: Type):
        if name in self.global_values:
            function = self.global_values[name]
            assert isinstance(function, Function)
            function.prepend_overload(arguments, return_type)
        else:
            self.global_values[name] = Function((arguments, return_type))
            self.exec_globals[name] = function

    def function(self, arguments: List[Type], return_type: Type):
        def wrapper(function):
            if isinstance(function, RuntimeFunction):
                name = function.name
            else:
                name = function.__name__
                function = RuntimeFunction(name, function)
            self.add_function(name, function, arguments, return_type)
            return function
        return wrapper

    def add_value(self, name: str, value_type: Type, value: Any):
        self.global_values[name] = value_type
        self.exec_globals[name] = value

    def initialize_stack(self, stack: Stack):
        for name, value_type in self.global_values.items():
            stack.add_global(name, value_type)


stdlib = Library()
stdlib.add_value("true", Bool, True)
stdlib.add_value("false", Bool, False)


from .collections import *
from .math import *
