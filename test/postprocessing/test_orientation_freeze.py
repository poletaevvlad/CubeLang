from typing import List

from cubelang.postprocessing import OrientationFreezePostprocessor
from cubelang.actions import Turn, Rotate, TurningType
from cubelang.orientation import Side


class TestOrientationFreeze:
    def test_normal(self):
        result: List[Turn] = []

        ofp = OrientationFreezePostprocessor()
        ofp.callback = result.append
        ofp.process(Turn(Side.FRONT, 1))
        ofp.process(Rotate(Side.TOP))
        ofp.process(Turn(Side.FRONT, 1))
        ofp.process(Rotate(Side.TOP))
        ofp.process(Turn(Side.FRONT, 1))
        ofp.process(Rotate(Side.TOP))
        ofp.process(Turn(Side.FRONT, 1))
        ofp.process(Rotate(Side.FRONT))
        ofp.process(Turn(Side.TOP, 1))

        actual = list(map(lambda x: (x.type, x.indices[0]), result))
        assert actual == [
            (TurningType.SLICE, 1), (TurningType.VERTICAL, -1), (TurningType.SLICE, -1),
            (TurningType.VERTICAL, 1), (TurningType.SLICE, -1)
        ]
