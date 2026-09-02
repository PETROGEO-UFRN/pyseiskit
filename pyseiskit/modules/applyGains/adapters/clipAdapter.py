from typing import Callable
import numpy.typing as np_types

def createClipAdapter(func: Callable) -> Callable:
    """
    Wraps a 2-parameter clipping function to safely accept 
    the 3-parameter strategy caller signature.
    """
    def clipAdapter(
        gatherAmplitudes: np_types.NDArray,
        gainValue: float,
        intervalTimeSamples: float
    ) -> np_types.NDArray:
        return func(gatherAmplitudes, gainValue)
    
    return clipAdapter
