import numpy.typing as np_types
from typing import Protocol

class DampedLeastSquaresSmoothingProtocol(Protocol):
    def __call__(
        self,
        velocityModel: np_types.NDArray,
        timeSmoothing: float,
        cdpSmoothing: float
    ) -> np_types.NDArray:
        """
        Damped least squares smoothing must exactly match these parameter names, order, and types.
        """
        ...

def DampedLeastSquaresSmoothingContract(callback: DampedLeastSquaresSmoothingProtocol) -> DampedLeastSquaresSmoothingProtocol:
    return callback
