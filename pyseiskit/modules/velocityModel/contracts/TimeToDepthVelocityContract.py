import numpy.typing as np_types
from typing import Protocol

class TimeToDepthVelocityProtocol(Protocol):
    def __call__(
        self,
        intervalVelocityModel: np_types.NDArray,
        intervalTimeSamples: float,
        numberDepthSamples: int,
        intervalDepthSamples: float
    ) -> np_types.NDArray:
        """
        Time to depth velocity conversion must exactly match these parameter names, order, and types.
        """
        ...

def TimeToDepthVelocityContract(callback: TimeToDepthVelocityProtocol) -> TimeToDepthVelocityProtocol:
    return callback
