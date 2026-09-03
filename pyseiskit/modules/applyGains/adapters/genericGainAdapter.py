from typing import Union
import numpy.typing as np_types

from ..contracts.GainStrategyProtocol import GainStrategyProtocol
from ...gain.contracts.AutomaticGain import AutomaticGainProtocol
from ...gain.contracts.TimePowerGainContract import TimePowerGainProtocol
from ...gain.contracts.ExponentialGainContract import ExponentialGainProtocol

def createGenericGainAdapter(
    callback: Union[AutomaticGainProtocol, TimePowerGainProtocol, ExponentialGainProtocol]
) -> GainStrategyProtocol:
    """
    Wraps a standard 3-parameter gain function 
    to explicitly satisfy the gain pipeline caller signature.
    """
    def genericGainAdapter(
        gatherAmplitudes: np_types.NDArray,
        gainValue: float,
        intervalTimeSamples: float = 0.0
    ) -> np_types.NDArray:
        return callback(gatherAmplitudes, gainValue, intervalTimeSamples)
    
    return genericGainAdapter
