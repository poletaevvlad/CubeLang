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


@stdlib.function([T, ...], Set(T))
def set_of(*args):
    return set(args)


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
    if index < 0:
        raise ValueError("List index must be zero or a positive integer")
    collection.insert(index, value)


@stdlib.function([List(T)], T)
def remove_first(collection: typing.List):
    """ Removes and returns the first element of a list. """
    if len(collection) == 0:
        raise ValueError("The list is empty. There is notthing to remove")
    return collection.pop(0)


@stdlib.function([List(T)], T)
def remove_last(collection: typing.List):
    """ Removes and returns the last element of a list. """
    if len(collection) == 0:
        raise ValueError("The list is empty. There is notthing to remove")
    return collection.pop()


@stdlib.function([List(T), Integer], T)
def remove_at(collection: typing.List, index: int):
    """ Removes and returns an element of a list at specified location. """
    if index < 0 or index >= len(collection):
        raise ValueError("List index is out of range")
    element = collection[index]
    del collection[index]
    return element


@stdlib.function([Integer, T], List(T))
def new_list(size: int, value):
    """ Creates a new list of length `size` and fills it with `value`s. """
    if size < 0:
        raise ValueError("List size must be a positive integer")
    return [value] * size


@stdlib.function([List(T), T], Integer)
def index_of(array: list, value) -> int:
    """ Returns index of an element in a list if it is present, or -1 otherwise. """
    try:
        return array.index(value)
    except ValueError:
        return -1


@stdlib.function([T, ...], List(T))
def list_of(*args):
    return list(args)
