from typing import Union
import numpy.typing as np_types

from ..contracts.GainStrategyProtocol import GainStrategyProtocol
from ...clip.contracts.PercentileClip import PercentileClipProtocol
from ...clip.contracts.AbsoluteClip import AbsoluteClipProtocol

def createClipAdapter(callback: Union[PercentileClipProtocol, AbsoluteClipProtocol]) -> GainStrategyProtocol:
    """
    Wraps a 2-parameter clipping function to safely accept 
    the 3-parameter strategy caller signature.
    """
    def clipAdapter(
        gatherAmplitudes: np_types.NDArray,
        gainValue: float,
        intervalTimeSamples: float = 0.0
    ) -> np_types.NDArray:
        return callback(gatherAmplitudes, gainValue)
    
    return clipAdapter
