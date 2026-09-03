import numpy.typing as np_types
from typing import Protocol

class AbsoluteClipProtocol(Protocol):
    def __call__(
        self,
        gatherAmplitudes: np_types.NDArray,
        clipValue: float,
    ) -> np_types.NDArray:
        """
        Clip functions must exactly match these parameter names, order, and types.
        """
        ...

def AbsoluteClipContract(callback: AbsoluteClipProtocol) -> AbsoluteClipProtocol:
    """
    Decorator that forces type checkers to verify the function matches AbsoluteClipProtocol.
    """
    return callback
