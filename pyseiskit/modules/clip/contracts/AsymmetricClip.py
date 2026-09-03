import numpy.typing as np_types
from typing import Protocol, Tuple

class AsymmetricClipProtocol(Protocol):
    def __call__(
        self,
        gatherAmplitudes: np_types.NDArray,
        lowerLimit: float,
        upperLimit: float
    ) -> np_types.NDArray:
        """
        Clip functions must exactly match these parameter names, order, and types.
        """
        ...

def AsymmetricClipContract(callback: AsymmetricClipProtocol) -> AsymmetricClipProtocol:
    """
    Decorator that forces type checkers to verify the function matches AsymmetricClipProtocol.
    """
    return callback
