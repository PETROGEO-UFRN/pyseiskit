from typing import Mapping
import numpy.typing as np_types

from ..contracts.GainStrategyProtocol import GainStrategyProtocol
from ...clip.contracts.AsymmetricClip import AsymmetricClipProtocol

def createAsymmetricClipAdapter(callback: AsymmetricClipProtocol) -> GainStrategyProtocol:
    """
    Wraps the 3-parameter asymmetric clipping function to safely accept 
    a dictionary of parameters from the strategy caller.
    """
    def asymmetricClipAdapter(
        gatherAmplitudes: np_types.NDArray,
        gainValue: Mapping[str, float],
        intervalTimeSamples: float = 0.0
    ) -> np_types.NDArray:
        return callback(
            gatherAmplitudes,
            gainValue["lowerLimit"],
            gainValue["upperLimit"]
        )
    
    return asymmetricClipAdapter
