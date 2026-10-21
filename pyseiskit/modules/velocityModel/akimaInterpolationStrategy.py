import numpy as np
import numpy.typing as np_types

from .contracts import InterpolationStrategyContract
from .cubicCoefficients import (
    computeTrivialCubicCoefficients,
    computeHigherDerivatives,
    evaluateCubicCoefficients
)

def computeWeightedDerivative(
    leftWeights: np_types.NDArray,
    rightWeights: np_types.NDArray,
    leftSlopes: np_types.NDArray,
    rightSlopes: np_types.NDArray
) -> np_types.NDArray:
    """
    Akima's weighted mean of two slopes, or their plain mean when both weights are zero.
    """
    weightsSum = leftWeights + rightWeights
    hasWeights = weightsSum != 0.0
    safeWeightsSum = np.where(hasWeights, weightsSum, 1.0)

    weightedMean = (leftWeights * leftSlopes + rightWeights * rightSlopes) / safeWeightsSum
    return np.where(hasWeights, weightedMean, 0.5 * (leftSlopes + rightSlopes))

@InterpolationStrategyContract
def interpolateAkima(
    inputCoordinates: np_types.NDArray,
    inputValues: np_types.NDArray,
    outputCoordinates: np_types.NDArray
) -> np_types.NDArray:
    """
    Akima piecewise cubic interpolation, as SU `cakima` used by `unisam` and `unisam2` method=akima.
    \nOutside the input coordinates, the first and last cubic polynomials are extrapolated.
    """
    cubicCoefficients = computeTrivialCubicCoefficients(inputCoordinates, inputValues)
    if cubicCoefficients is not None:
        return evaluateCubicCoefficients(inputCoordinates, cubicCoefficients, outputCoordinates)

    intervals = np.diff(inputCoordinates).reshape((-1,) + (1,) * (inputValues.ndim - 1))
    slopes = np.diff(inputValues, axis=0) / intervals

    # *** weight of each coordinate: how much the slope changes across it
    slopeChanges = np.abs(np.diff(slopes, axis=0))
    weights = np.concatenate([slopeChanges[:1], slopeChanges, slopeChanges[-1:]])

    firstDerivatives = np.empty_like(inputValues)

    # *** end slopes are extrapolated linearly from the two nearest intervals
    firstExtrapolatedSlope = 2.0 * slopes[0] - slopes[1]
    lastExtrapolatedSlope = 2.0 * slopes[-1] - slopes[-2]

    firstDerivatives[0] = computeWeightedDerivative(weights[1], weights[0], firstExtrapolatedSlope, slopes[0])
    firstDerivatives[1:-1] = computeWeightedDerivative(weights[2:], weights[:-2], slopes[:-1], slopes[1:])
    firstDerivatives[-1] = computeWeightedDerivative(weights[-2], weights[-1], lastExtrapolatedSlope, slopes[-1])

    cubicCoefficients = computeHigherDerivatives(inputCoordinates, inputValues, firstDerivatives)
    return evaluateCubicCoefficients(inputCoordinates, cubicCoefficients, outputCoordinates)
