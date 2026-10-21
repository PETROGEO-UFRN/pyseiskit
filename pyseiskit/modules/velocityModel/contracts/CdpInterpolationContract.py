import numpy.typing as np_types
from typing import Protocol

from .InterpolationStrategyContract import InterpolationMethodType

class CdpInterpolationProtocol(Protocol):
    def __call__(
        self,
        velocityFunctions: np_types.NDArray,
        pickedCdps: np_types.NDArray,
        cdps: np_types.NDArray,
        method: InterpolationMethodType = 'linear'
    ) -> np_types.NDArray:
        """
        CDP interpolation must exactly match these parameter names, order, and types.
        """
        ...

def CdpInterpolationContract(callback: CdpInterpolationProtocol) -> CdpInterpolationProtocol:
    return callback
