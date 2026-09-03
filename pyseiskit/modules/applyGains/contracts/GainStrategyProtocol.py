import numpy.typing as np_types
from typing import Protocol, Any

class GainStrategyProtocol(Protocol):
    """
    Contract defining the expected signature for any gain strategy
    in the applyGains pipeline domain.
    """
    def __call__(
        self,
        data: np_types.NDArray,
        value: Any,
        timeSamples: float = ...,
        /
    ) -> np_types.NDArray:
        ...
