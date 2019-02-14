from libcube.listutils import shift_list


def test_shift_list() -> None:
    lst = [1, 2, 3, 4, 5]
    assert shift_list(lst) == [2, 3, 4, 5, 1]


def test_shift_list_2() -> None:
    lst = [1, 2, 3, 4, 5]
    assert shift_list(lst, 2) == [3, 4, 5, 1, 2]
