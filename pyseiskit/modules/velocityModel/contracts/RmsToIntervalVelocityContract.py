import numpy.typing as np_types
from typing import Protocol

class RmsToIntervalVelocityProtocol(Protocol):
    def __call__(
        self,
        rmsVelocityModel: np_types.NDArray,
        intervalTimeSamples: float
    ) -> np_types.NDArray:
        """
        RMS to interval velocity conversion must exactly match these parameter names, order, and types.
        """
        ...

def RmsToIntervalVelocityContract(callback: RmsToIntervalVelocityProtocol) -> RmsToIntervalVelocityProtocol:
    return callback
