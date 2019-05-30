from . import stdlib
from ..compiler.types import Real, Integer, List, Set, Bool
import math


stdlib.add_function("round", round, [Real], Integer)
stdlib.add_function("floor", math.floor, [Real], Integer)
stdlib.add_function("ceil", math.ceil, [Real], Integer)

stdlib.add_function("sqrt", math.sqrt, [Real], Real)
stdlib.add_function("pow", math.pow, [Real, Real], Real)
stdlib.add_function("pow", math.pow, [Integer, Integer], Integer)

stdlib.add_function("max", max, [Real, Real], Real)
stdlib.add_function("max", max, [Integer, Integer], Integer)
stdlib.add_function("max", max, [List(Real)], Real)
stdlib.add_function("max", max, [List(Integer)], Integer)
stdlib.add_function("max", max, [Set(Real)], Real)
stdlib.add_function("max", max, [Set(Integer)], Integer)

stdlib.add_function("min", min, [Real, Real], Real)
stdlib.add_function("min", min, [Integer, Integer], Integer)
stdlib.add_function("min", min, [List(Real)], Real)
stdlib.add_function("min", min, [List(Integer)], Integer)
stdlib.add_function("min", min, [Set(Real)], Real)
stdlib.add_function("min", min, [Set(Integer)], Integer)


@stdlib.function([Real], Integer)
def sign(x: float) -> int:
    if x > 1e-7:
        return 1
    elif x < -1e-7:
        return -1
    else:
        return 0

stdlib.add_function("not", lambda x: not x, [Bool], Bool)
