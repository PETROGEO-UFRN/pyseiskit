import numpy as np
import numpy.typing as np_types

from .contracts.FKDipFilterContract import FKDipFilterContract

@FKDipFilterContract
def applyFKDipFilter(
    complexFKSpectrum: np_types.NDArray,
    wavenumbers: np_types.NDArray,
    frequencies: np_types.NDArray,
    dipSlopes: list[float],
    amplitudes: list[float]
) -> np_types.NDArray:
    """
    Applies a dip filter in the F-K domain.

    The filter operates on the apparent slowness (slope p = k/f).
    For every point in the F-K spectrum, its slope is calculated.
    The amplitude multiplier is linearly interpolated from the given (dipSlopes, amplitudes) arrays.

    Parameters
    ----------
    complexFKSpectrum : np_types.NDArray
        Complex F-K spectrum [2D: frequencies x wavenumbers].
    wavenumbers : np_types.NDArray
        Wavenumber axis (e.g. cycles/m).
    frequencies : np_types.NDArray
        Frequency axis (Hz).
    dipSlopes : list[float]
        List of slope values (dt/dx). Must be sorted in ascending order.
    amplitudes : list[float]
        List of amplitude multipliers (0.0 to 1.0) corresponding to each slope.

    Returns
    -------
    np_types.NDArray
        Filtered complex F-K spectrum.
    """
    if len(dipSlopes) != len(amplitudes):
        raise ValueError("dipSlopes and amplitudes arrays must have the same length.")

    dipSlopesArray = np.array(dipSlopes, dtype=float)
    amplitudesArray = np.array(amplitudes, dtype=float)

    if not np.all(np.diff(dipSlopesArray) >= 0):
        raise ValueError("dipSlopes array must be monotonically increasing.")

    # To avoid division by zero at f=0, we use a very small epsilon.
    safeFrequencies = np.where(frequencies == 0, 1e-12, frequencies)
    
    # Broadcast 1D coordinate arrays directly into a 2D grid
    apparentSlownessGrid = wavenumbers[None, :] / safeFrequencies[:, None]

    # Interpolate multipliers for the entire 2D grid
    multipliers = np.interp(
        apparentSlownessGrid.ravel(), 
        dipSlopesArray, 
        amplitudesArray
    ).reshape(apparentSlownessGrid.shape)

    return complexFKSpectrum * multipliers
