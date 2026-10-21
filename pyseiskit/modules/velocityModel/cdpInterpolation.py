import numpy as np
import numpy.typing as np_types

from .contracts import CdpInterpolationContract, InterpolationMethodType
from .interpolationStrategies import getInterpolationStrategy
from .constants import CDP_AXIS

@CdpInterpolationContract
def interpolateAcrossCdps(
    velocityFunctions: np_types.NDArray,
    pickedCdps: np_types.NDArray,
    cdps: np_types.NDArray,
    method: InterpolationMethodType = 'linear'
) -> np_types.NDArray:
    """
    Interpolates uniformly sampled velocity functions of the picked CDPs into every
    requested CDP, sample by sample, as SU `unisam2 x2=<pickedCdps> f2=<first cdp> d2=<cdp interval>`.

    \nNote: SU `unisam2` applies method1= along the 2nd dimension (CDPs) and method2= along the
    1st one, the opposite of its self-documentation. This function's method matches unisam2 method1=.

    Parameters
    ----------
    velocityFunctions : np_types.NDArray
        Velocity functions of the picked CDPs [2D: samples x picked cdps].
    pickedCdps : np_types.NDArray
        CDP number of each velocity function column. Columns are sorted by CDP before interpolating.
    cdps : np_types.NDArray
        Output CDP numbers.
    method : InterpolationMethodType
        'linear', 'mono', 'akima' or 'spline'. 'linear' repeats the first and last picked
        CDP functions outside the picked CDPs; the cubic methods extrapolate their end polynomials.

    Returns
    -------
    np_types.NDArray
        Velocity model [2D: samples x cdps].
    """
    if velocityFunctions.ndim != 2:
        raise ValueError("velocityFunctions must be a 2D array of shape (samples, picked cdps).")

    pickedCdpsArray = np.asarray(pickedCdps, dtype=float)
    if pickedCdpsArray.shape != (velocityFunctions.shape[CDP_AXIS],):
        raise ValueError("pickedCdps must have one CDP number per velocityFunctions column.")

    cdpOrder = np.argsort(pickedCdpsArray, kind='stable')
    interpolationStrategy = getInterpolationStrategy(method)

    # *** strategies interpolate along the first axis, so CDPs go first
    cdpMajorModel = interpolationStrategy(
        pickedCdpsArray[cdpOrder],
        velocityFunctions[:, cdpOrder].T,
        np.asarray(cdps, dtype=float)
    )
    return cdpMajorModel.T
