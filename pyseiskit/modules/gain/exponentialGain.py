import numpy as np
import numpy.typing as np_types

from .contracts.ExponentialGainContract import ExponentialGainContract

@ExponentialGainContract
def applyExponentialGain(
    gatherAmplitudes: np_types.NDArray,
    coefficient: float,
    intervalTimeSamples: float
) -> np_types.NDArray:
    """
    Apply an exponential time gain (exp(power * t)) to the data.

    Parameters
    ----------
    gatherAmplitudes : np_types.NDArray
        Input data array [2D array]
    coefficient : float
        Scalar multiplied by time in the exponent.
    intervalTimeSamples : float
        Time step between samples in seconds.
    """
    timeVector = np.arange(gatherAmplitudes.shape[0]) * intervalTimeSamples
    
    factor = np.exp(coefficient * timeVector)
    
    gainedAmplitudes = gatherAmplitudes * factor[:, np.newaxis]
    
    return gainedAmplitudes
