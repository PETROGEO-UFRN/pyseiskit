import numpy.typing as np_types
from typing import Protocol

class FKDipFilterProtocol(Protocol):
    def __call__(
        self,
        complexFKSpectrum: np_types.NDArray,
        wavenumbers: np_types.NDArray,
        frequencies: np_types.NDArray,
        dipSlopes: list[float],
        amplitudes: list[float]
    ) -> np_types.NDArray:
        """
        FK dip filter functions must exactly match these parameter names, order, and types.
        """
        ...

def FKDipFilterContract(callback: FKDipFilterProtocol) -> FKDipFilterProtocol:
    return callback
