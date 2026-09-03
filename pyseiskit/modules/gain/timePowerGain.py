import numpy as np
import numpy.typing as np_types

from .contracts.TimePowerGainContract import TimePowerGainContract

@TimePowerGainContract
def applyTimePowerGain(
    gatherAmplitudes: np_types.NDArray,
    power: float,
    intervalTimeSamples: float
) -> np_types.NDArray:
    """
    Apply a time-power gain (t^power) to the data.

    Parameters
    ----------
    gatherAmplitudes : np_types.NDArray
        Input data array [2D array]
    power : float
        Exponent applied to time (t^power).
    intervalTimeSamples : float
        Time step between samples in seconds.
    """
    timeVector = np.arange(gatherAmplitudes.shape[0]) * intervalTimeSamples
    
    # SU handles t=0 by setting the factor to 0.0 to prevent domain errors for negative powers
    factor = np.where(timeVector > 0.0, timeVector ** power, 0.0)
    
    # Broadcast time factor across all traces
    # factor has shape (samples,), gatherAmplitudes has shape (samples, traces)
    # We expand dimensions of factor to (samples, 1) to broadcast correctly.
    gainedAmplitudes = gatherAmplitudes * factor[:, np.newaxis]
    
    return gainedAmplitudes
