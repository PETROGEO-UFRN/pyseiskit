import numpy as np
import numpy.typing as np_types

from .contracts import InterpolationStrategyContract
from .cubicCoefficients import (
    computeTrivialCubicCoefficients,
    computeEndDerivative,
    computeHigherDerivatives,
    evaluateCubicCoefficients
)

@InterpolationStrategyContract
def interpolateMonotonic(
    inputCoordinates: np_types.NDArray,
    inputValues: np_types.NDArray,
    outputCoordinates: np_types.NDArray
) -> np_types.NDArray:
    """
    Monotonicity-preserving piecewise cubic interpolation (Fritsch-Carlson),
    as SU `cmonot` used by `unisam` and `unisam2` method=mono.
    \nOutside the input coordinates, the first and last cubic polynomials are extrapolated.
    """
    cubicCoefficients = computeTrivialCubicCoefficients(inputCoordinates, inputValues)
    if cubicCoefficients is not None:
        return evaluateCubicCoefficients(inputCoordinates, cubicCoefficients, outputCoordinates)

    intervals = np.diff(inputCoordinates).reshape((-1,) + (1,) * (inputValues.ndim - 1))
    slopes = np.diff(inputValues, axis=0) / intervals

    firstDerivatives = np.empty_like(inputValues)
    firstDerivatives[0] = computeEndDerivative(intervals[0], intervals[1], slopes[0], slopes[1])
    firstDerivatives[-1] = computeEndDerivative(intervals[-1], intervals[-2], slopes[-1], slopes[-2])

    # *** interior derivatives by Butland's weighted harmonic mean of the neighbour slopes
    previousIntervals = intervals[:-1]
    nextIntervals = intervals[1:]
    previousSlopes = slopes[:-1]
    nextSlopes = slopes[1:]

    intervalsSum = previousIntervals + nextIntervals
    previousWeights = (intervalsSum + previousIntervals) / (3.0 * intervalsSum)
    nextWeights = (intervalsSum + nextIntervals) / (3.0 * intervalsSum)

    minimumSlopes = np.minimum(np.abs(previousSlopes), np.abs(nextSlopes))
    maximumSlopes = np.maximum(np.abs(previousSlopes), np.abs(nextSlopes))
    isStrictlyMonotonic = previousSlopes * nextSlopes > 0.0
    safeMaximumSlopes = np.where(isStrictlyMonotonic, maximumSlopes, 1.0)

    harmonicMeanDenominator = (
        previousWeights * previousSlopes / safeMaximumSlopes
        + nextWeights * nextSlopes / safeMaximumSlopes
    )
    safeDenominator = np.where(isStrictlyMonotonic, harmonicMeanDenominator, 1.0)

    # *** a slope sign change (local extremum) gets a flat derivative
    firstDerivatives[1:-1] = np.where(isStrictlyMonotonic, minimumSlopes / safeDenominator, 0.0)

    cubicCoefficients = computeHigherDerivatives(inputCoordinates, inputValues, firstDerivatives)
    return evaluateCubicCoefficients(inputCoordinates, cubicCoefficients, outputCoordinates)
