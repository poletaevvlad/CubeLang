from typing import TypeVar, List

T = TypeVar("T")


def shift_list(list: List[T], amount: int = 1) -> List[T]:
    return list[amount:] + list[:amount]
