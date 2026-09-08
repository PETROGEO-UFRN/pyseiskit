import numpy as np
import numpy.typing as np_types
from typing import List

from .contracts.FKTaperedMuteContract import FKTaperedMuteContract

@FKTaperedMuteContract
def applyFKTaperedMute(
    complexFKSpectrum: np_types.NDArray,
    wavenumbers: np_types.NDArray,
    frequencies: np_types.NDArray,
    wavenumberNodes: List[float],
    frequencyNodes: List[float],
    wavenumberAmplitudes: List[float],
    frequencyAmplitudes: List[float]
) -> np_types.NDArray:
    """
    Applies a separable 2D tapered mute using completely independent amplitude envelopes.
    """
    wavenumberNodesArray = np.array(wavenumberNodes, dtype=float)
    wavenumberAmplitudesArray = np.array(wavenumberAmplitudes, dtype=float)
    frequencyNodesArray = np.array(frequencyNodes, dtype=float)
    frequencyAmplitudesArray = np.array(frequencyAmplitudes, dtype=float)

    if not np.all(np.diff(wavenumberNodesArray) >= 0):
        raise ValueError("wavenumberNodes must be sorted in ascending order.")
    if not np.all(np.diff(frequencyNodesArray) >= 0):
        raise ValueError("frequencyNodes must be sorted in ascending order.")

    wavenumberMultiplier = np.interp(wavenumbers, wavenumberNodesArray, wavenumberAmplitudesArray, left=1.0, right=1.0)
    frequencyMultiplier = np.interp(frequencies, frequencyNodesArray, frequencyAmplitudesArray, left=1.0, right=1.0)

    # To isolate the rectangle (avoiding a cross-shaped mute) while 
    # perfectly preserving the user's explicit amplitude gradients inside 
    # the box, we use the maximum of the two multipliers.
    # Outside the box, max(1.0, X) = 1.0 (preserves data).
    # Inside the box, the amplitude is exactly the maximum of the two requested tapers.
    taperEnvelope = np.maximum(
        frequencyMultiplier[:, None],
        wavenumberMultiplier[None, :]
    )

    return complexFKSpectrum * taperEnvelope
