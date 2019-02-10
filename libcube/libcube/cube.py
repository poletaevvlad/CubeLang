from typing import Tuple, Dict
from .orientation import Side, Color
from .sides import CubeSide


class Cube:
    def __init__(self, shape: Tuple[int, int, int]):
        self.shape: Tuple[int, int, int] = shape
        self.sides: Dict[Side, CubeSide] = {
            Side.FRONT: CubeSide(shape[0], shape[2], Color.RED),
            Side.LEFT: CubeSide(shape[1], shape[2], Color.BLUE),
            Side.BACK: CubeSide(shape[0], shape[2], Color.ORANGE),
            Side.RIGHT: CubeSide(shape[1], shape[2], Color.GREEN),
            Side.TOP: CubeSide(shape[0], shape[1], Color.YELLOW),
            Side.BOTTOM: CubeSide(shape[0], shape[1], Color.WHITE)
        }
