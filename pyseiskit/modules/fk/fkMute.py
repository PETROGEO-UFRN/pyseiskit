import numpy as np
import numpy.typing as np_types

from .contracts.FKMuteContract import FKMuteContract

@FKMuteContract
def applyFKMute(
    complexFKSpectrum: np_types.NDArray,
    wavenumbers: np_types.NDArray,
    frequencies: np_types.NDArray,
    minWavenumber: float,
    maxWavenumber: float,
    minFrequency: float,
    maxFrequency: float,
    amplitudeMultiplier: float = 0.0
) -> np_types.NDArray:
    """
    Zeroes out or attenuates a strictly rectangular region of the F-K spectrum.
    """
    mutedFKSpectrum = complexFKSpectrum.copy()

    # Ensure bounds are correctly ordered regardless of UI selection drag direction
    lowerWavenumberBound = min(minWavenumber, maxWavenumber)
    upperWavenumberBound = max(minWavenumber, maxWavenumber)
    lowerFrequencyBound = min(minFrequency, maxFrequency)
    upperFrequencyBound = max(minFrequency, maxFrequency)

    wavenumberMask = (wavenumbers >= lowerWavenumberBound) & (wavenumbers <= upperWavenumberBound)
    frequencyMask = (frequencies >= lowerFrequencyBound) & (frequencies <= upperFrequencyBound)

    mutedFKSpectrum[np.ix_(frequencyMask, wavenumberMask)] *= amplitudeMultiplier

    return mutedFKSpectrum
