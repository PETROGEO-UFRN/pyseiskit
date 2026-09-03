import numpy as np
from numpy import typing as np_types

from .contracts.AbsoluteClip import AbsoluteClipContract

@AbsoluteClipContract
def applyAbsoluteClip(
    gatherAmplitudes: np_types.NDArray,
    clipValue: float
) -> np_types.NDArray:
    """
    Apply absolute value clipping to input data.

    Parameters
    ----------
    gatherAmplitudes : np_types.NDArray
        Input data array.
    clipValue : float
        Absolute threshold value for clipping.

    Returns
    -------
    np_types.NDArray
        Clipped data array.
    """
    clippedTraces = np.clip(gatherAmplitudes, a_min=-clipValue, a_max=clipValue)
    return clippedTraces
