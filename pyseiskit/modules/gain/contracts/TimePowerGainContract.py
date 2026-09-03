import numpy.typing as np_types
from typing import Protocol

class TimePowerGainProtocol(Protocol):
    def __call__(
        self,
        gatherAmplitudes: np_types.NDArray,
        power: float,
        intervalTimeSamples: float
    ) -> np_types.NDArray:
        """
        Time-Power gain functions must exactly match these parameter names, order, and types.
        """
        ...

def TimePowerGainContract(callback: TimePowerGainProtocol) -> TimePowerGainProtocol:
    """
    Decorator that forces type checkers to verify the function matches TimePowerGainProtocol.
    """
    return callback
