from types import MethodType
import typing


class Type:
    def __init__(self, name: str, default: str):
        self.name = name
        self.default = default

    def is_assignable(self, fr: "Type") -> bool:
        return self.get_generic_vars(fr) is not None

    def get_generic_vars(self, fr: "Type") -> typing.Optional[typing.Dict[str, "Type"]]:
        return {} if self == fr else None

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

    def default_value(self) -> str:
        return self.default

    def substitute_generic(self, _generic_arguments: typing.Dict[str, "Type"]) -> "Type":
        return self


class GenericTypeVar(Type):
    def __init__(self, name: str):
        super().__init__(name, "")

    def get_generic_vars(self, fr: Type):
        return {self.name: fr}

    def substitute_generic(self, generic_arguments: typing.Dict[str, "Type"]):
        return generic_arguments[self.name]


T = GenericTypeVar("T")

Integer = Type("Integer", "0")

Real = Type("Real", "0.0")
Void = Type("Void", "")
Real.is_assignable = MethodType(lambda self, fr: fr in {Integer, Real}, Real)
Color = Type("Color", "white")
Side = Type("Side", "front")
Bool = Type("Bool", "False")


class CollectionType(Type):
    def __init__(self, name: str, item_type: typing.Union[Type, GenericTypeVar], default: str):
        super().__init__(name, default)
        self.item_type = item_type

    def __eq__(self, other):
        return type(self) == type(other) and self.item_type == other.item_type

    def __repr__(self):
        return f"{self.name}({self.item_type!r})"

    def __hash__(self):
        return hash((self.name, hash(self.item_type)))

    def get_generic_vars(self, fr: "Type"):
        if type(self) != type(fr):
            return None
        fr: CollectionType
        return self.item_type.get_generic_vars(fr.item_type)


class List(CollectionType):
    def __init__(self, item_type: Type):
        super().__init__("List", item_type, "list()")

    def substitute_generic(self, generic_arguments: typing.Dict[str, "Type"]):
        return List(self.item_type.substitute_generic(generic_arguments))


class Set(CollectionType):
    def __init__(self, item_type: Type):
        super().__init__("Set", item_type, "set()")

    def substitute_generic(self, generic_arguments: typing.Dict[str, "Type"]):
        return Set(self.item_type.substitute_generic(generic_arguments))


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
    class FunctionOverload(typing.NamedTuple):
        arguments: typing.List[Type]
        return_type: Type

    def __init__(self, *overloads: typing.Tuple[typing.List[Type], Type]):
        super().__init__("Function", "")
        self.overloads = [Function.FunctionOverload(*x) for x in overloads]

    def __hash__(self):
        return hash(tuple((tuple(x.arguments), x.return_type) for x in self.overloads))

    def __eq__(self, other):
        return isinstance(other, Function) and self.overloads == other.overloads

    def __repr__(self):
        args = ", ".join(f"({x.arguments}, {x.return_type})" for x in self.overloads)
        return f"{self.name}({args})"

    def takes_arguments(self, arguments: typing.List[Type]) -> typing.Optional[Type]:
        for overload in self.overloads:
            if len(arguments) != len(overload.arguments):
                continue
            generic_arguments = {}
            for func_arg, real_arg in zip(overload.arguments, arguments):
                if func_arg == Real and real_arg == Integer:
                    continue
                else:
                    generics = func_arg.get_generic_vars(real_arg)
                    if generics is None:
                        break
                    elif any(argument in generic_arguments and generics[argument] != generic_arguments[argument]
                             for argument in generics):
                        break
                    generic_arguments.update(generics)
            else:
                return overload.return_type.substitute_generic(generic_arguments)
        return None
