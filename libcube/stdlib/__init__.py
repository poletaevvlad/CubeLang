from typing import Dict, Any, List

from ..compiler.types import Type, Function


class Library:
    def __init__(self):
        self.global_functions: Dict[str, Function] = dict()
        self.exec_globals: Dict[str, Any] = dict()

    def function(self, arguments: List[Type], return_type: Type):
        def wrapper(function):
            name = function.__name__
            if name in self.global_functions:
                self.global_functions[name].prepend_overload(arguments, return_type)
            else:
                self.global_functions[name] = Function((arguments, return_type))
                self.exec_globals[name] = function
            return function

        return wrapper
