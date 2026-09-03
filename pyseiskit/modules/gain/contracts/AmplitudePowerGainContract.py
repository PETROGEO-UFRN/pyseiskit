import numpy.typing as np_types
from typing import Protocol

class AmplitudePowerGainProtocol(Protocol):
    def __call__(
        self,
        gatherAmplitudes: np_types.NDArray,
        power: float,
    ) -> np_types.NDArray:
        """
        Amplitude-Power gain functions must exactly match these parameter names, order, and types.
        """
        ...

def AmplitudePowerGainContract(callback: AmplitudePowerGainProtocol) -> AmplitudePowerGainProtocol:
    """
    Decorator that forces type checkers to verify the function matches AmplitudePowerGainProtocol.
    """
    return callback
