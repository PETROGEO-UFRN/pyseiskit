import numpy.typing as np_types
from typing import Protocol, List

from .InterpolationStrategyContract import InterpolationMethodType

class VelocityFunctionInterpolationProtocol(Protocol):
    def __call__(
        self,
        times: List[float],
        velocities: List[float],
        numberSamples: int,
        intervalTimeSamples: float,
        method: InterpolationMethodType = 'linear'
    ) -> np_types.NDArray:
        """
        Velocity function interpolation must exactly match these parameter names, order, and types.
        """
        ...

def VelocityFunctionInterpolationContract(callback: VelocityFunctionInterpolationProtocol) -> VelocityFunctionInterpolationProtocol:
    return callback
