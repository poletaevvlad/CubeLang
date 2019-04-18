from types import MethodType
import typing
from inspect import getfullargspec


class Type:
    def __init__(self, name: str, default: str):
        self.name = name
        self.default = default

    def is_assignable(self, fr: "Type"):
        return self == fr

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

    def default_value(self) -> str:
        return self.default


Integer = Type("Integer", "0")

Real = Type("Real", "0.0")
Void = Type("Void", "")
Real.is_assignable = MethodType(lambda self, fr: fr in {Integer, Real}, Real)
Color = Type("Color", "white")
Side = Type("Side", "front")
Bool = Type("Bool", "False")


class CollectionType(Type):
    def __init__(self, name: str, item_type: Type, default: str):
        super().__init__(name, default)
        self.item_type = item_type

    def __eq__(self, other):
        return type(self) == type(other) and self.item_type == other.item_type

    def __repr__(self):
        return f"{self.name}({self.item_type!r})"

    def __hash__(self):
        return hash((self.name, hash(self.item_type)))


class List(CollectionType):
    def __init__(self, item_type: Type):
        super().__init__("List", item_type, "list()")


class Set(CollectionType):
    def __init__(self, item_type: Type):
        super().__init__("Set", item_type, "set()")


def type_annotation_to_type(annotation: typing.Any) -> Type:
    if annotation == int:
        return Integer
    elif annotation == float:
        return Real
    elif annotation == bool:
        return Bool
    elif annotation is None:
        return Void
    r = repr(annotation)
    if r.startswith(repr(typing.List)):
        return List(type_annotation_to_type(annotation.__args__[0]))
    elif r.startswith(repr(typing.Set)):
        return Set(type_annotation_to_type(annotation.__args__[0]))
    else:
        raise ValueError(f"Unsupported annotation: {annotation!r}")


class Function(Type):
    def __init__(self, arguments: typing.List[Type], return_type: Type):
        super().__init__("Function", "")
        self.arguments: typing.List[Type] = arguments
        self.return_type: Type = return_type

    def __hash__(self):
        return hash((tuple(self.arguments), self.return_type))

    def __eq__(self, other):
        return (isinstance(other, Function) and self.arguments == other.arguments and
                self.return_type == other.return_type)

    def __repr__(self):
        return f"{self.name}({self.arguments}, {self.return_type})"

    def takes_arguments(self, arguments: typing.List[Type]) -> bool:
        return (len(arguments) == len(self.arguments) and
                all(y.is_assignable(x) for x, y in zip(arguments, self.arguments)))

    @staticmethod
    def from_function(func: typing.Any) -> "Function":
        arg_spec = getfullargspec(func)
        argument_types = (arg_spec.annotations[x] for x in arg_spec.args)
        return_type = type_annotation_to_type(arg_spec.annotations["return"])
        return Function(list(map(type_annotation_to_type, argument_types)), return_type)
