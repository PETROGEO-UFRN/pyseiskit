import numpy as np
import numpy.typing as np_types
import scipy.ndimage

from .contracts import MovingAverageSmoothingContract

def computeBoxSums(velocityModel: np_types.NDArray, halfTimeSamples: int, halfCdps: int) -> np_types.NDArray:
    # *** mode='constant' with cval=0.0 drops the box positions outside the model from the sum
    timeSums = scipy.ndimage.convolve1d(
        velocityModel,
        np.ones(2 * halfTimeSamples + 1),
        mode='constant',
        cval=0.0,
        axis=0
    )
    return scipy.ndimage.convolve1d(
        timeSums,
        np.ones(2 * halfCdps + 1),
        mode='constant',
        cval=0.0,
        axis=1
    )

@MovingAverageSmoothingContract
def applyMovingAverageSmoothing(
    velocityModel: np_types.NDArray,
    timeWindow: float,
    cdpWindow: float,
    intervalTimeSamples: float,
    intervalCdps: float = 1.0
) -> np_types.NDArray:
    """
    Smooths a velocity model with a 2D moving average (box filter) of
    timeWindow x cdpWindow, centred on each sample.

    \nNear the model edges the box is truncated: only the samples inside the model are
    averaged, so edge velocities are not pulled towards zero.

    \nNo single SU program does it; the SU equivalent is a `suconv` (time) + `sumix` (CDPs)
    box sum divided by the same box sum of an all-ones model.

    Parameters
    ----------
    velocityModel : np_types.NDArray
        Velocity model [2D: samples x cdps].
    timeWindow : float
        Box length in seconds. The equivalent number of samples is rounded, and one
        sample is added when it is even, so the box stays centred.
    cdpWindow : float
        Box length in CDP units. The equivalent number of model columns is rounded, and one
        column is added when it is even, so the box stays centred.
    intervalTimeSamples : float
        Time step between samples in seconds.
    intervalCdps : float
        CDP step between model columns (e.g. the picking interval when smoothing
        only the picked CDPs).

    Returns
    -------
    np_types.NDArray
        Smoothed velocity model [2D: samples x cdps].
    """
    if velocityModel.ndim != 2:
        raise ValueError("velocityModel must be a 2D array of shape (samples, cdps).")

    halfTimeSamples = round(timeWindow / intervalTimeSamples) // 2
    halfCdps = round(cdpWindow / intervalCdps) // 2

    # *** a 1 x 1 box averages each sample with itself
    if halfTimeSamples == 0 and halfCdps == 0:
        return velocityModel.copy()

    velocitySums = computeBoxSums(velocityModel, halfTimeSamples, halfCdps)
    sampleCounts = computeBoxSums(np.ones(velocityModel.shape), halfTimeSamples, halfCdps)

    return velocitySums / sampleCounts
