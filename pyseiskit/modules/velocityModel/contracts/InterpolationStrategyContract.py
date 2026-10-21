import numpy.typing as np_types
from typing import Protocol, Literal, Callable

# *** Same options as SU `unisam` method= and `unisam2` method1=/method2=
InterpolationMethodType = Literal['linear', 'mono', 'akima', 'spline']

class InterpolationStrategyProtocol(Protocol):
    def __call__(
        self,
        inputCoordinates: np_types.NDArray,
        inputValues: np_types.NDArray,
        outputCoordinates: np_types.NDArray
    ) -> np_types.NDArray:
        """
        Interpolation strategies must exactly match these parameter names, order, and types.
        \nInterpolates along the first axis of inputValues.
        """
        ...

def InterpolationStrategyContract(callback: InterpolationStrategyProtocol) -> InterpolationStrategyProtocol:
    return callback

InterpolationStrategyType = Callable[[np_types.NDArray, np_types.NDArray, np_types.NDArray], np_types.NDArray]
