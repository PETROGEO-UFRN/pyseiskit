import numpy.typing as np_types
from typing import Protocol

class MovingAverageSmoothingProtocol(Protocol):
    def __call__(
        self,
        velocityModel: np_types.NDArray,
        timeWindow: float,
        cdpWindow: float,
        intervalTimeSamples: float,
        intervalCdps: float = 1.0
    ) -> np_types.NDArray:
        """
        Moving average smoothing must exactly match these parameter names, order, and types.
        """
        ...

def MovingAverageSmoothingContract(callback: MovingAverageSmoothingProtocol) -> MovingAverageSmoothingProtocol:
    return callback
