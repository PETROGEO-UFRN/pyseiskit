import numpy.typing as np_types
from typing import Protocol

class AutomaticGainProtocol(Protocol):
    def __call__(
        self,
        gatherAmplitudes: np_types.NDArray,
        wagc: float,
        intervalTimeSamples: float
    ) -> np_types.NDArray:
        """
        Automatic gain functions must exactly match these parameter names, order, and types.
        """
        ...

def AutomaticGainContract(callback: AutomaticGainProtocol) -> AutomaticGainProtocol:
    """
    Decorator that forces type checkers to verify the function matches AutomaticGainProtocol.
    """
    return callback
