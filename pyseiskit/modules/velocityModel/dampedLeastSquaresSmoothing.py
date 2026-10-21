import numpy as np
import numpy.typing as np_types
import scipy.linalg

from .contracts import DampedLeastSquaresSmoothingContract
from .constants import TIME_AXIS, CDP_AXIS

def solveDampingSystem(
    diagonal: np_types.NDArray,
    damping: float,
    rightHandSide: np_types.NDArray
) -> np_types.NDArray:
    """
    Solves the symmetric tridiagonal system with the given diagonal and -damping
    off the diagonal, for every column of rightHandSide.
    """
    bandedMatrix = np.zeros((3, len(diagonal)))
    bandedMatrix[0, 1:] = -damping
    bandedMatrix[1] = diagonal
    bandedMatrix[2, :-1] = -damping
    return scipy.linalg.solve_banded((1, 1), bandedMatrix, rightHandSide)

@DampedLeastSquaresSmoothingContract
def applyDampedLeastSquaresSmoothing(
    velocityModel: np_types.NDArray,
    timeSmoothing: float,
    cdpSmoothing: float
) -> np_types.NDArray:
    """
    Smooths a velocity model by damped least squares, as SU `smooth2 r1=<timeSmoothing> r2=<cdpSmoothing>`.

    \nFor each direction, solves (I + r²/4 · DᵀD) v_smooth = v, where D is the first difference
    operator: first across CDPs, then along time. As in smooth2, the first time sample is
    kept unchanged.

    Parameters
    ----------
    velocityModel : np_types.NDArray
        Velocity model [2D: samples x cdps].
    timeSmoothing : float
        Smoothing along time (SU smooth2 r1). SU recommends values from 1 to 20; 0 disables it.
    cdpSmoothing : float
        Smoothing across CDPs (SU smooth2 r2). SU recommends values from 1 to 20; 0 disables it.

    Returns
    -------
    np_types.NDArray
        Smoothed velocity model [2D: samples x cdps].
    """
    if velocityModel.ndim != 2:
        raise ValueError("velocityModel must be a 2D array of shape (samples, cdps).")

    timeDamping = timeSmoothing * timeSmoothing * 0.25
    cdpDamping = cdpSmoothing * cdpSmoothing * 0.25
    numberSamples = velocityModel.shape[TIME_AXIS]
    numberCdps = velocityModel.shape[CDP_AXIS]

    smoothedModel = np.array(velocityModel, dtype=float)

    # *** across CDPs: free (zero slope) at both edges
    if numberCdps > 1:
        cdpDiagonal = np.full(numberCdps, 1.0 + 2.0 * cdpDamping)
        cdpDiagonal[[0, -1]] = 1.0 + cdpDamping
        smoothedModel = solveDampingSystem(cdpDiagonal, cdpDamping, smoothedModel.T).T

    # *** along time: the first sample is fixed and the last one is free
    if numberSamples > 1:
        timeDiagonal = np.full(numberSamples - 1, 1.0 + 2.0 * timeDamping)
        timeDiagonal[-1] = 1.0 + timeDamping

        rightHandSide = smoothedModel[1:].copy()
        rightHandSide[0] += timeDamping * smoothedModel[0]
        smoothedModel[1:] = solveDampingSystem(timeDiagonal, timeDamping, rightHandSide)

    return smoothedModel
