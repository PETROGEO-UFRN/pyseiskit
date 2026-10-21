import numpy as np
import numpy.typing as np_types

from .contracts import TimeToDepthVelocityContract
from .constants import TIME_AXIS, CDP_AXIS

def convertTraceTimeToDepth(
    intervalVelocities: np_types.NDArray,
    intervalTimeSamples: float,
    depths: np_types.NDArray
) -> np_types.NDArray:
    numberSamples = len(intervalVelocities)
    times = np.arange(numberSamples) * intervalTimeSamples

    # *** z(t): depth reached at each two-way time
    depthsAtTimes = np.concatenate([
        [0.0],
        np.cumsum(0.5 * intervalTimeSamples * intervalVelocities[:-1])
    ])

    # *** t(z): inverse of z(t); below the last time, the last velocity continues
    timesAtDepths = np.interp(depths, depthsAtTimes, times)
    isBelowLastTime = depths >= depthsAtTimes[-1]
    timesAtDepths[isBelowLastTime] = (
        times[-1] + 2.0 * (depths[isBelowLastTime] - depthsAtTimes[-1]) / intervalVelocities[-1]
    )

    intervalDepthSamples = depths[1] - depths[0]
    depthIntervalVelocities = 2.0 * intervalDepthSamples / np.diff(timesAtDepths)
    return np.concatenate([depthIntervalVelocities, depthIntervalVelocities[-1:]])

@TimeToDepthVelocityContract
def convertTimeToDepthVelocity(
    intervalVelocityModel: np_types.NDArray,
    intervalTimeSamples: float,
    numberDepthSamples: int,
    intervalDepthSamples: float
) -> np_types.NDArray:
    """
    Converts interval velocities in time into interval velocities in depth,
    as SU `velconv intype=vintt outtype=vintz`.

    \nDepths are integrated from the two-way times; depths below the model's last time
    keep its last velocity.

    Parameters
    ----------
    intervalVelocityModel : np_types.NDArray
        Interval velocities in time [2D: samples x cdps], starting at 0 s.
        RMS velocities must go through convertRmsToIntervalVelocity first.
    intervalTimeSamples : float
        Time step between samples in seconds.
    numberDepthSamples : int
        Number of output depth samples, starting at depth 0.
    intervalDepthSamples : float
        Depth step between output samples, in the velocity length unit (e.g. m).

    Returns
    -------
    np_types.NDArray
        Interval velocities in depth [2D: depth samples x cdps].
    """
    if intervalVelocityModel.ndim != 2:
        raise ValueError("intervalVelocityModel must be a 2D array of shape (samples, cdps).")
    if intervalVelocityModel.shape[TIME_AXIS] < 2 or numberDepthSamples < 2:
        raise ValueError("Time and depth axes must have at least 2 samples.")
    if np.any(intervalVelocityModel <= 0):
        raise ValueError("intervalVelocityModel must have only positive velocities.")

    depths = np.arange(numberDepthSamples) * intervalDepthSamples

    return np.stack(
        [
            convertTraceTimeToDepth(intervalVelocityModel[:, cdpIndex], intervalTimeSamples, depths)
            for cdpIndex in range(intervalVelocityModel.shape[CDP_AXIS])
        ],
        axis=CDP_AXIS
    )
