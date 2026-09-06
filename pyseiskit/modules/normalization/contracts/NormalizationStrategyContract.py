import numpy.typing as np_types
from typing import Protocol, Callable

class NormalizationStrategyProtocol(Protocol):
    def __call__(self, gatherAmplitudes: np_types.NDArray) -> np_types.NDArray:
        ...

def NormalizationStrategyContract(callback: NormalizationStrategyProtocol) -> NormalizationStrategyProtocol:
    return callback

NormalizationStrategyType = Callable[[np_types.NDArray], np_types.NDArray]
