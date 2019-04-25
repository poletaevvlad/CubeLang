from typing import Tuple, List

from libcube.cube import ICubeSide
from libcube.orientation import Color
from libcube.sides import Component
from libcube.pattern import Pattern, PatternGroup


class MockCubeSide(ICubeSide[None]):
    def __init__(self, colors: List[List[Color]]):
        super().__init__()
        self._colors = colors

    @property
    def rows(self) -> int:
        return len(self._colors)

    @property
    def columns(self) -> int:
        return len(self._colors[0])

    def __getitem__(self, item: Tuple[int, int]) -> Component[None]:
        i, j = item
        return Component(self._colors[i][j], None)

    def __setitem__(self, key: Tuple[int, int], value: Component[None]) -> None:
        raise NotImplementedError()


COLORS = [
    [Color.RED, Color.GREEN, Color.BLUE],
    [Color.WHITE, Color.WHITE, Color.ORANGE],
    [Color.ORANGE, Color.YELLOW, Color.YELLOW]
]


def test_pattern_match_correct():
    side = MockCubeSide(COLORS)
    g1 = PatternGroup()
    g2 = PatternGroup()
    pattern = Pattern([
        [None, Color.GREEN, None],
        [g1, g1, None],
        [None, g2, g2]
    ])
    match = pattern.match(side, {g1: Color.WHITE})
    assert match == {g2: Color.YELLOW}


def test_pattern_match_wrong_color():
    side = MockCubeSide(COLORS)
    g1 = PatternGroup()
    pattern = Pattern([
        [None, Color.RED, None],
        [g1, g1, None],
        [None, None, None]
    ])
    assert pattern.match(side, dict()) is None


def test_pattern_match_wrong_known():
    side = MockCubeSide(COLORS)
    g1 = PatternGroup()
    g2 = PatternGroup()
    pattern = Pattern([
        [None, Color.GREEN, None],
        [g1, Color.WHITE, None],
        [None, g2, g2]
    ])
    assert pattern.match(side, {g1: Color.YELLOW}) is None


def test_pattern_match_wrong_found():
    side = MockCubeSide(COLORS)
    g1 = PatternGroup()
    pattern = Pattern([
        [None, None, None],
        [g1, None, None],
        [g1, None, None]
    ])
    assert pattern.match(side, dict()) is None


def test_parsing_valid():
    pattern = "--R/Gxy/xOy/yyy"
    parsed = Pattern.parse(pattern)
    assert parsed.values[0][0] is None
    assert parsed.values[0][1] is None
    assert parsed.values[0][2] == Color.RED

    assert parsed.values[1][0] == Color.GREEN
    assert parsed.values[1][1] != parsed.values[1][2]
    assert parsed.values[2][0] == parsed.values[1][1]
    assert parsed.values[2][2] == parsed.values[1][2]
    assert all(x == parsed.values[1][2] for x in parsed.values[3])

# TODO: Either add test for exceptional control flow or remove parsing
#       if functionality isn't needed
