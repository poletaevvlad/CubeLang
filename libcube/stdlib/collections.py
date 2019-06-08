from . import stdlib
from ..compiler.types import Integer, List, Set, T, Void, Bool
import typing

CollectionType = typing.Union[typing.Set, typing.List]


# Set functions

@stdlib.function([Set(T)], Integer)
@stdlib.function([List(T)], Integer)
def size(collection: CollectionType):
    """ Returns number of elements in the collection. """
    return len(collection)


@stdlib.function([Set(T), T], Void)
def add(collection: typing.Set, value) -> None:
    """ Adds a new value to the set. """
    collection.add(value)


@stdlib.function([Set(T), T], Bool)
def remove(collection: typing.Set, value) -> bool:
    """ Removes a value from the set. Returns true if the value were present,
    false otherwise. """
    try:
        collection.remove(value)
        return True
    except KeyError:
        return False


@stdlib.function([Set(T), T], Bool)
@stdlib.function([List(T), T], Bool)
def contains(collection: CollectionType, value) -> bool:
    """ Returns true if the value is present in the collection, false otherwise. """
    return value in collection


@stdlib.function([Set(T), T], Void)
@stdlib.function([List(T), T], Void)
def clear(collection: CollectionType) -> None:
    """ Removes all values from the collection. """
    collection.clear()


# List functions

@stdlib.function([List(T), T], Void)
def add_first(collection: typing.List, value) -> None:
    """ Adds an elements to the begining of a list. It's index will be 0. """
    collection.insert(0, value)


@stdlib.function([List(T), T], Void)
def add_last(collection: typing.List, value) -> None:
    """ Adds an element to the end of a list. It's index will be one less
    than the size of a list. """
    collection.append(value)


@stdlib.function([List(T), Integer, T], Void)
def add_at(collection: typing.List, index: int, value) -> None:
    """ Adds an elements to the list at a specified location. """
    collection.insert(index, value)


@stdlib.function([List(T)], T)
def remove_first(collection: typing.List):
    """ Removes and returns the first element of a list. """
    return collection.pop(0)


@stdlib.function([List(T)], T)
def remove_last(collection: typing.List):
    """ Removes and returns the last element of a list. """
    return collection.pop()


@stdlib.function([List(T), Integer], T)
def remove_at(collection: typing.List, index: int):
    """ Removes and returns an element of a list at specified location. """
    element = collection[index]
    del collection[index]
    return element


@stdlib.function([Integer, T], List(T))
def new_list(size: int, value):
    """ Creates a new list of length `size` and fills it with `value`s. """
    return [value] * size


@stdlib.function([List(T), T], Integer)
def index_of(array: list, value) -> int:
    """ Returns index of an element in a list if it is present, or -1 otherwise. """
    try:
        return array.index(value)
    except ValueError:
        return -1
