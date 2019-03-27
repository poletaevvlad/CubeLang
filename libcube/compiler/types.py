from types import MethodType
import typing

class Type:
    def __init__(self, name: str):
        self.name = name

    def is_assignable(self, fr: "Type"):
        return self == fr

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name


Integer = Type("Integer")

Real = Type("Real")
Void = Type("Void")
Real.is_assignable = MethodType(lambda self, fr: fr in {Integer, Real}, Real)

Bool = Type("Bool")


class CollectionType(Type):
    def __init__(self, name: str, item_type: Type):
        super().__init__(name)
        self.item_type = item_type

    def __eq__(self, other):
        return type(self) == type(other) and self.item_type == other.item_type

    def __repr__(self):
        return f"{self.name}({self.item_type!r})"

    def __hash__(self):
        return hash((self.name, hash(self.item_type)))


class List(CollectionType):
    def __init__(self, item_type: Type):
        super().__init__("List", item_type)


class Set(CollectionType):
    def __init__(self, item_type: Type):
        super().__init__("Set", item_type)


class Function(Type):
    def __init__(self, arguments: typing.List[Type], return_type: Type):
        super().__init__("Function")
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
