import numpy.typing as np_types
from typing import Protocol

class ExponentialGainProtocol(Protocol):
    def __call__(
        self,
        gatherAmplitudes: np_types.NDArray,
        coefficient: float,
        intervalTimeSamples: float
    ) -> np_types.NDArray:
        """
        Exponential gain functions must exactly match these parameter names, order, and types.
        """
        ...

def ExponentialGainContract(callback: ExponentialGainProtocol) -> ExponentialGainProtocol:
    """
    Decorator that forces type checkers to verify the function matches ExponentialGainProtocol.
    """
    return callback
