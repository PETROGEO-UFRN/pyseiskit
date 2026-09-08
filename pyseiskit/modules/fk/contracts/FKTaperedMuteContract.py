import numpy.typing as np_types
from typing import Protocol, List

class FKTaperedMuteProtocol(Protocol):
    def __call__(
        self,
        complexFKSpectrum: np_types.NDArray,
        wavenumbers: np_types.NDArray,
        frequencies: np_types.NDArray,
        wavenumberNodes: List[float],
        frequencyNodes: List[float],
        wavenumberAmplitudes: List[float],
        frequencyAmplitudes: List[float]
    ) -> np_types.NDArray:
        ...

def FKTaperedMuteContract(callback: FKTaperedMuteProtocol) -> FKTaperedMuteProtocol:
    return callback
