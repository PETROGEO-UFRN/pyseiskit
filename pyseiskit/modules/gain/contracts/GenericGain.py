import numpy.typing as np_types
from typing import Protocol

class GenericGainProtocol(Protocol):
    def __call__(
        self,
        data: np_types.NDArray,
        value: float,
        # *** The '= ...' makes the third parameter optional.
        timeSamples: float = ...,
        # *** '/' means this protocol is positional-only. 
        /
    ) -> np_types.NDArray:
        """
        Functions can name their variables wagc, percentile, threshold, etc., 
        and it will still be valid.
        The third parameter is optional.
        """
        ...
