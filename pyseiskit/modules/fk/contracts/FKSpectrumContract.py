import numpy.typing as np_types
from typing import Protocol, Tuple

class FKSpectrumProtocol(Protocol):
    def __call__(
        self,
        gatherAmplitudes: np_types.NDArray,
        intervalTimeSamples: float,
        intervalSpaceSamples: float
    ) -> Tuple[np_types.NDArray, np_types.NDArray, np_types.NDArray]:
        """
        FK spectrum functions must exactly match these parameter names, order, and types.
        """
        ...

def FKSpectrumContract(callback: FKSpectrumProtocol) -> FKSpectrumProtocol:
    return callback
