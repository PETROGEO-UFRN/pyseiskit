import numpy as np
import numpy.typing as np_types

from .contracts import VelocityModelBuildingContract, VelocityPicksType, InterpolationMethodType
from .velocityFunctionInterpolation import interpolateVelocityFunction
from .cdpInterpolation import interpolateAcrossCdps
from .constants import CDP_AXIS

@VelocityModelBuildingContract
def buildVelocityModel(
    velocityPicks: VelocityPicksType,
    cdps: np_types.NDArray,
    numberSamples: int,
    intervalTimeSamples: float,
    timeMethod: InterpolationMethodType = 'linear',
    cdpMethod: InterpolationMethodType = 'linear'
) -> np_types.NDArray:
    """
    Builds a velocity model from velocity analysis picks with the SU strategy:
    `unisam` along time for each picked CDP, then `unisam2` across CDPs.

    \nSmoothing is a separate step, so it can be applied either to the picked CDPs
    (interpolateVelocityFunction + smoothing + interpolateAcrossCdps) or to the whole model.

    Parameters
    ----------
    velocityPicks : VelocityPicksType
        Picks keyed by CDP number. CDPs without picks are skipped.
    cdps : np_types.NDArray
        Output CDP numbers, one model column each.
    numberSamples : int
        Number of time samples, starting at 0 s.
    intervalTimeSamples : float
        Time step between samples in seconds.
    timeMethod : InterpolationMethodType
        Interpolation along time ('linear', 'mono', 'akima' or 'spline').
    cdpMethod : InterpolationMethodType
        Interpolation across CDPs ('linear', 'mono', 'akima' or 'spline').

    Returns
    -------
    np_types.NDArray
        Velocity model [2D: samples x cdps].
    """
    pickedCdps = sorted(
        cdp for cdp, pick in velocityPicks.items()
        if len(pick['times']) > 0
    )
    if not pickedCdps:
        raise ValueError("velocityPicks must have picks for at least one CDP.")

    velocityFunctions = np.stack(
        [
            interpolateVelocityFunction(
                velocityPicks[cdp]['times'],
                velocityPicks[cdp]['velocity'],
                numberSamples,
                intervalTimeSamples,
                timeMethod
            )
            for cdp in pickedCdps
        ],
        axis=CDP_AXIS
    )

    return interpolateAcrossCdps(
        velocityFunctions,
        np.array(pickedCdps),
        cdps,
        cdpMethod
    )
