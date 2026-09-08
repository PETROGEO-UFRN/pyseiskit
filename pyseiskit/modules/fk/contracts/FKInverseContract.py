import numpy.typing as np_types
from typing import Protocol

class FKInverseProtocol(Protocol):
    def __call__(
        self,
        complexFKSpectrum: np_types.NDArray,
        numberSamples: int,
        numberTraces: int
    ) -> np_types.NDArray:
        ...

def FKInverseContract(callback: FKInverseProtocol) -> FKInverseProtocol:
    return callback
