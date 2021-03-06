from cubelang.postprocessing.base import PostprocessorBase
from cubelang.postprocessing import chain
from unittest.mock import MagicMock
import pytest


class MockPostprocessor(PostprocessorBase[str, str]):
    def process(self, value: str):
        pass


class TestChaining:
    def test_normal(self):
        p1 = MockPostprocessor()
        p2 = MockPostprocessor()
        p3 = MockPostprocessor()
        chain(p1, p2, p3)

        assert p1.callback == p2.process
        assert p1.done_callback == p2.done
        assert p2.callback == p3.process
        assert p2.done_callback == p3.done
        assert p3.callback is None
        assert p3.done_callback is None

    def test_function(self):
        p1 = MockPostprocessor()
        mock = MagicMock()
        chain(p1, mock)

        assert p1.callback == mock
        assert p1.done_callback is None

    def test_function_not_last(self):
        p1 = MockPostprocessor()
        mock = MagicMock()
        p2 = MockPostprocessor()
        with pytest.raises(ValueError):
            chain(p1, mock, p2)

    def test_single(self):
        p1 = MockPostprocessor()
        chain(p1)
        assert p1.callback is None
        assert p1.done_callback is None
