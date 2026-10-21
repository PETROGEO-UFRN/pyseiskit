import numpy.typing as np_types
from typing import Protocol

from .InterpolationStrategyContract import InterpolationMethodType
from .VelocityPicksType import VelocityPicksType

class VelocityModelBuildingProtocol(Protocol):
    def __call__(
        self,
        velocityPicks: VelocityPicksType,
        cdps: np_types.NDArray,
        numberSamples: int,
        intervalTimeSamples: float,
        timeMethod: InterpolationMethodType = 'linear',
        cdpMethod: InterpolationMethodType = 'linear'
    ) -> np_types.NDArray:
        """
        Velocity model building must exactly match these parameter names, order, and types.
        """
        ...

def VelocityModelBuildingContract(callback: VelocityModelBuildingProtocol) -> VelocityModelBuildingProtocol:
    return callback
