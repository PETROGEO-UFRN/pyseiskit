import numpy as np
from numpy import typing as np_types

from .contracts.AsymmetricClip import AsymmetricClipContract

@AsymmetricClipContract
def applyAsymmetricClip(
    gatherAmplitudes: np_types.NDArray,
    lowerLimit: float,
    upperLimit: float
) -> np_types.NDArray:
    """
    Apply an asymmetric clipping to input data based on a minimum and maximum threshold.

    Parameters
    ----------
    gatherAmplitudes : np_types.NDArray
        Input data array.
    lowerLimit : float
        Minimum threshold for clipping.
    upperLimit : float
        Maximum threshold for clipping.

    Returns
    -------
    np_types.NDArray
        Clipped data array.
    """
    clippedTraces = np.clip(gatherAmplitudes, a_min=lowerLimit, a_max=upperLimit)
    return clippedTraces
