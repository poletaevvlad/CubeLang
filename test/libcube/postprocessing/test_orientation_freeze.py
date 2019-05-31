from typing import List

from libcube.postprocessing import OrientationFreezePostprocessor
from libcube.actions import Turn, Rotate, TurningType
from libcube.orientation import Side


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

        actual = list(map(lambda x: (x.type, x.sides[0]), result))
        assert actual == [
            (TurningType.SLICE, 1), (TurningType.VERTICAL, -1), (TurningType.SLICE, -1),
            (TurningType.VERTICAL, 1), (TurningType.SLICE, -1)
        ]
