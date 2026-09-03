import numpy.typing as np_types

from ..contracts.GainStrategyProtocol import GainStrategyProtocol
from ...gain.contracts.AmplitudePowerGainContract import AmplitudePowerGainProtocol

def createAmplitudePowerGainAdapter(callback: AmplitudePowerGainProtocol) -> GainStrategyProtocol:
    """
    Wraps a 2-parameter amplitude-power gain function to safely accept 
    the 3-parameter strategy caller signature.
    """
    def amplitudePowerGainAdapter(
        gatherAmplitudes: np_types.NDArray,
        gainValue: float,
        intervalTimeSamples: float = 0.0
    ) -> np_types.NDArray:
        return callback(gatherAmplitudes, gainValue)
    
    return amplitudePowerGainAdapter
