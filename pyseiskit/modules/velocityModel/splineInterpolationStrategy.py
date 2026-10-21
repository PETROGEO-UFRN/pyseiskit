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
def interpolateSpline(
    inputCoordinates: np_types.NDArray,
    inputValues: np_types.NDArray,
    outputCoordinates: np_types.NDArray
) -> np_types.NDArray:
    """
    Cubic spline interpolation (continuous 2nd derivatives), as SU `csplin` used by
    `unisam` and `unisam2` method=spline.
    \nEnd derivatives are set by the same shape-preserving 3-point formula of method='mono'.
    \nOutside the input coordinates, the first and last cubic polynomials are extrapolated.
    """
    cubicCoefficients = computeTrivialCubicCoefficients(inputCoordinates, inputValues)
    if cubicCoefficients is not None:
        return evaluateCubicCoefficients(inputCoordinates, cubicCoefficients, outputCoordinates)

    numberInputs = len(inputCoordinates)
    coordinateIntervals = np.diff(inputCoordinates)
    intervals = coordinateIntervals.reshape((-1,) + (1,) * (inputValues.ndim - 1))
    slopes = np.diff(inputValues, axis=0) / intervals

    # *** tridiagonal system for the 1st derivatives: 2 on the diagonal,
    # *** lowerCoefficients below it and (1 - lowerCoefficients) of the previous row above it
    lowerCoefficients = np.empty(numberInputs)
    rightHandSide = np.empty_like(inputValues)

    lowerCoefficients[0] = 1.0
    rightHandSide[0] = 2.0 * computeEndDerivative(intervals[0], intervals[1], slopes[0], slopes[1])

    interiorAlphas = coordinateIntervals[1:] / (coordinateIntervals[:-1] + coordinateIntervals[1:])
    lowerCoefficients[1:-1] = interiorAlphas
    interiorAlphas = interiorAlphas.reshape((-1,) + (1,) * (inputValues.ndim - 1))
    rightHandSide[1:-1] = 3.0 * (interiorAlphas * slopes[:-1] + (1.0 - interiorAlphas) * slopes[1:])

    lowerCoefficients[-1] = 0.0
    rightHandSide[-1] = 2.0 * computeEndDerivative(intervals[-1], intervals[-2], slopes[-1], slopes[-2])

    # *** Thomas algorithm, in the same elimination order as SU csplin
    firstDerivatives = np.empty_like(inputValues)
    eliminationFactors = np.zeros(numberInputs)
    pivot = 2.0
    firstDerivatives[0] = rightHandSide[0] / pivot
    for inputIndex in range(1, numberInputs):
        eliminationFactors[inputIndex] = (1.0 - lowerCoefficients[inputIndex - 1]) / pivot
        pivot = 2.0 - lowerCoefficients[inputIndex] * eliminationFactors[inputIndex]
        firstDerivatives[inputIndex] = (
            rightHandSide[inputIndex] - lowerCoefficients[inputIndex] * firstDerivatives[inputIndex - 1]
        ) / pivot

    for inputIndex in range(numberInputs - 2, -1, -1):
        firstDerivatives[inputIndex] -= eliminationFactors[inputIndex + 1] * firstDerivatives[inputIndex + 1]

    cubicCoefficients = computeHigherDerivatives(inputCoordinates, inputValues, firstDerivatives)
    return evaluateCubicCoefficients(inputCoordinates, cubicCoefficients, outputCoordinates)
