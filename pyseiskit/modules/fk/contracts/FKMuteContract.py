import numpy.typing as np_types
from typing import Protocol

class FKMuteProtocol(Protocol):
    def __call__(
        self,
        complexFKSpectrum: np_types.NDArray,
        wavenumbers: np_types.NDArray,
        frequencies: np_types.NDArray,
        minWavenumber: float,
        maxWavenumber: float,
        minFrequency: float,
        maxFrequency: float,
        amplitudeMultiplier: float = 0.0
    ) -> np_types.NDArray:
        ...

def FKMuteContract(callback: FKMuteProtocol) -> FKMuteProtocol:
    return callback
