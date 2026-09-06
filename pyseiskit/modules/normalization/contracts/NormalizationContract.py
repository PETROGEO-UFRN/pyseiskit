import numpy.typing as np_types
from typing import Protocol, Literal

NormalizationMethodType = Literal['max', 'rms', 'med', 'balmed']

class NormalizationProtocol(Protocol):
    def __call__(
        self,
        gatherAmplitudes: np_types.NDArray,
        method: NormalizationMethodType = 'max'
    ) -> np_types.NDArray:
        ...

def NormalizationContract(callback: NormalizationProtocol) -> NormalizationProtocol:
    return callback
