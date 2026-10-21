import numpy as np
import numpy.typing as np_types

from .contracts import RmsToIntervalVelocityContract
from .constants import TIME_AXIS, DIX_MINIMUM_SQUARED_VELOCITY_RATIO

@RmsToIntervalVelocityContract
def convertRmsToIntervalVelocity(
    rmsVelocityModel: np_types.NDArray,
    intervalTimeSamples: float
) -> np_types.NDArray:
    """
    Converts RMS velocities into interval velocities with the Dix equation,
    as SU `velconv intype=vrmst outtype=vintt`.

    \nThe interval velocity of sample i is the one between samples i and i+1; the last sample
    repeats the previous one. As in velconv, squared interval velocities below 0.00001 of the
    first squared RMS velocity (RMS inversions) are clipped to that floor.

    Parameters
    ----------
    rmsVelocityModel : np_types.NDArray
        RMS velocities in time [2D: samples x cdps, or 1D: samples], starting at 0 s.
    intervalTimeSamples : float
        Time step between samples in seconds.

    Returns
    -------
    np_types.NDArray
        Interval velocities in time, with the same shape as rmsVelocityModel.
    """
    numberSamples = rmsVelocityModel.shape[TIME_AXIS]
    if numberSamples < 2:
        raise ValueError("rmsVelocityModel must have at least 2 time samples.")
    if np.any(rmsVelocityModel <= 0):
        raise ValueError("rmsVelocityModel must have only positive velocities.")

    times = np.arange(numberSamples) * intervalTimeSamples
    times = times.reshape((-1,) + (1,) * (rmsVelocityModel.ndim - 1))

    # *** t·v²: the time integral of the squared interval velocity up to each sample
    squaredVelocityIntegrals = times * np.square(rmsVelocityModel)
    squaredIntervalVelocities = np.diff(squaredVelocityIntegrals, axis=TIME_AXIS) / intervalTimeSamples

    minimumSquaredVelocities = DIX_MINIMUM_SQUARED_VELOCITY_RATIO * np.square(rmsVelocityModel[0])
    intervalVelocities = np.sqrt(np.maximum(squaredIntervalVelocities, minimumSquaredVelocities))

    return np.concatenate([intervalVelocities, intervalVelocities[-1:]], axis=TIME_AXIS)
