import numpy as np
import numpy.typing as np_types
import scipy.fft
from .constants import FFT_WORKERS

from .contracts.FKInverseContract import FKInverseContract

@FKInverseContract
def applyFKInverse(
    complexFKSpectrum: np_types.NDArray,
    numberSamples: int,
    numberTraces: int
) -> np_types.NDArray:
    """
    Inverse F-K transform to bring a complex F-K spectrum back to a real time-space section.
    """
    paddedSamplesLength = (complexFKSpectrum.shape[0] - 1) * 2

    # Space Inverse FFT
    complexFrequencies = scipy.fft.ifft(complexFKSpectrum, axis=1, workers=FFT_WORKERS)
    
    # Time Inverse FFT
    paddedAmplitudes = scipy.fft.irfft(np.conj(complexFrequencies), n=paddedSamplesLength, axis=0, workers=FFT_WORKERS)

    # Crop back to original dimensions
    gatherAmplitudes = paddedAmplitudes[:numberSamples, :numberTraces]

    # Undo spatial frequency centering trick (negate odd spatial traces)
    gatherAmplitudes[:, 1::2] = -gatherAmplitudes[:, 1::2]

    return gatherAmplitudes
