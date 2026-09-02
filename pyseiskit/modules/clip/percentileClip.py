import numpy as np
from numpy import typing as np_types

from .contracts.PercentileClip import PercentileClipContract

@PercentileClipContract
def applyPercentileClip(
	gatherAmplitudes: np_types.NDArray,
    percentile: float
) -> np_types.NDArray:
    """
    Apply a percentile-based clipping to input data.

    Parameters
    ----------
    gatherAmplitudes : np_types.NDArray
        Input data array.
    percentile : float
        Percentile value for clipping.

    Returns
    -------
    np_types.NDArray
        Clipped data array.
    """
    maxTraceAmplitude = np.percentile(
        np.absolute(gatherAmplitudes),
        percentile
    )
    clippedTraces = np.clip(gatherAmplitudes, a_min=-maxTraceAmplitude, a_max=maxTraceAmplitude)
    return clippedTraces
