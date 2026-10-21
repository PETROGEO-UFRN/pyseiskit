import numpy as np
import numpy.typing as np_types
from typing import List

from .contracts import VelocityFunctionInterpolationContract, InterpolationMethodType
from .interpolationStrategies import getInterpolationStrategy

@VelocityFunctionInterpolationContract
def interpolateVelocityFunction(
    times: List[float],
    velocities: List[float],
    numberSamples: int,
    intervalTimeSamples: float,
    method: InterpolationMethodType = 'linear'
) -> np_types.NDArray:
    """
    Interpolates the velocity picks of a single CDP into a uniformly sampled
    velocity function, as SU `unisam xin=<times> yin=<velocities> nout=<numberSamples> dxout=<intervalTimeSamples>`.

    Parameters
    ----------
    times : List[float]
        Picked times in seconds (SU tnmo). Picks are sorted by time before interpolating.
    velocities : List[float]
        Picked velocities (SU vnmo), one per picked time.
    numberSamples : int
        Number of output time samples, starting at 0 s.
    intervalTimeSamples : float
        Time step between output samples in seconds.
    method : InterpolationMethodType
        'linear', 'mono', 'akima' or 'spline'. 'linear' repeats the first and last picked
        velocities outside the picked times; the cubic methods extrapolate their end polynomials.

    Returns
    -------
    np_types.NDArray
        Velocity function [1D: samples].
    """
    timesArray = np.asarray(times, dtype=float)
    velocitiesArray = np.asarray(velocities, dtype=float)

    if timesArray.ndim != 1 or len(timesArray) == 0 or timesArray.shape != velocitiesArray.shape:
        raise ValueError("times and velocities must be non-empty lists of the same length.")

    timeOrder = np.argsort(timesArray, kind='stable')
    outputTimes = np.arange(numberSamples) * intervalTimeSamples

    interpolationStrategy = getInterpolationStrategy(method)
    return interpolationStrategy(timesArray[timeOrder], velocitiesArray[timeOrder], outputTimes)
