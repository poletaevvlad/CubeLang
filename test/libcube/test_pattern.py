from typing import Tuple, List

from libcube.cube import ICubeSide
from libcube.orientation import Color
from libcube.sides import Component
from libcube.pattern import Pattern, PatternGroup


class MockCubeSide(ICubeSide[None]):
    def __init__(self, colors: List[List[Color]]):
        super().__init__()
        self.colors = colors

    @property
    def rows(self) -> int:
        return len(self.colors)

    @property
    def columns(self) -> int:
        return len(self.colors[0])

    def __getitem__(self, item: Tuple[int, int]) -> Component[None]:
        i, j = item
        return Component(self.colors[i][j], None)

    def __setitem__(self, key: Tuple[int, int], value: Component[None]) -> None:
        raise NotImplementedError()


COLORS = [
    [Color.RED, Color.GREEN, Color.BLUE],
    [Color.WHITE, Color.WHITE, Color.ORANGE],
    [Color.ORANGE, Color.YELLOW, Color.YELLOW]
]


def test_pattern_match_correct():
    side = MockCubeSide(COLORS)
    g1 = PatternGroup("A")
    g2 = PatternGroup("B")
    pattern = Pattern([
        [None, Color.GREEN, None],
        [g1, g1, None],
        [None, g2, g2]
    ])
    match = pattern.match(side, {g1: Color.WHITE})
    assert match == {g2: Color.YELLOW}


def test_pattern_match_wrong_color():
    side = MockCubeSide(COLORS)
    g1 = PatternGroup("A")
    pattern = Pattern([
        [None, Color.RED, None],
        [g1, g1, None],
        [None, None, None]
    ])
    assert pattern.match(side, dict()) is None


def test_pattern_match_wrong_known():
    side = MockCubeSide(COLORS)
    g1 = PatternGroup("A")
    g2 = PatternGroup("B")
    pattern = Pattern([
        [None, Color.GREEN, None],
        [g1, Color.WHITE, None],
        [None, g2, g2]
    ])
    assert pattern.match(side, {g1: Color.YELLOW}) is None


def test_pattern_match_wrong_found():
    side = MockCubeSide(COLORS)
    g1 = PatternGroup("A")
    pattern = Pattern([
        [None, None, None],
        [g1, None, None],
        [g1, None, None]
    ])
    assert pattern.match(side, dict()) is None