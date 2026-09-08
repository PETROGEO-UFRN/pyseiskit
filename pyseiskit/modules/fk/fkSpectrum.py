import numpy as np
import numpy.typing as np_types
import scipy.fft
from typing import Tuple
from .constants import FFT_WORKERS

from .contracts.FKSpectrumContract import FKSpectrumContract

@FKSpectrumContract
def computeFKSpectrum(
    gatherAmplitudes: np_types.NDArray,
    intervalTimeSamples: float,
    intervalSpaceSamples: float = 1.0
) -> Tuple[np_types.NDArray, np_types.NDArray, np_types.NDArray]:
    numberSamples, numberTraces = gatherAmplitudes.shape

    # Match required padding precisely
    paddedSamplesLength = scipy.fft.next_fast_len(numberSamples, real=True)
    paddedTracesLength = scipy.fft.next_fast_len(numberTraces, real=False)

    # Apply spatial frequency centering trick (negate odd spatial traces) on original data
    centeredAmplitudes = np.copy(gatherAmplitudes)
    centeredAmplitudes[:, 1::2] = -centeredAmplitudes[:, 1::2]

    # Pad to fast FFT lengths
    paddedAmplitudes = np.zeros((paddedSamplesLength, paddedTracesLength), dtype=np.float32)
    paddedAmplitudes[:numberSamples, :numberTraces] = centeredAmplitudes

    # Frequencies and Wavenumbers matching padded lengths
    frequencies = scipy.fft.rfftfreq(paddedSamplesLength, intervalTimeSamples)
    wavenumbers = scipy.fft.fftfreq(paddedTracesLength, d=intervalSpaceSamples)
    wavenumbers = scipy.fft.fftshift(wavenumbers)

    # Time FFT
    timeFrequencySpectrum = np.conj(
        scipy.fft.rfft(paddedAmplitudes, axis=0, workers=FFT_WORKERS)
    )

    # Space FFT
    complexFKSpectrum = scipy.fft.fft(
        timeFrequencySpectrum,
        axis=1,
        workers=FFT_WORKERS
    )

    return wavenumbers, frequencies, complexFKSpectrum
