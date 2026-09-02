import numpy.typing as np_types
from typing import Protocol

class PercentileClipProtocol(Protocol):
    def __call__(
        self,
        gatherAmplitudes: np_types.NDArray,
        percentile: float,
    ) -> np_types.NDArray:
        """
        Clip functions must exactly match these parameter names, order, and types.
        """
        ...

def PercentileClipContract(function: PercentileClipProtocol) -> PercentileClipProtocol:
    """
    Decorator that forces type checkers to verify the function matches ClipProtocol.
    """
    return function
