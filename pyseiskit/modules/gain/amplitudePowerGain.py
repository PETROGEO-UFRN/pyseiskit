import numpy as np
import numpy.typing as np_types

from .contracts.AmplitudePowerGainContract import AmplitudePowerGainContract

@AmplitudePowerGainContract
def applyAmplitudePowerGain(
    gatherAmplitudes: np_types.NDArray,
    power: float
) -> np_types.NDArray:
    """
    Apply an amplitude-power gain (sgn(val) * abs(val)^power) to the data.

    Parameters
    ----------
    gatherAmplitudes : np_types.NDArray
        Input data array [2D array]
    power : float
        Exponent applied to amplitude.
    """
    # Equivalent to SU's val >= 0.0 ? pow(val, gpow) : -pow(-val, gpow)
    return np.sign(gatherAmplitudes) * (np.abs(gatherAmplitudes) ** power)
