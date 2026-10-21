from typing import Optional, Tuple
import numpy as np
import numpy.typing as np_types

# *** Piecewise cubic coefficients as SU cwp `cubicspline.c` stores them:
# *** value, 1st, 2nd and 3rd derivatives at each input coordinate
CubicCoefficientsType = Tuple[np_types.NDArray, np_types.NDArray, np_types.NDArray, np_types.NDArray]

def computeTrivialCubicCoefficients(
    inputCoordinates: np_types.NDArray,
    inputValues: np_types.NDArray
) -> Optional[CubicCoefficientsType]:
    """
    Constant (1 input) or linear (2 inputs) coefficients, as every SU cubic method does
    for less than 3 inputs. Returns None when there are enough inputs for a cubic.
    """
    numberInputs = len(inputCoordinates)
    if numberInputs > 2:
        return None

    zeros = np.zeros_like(inputValues)
    if numberInputs == 1:
        return inputValues, zeros, zeros, zeros

    slope = (inputValues[1] - inputValues[0]) / (inputCoordinates[1] - inputCoordinates[0])
    firstDerivatives = np.stack([slope, slope])
    return inputValues, firstDerivatives, zeros, zeros

def computeEndDerivative(
    nearestInterval: float,
    farthestInterval: float,
    nearestSlope: np_types.NDArray,
    farthestSlope: np_types.NDArray
) -> np_types.NDArray:
    """
    Shape-preserving 3-point end derivative of SU `cmonot` and `csplin`.
    """
    intervalsSum = nearestInterval + farthestInterval
    nearestWeight = (nearestInterval + intervalsSum) / intervalsSum
    farthestWeight = -nearestInterval / intervalsSum
    endDerivative = nearestWeight * nearestSlope + farthestWeight * farthestSlope

    # *** a derivative against the nearest slope direction is zeroed
    isAgainstSlope = endDerivative * nearestSlope <= 0.0

    # *** limit the derivative so the end interval doesn't overshoot
    maximumDerivative = 3.0 * nearestSlope
    isOvershooting = (
        (nearestSlope * farthestSlope < 0.0)
        & (np.abs(endDerivative) > np.abs(maximumDerivative))
    )
    endDerivative = np.where(isOvershooting, maximumDerivative, endDerivative)

    return np.where(isAgainstSlope, 0.0, endDerivative)

def computeHigherDerivatives(
    inputCoordinates: np_types.NDArray,
    inputValues: np_types.NDArray,
    firstDerivatives: np_types.NDArray
) -> CubicCoefficientsType:
    """
    2nd and 3rd derivatives of the cubic polynomials that match values and
    1st derivatives at both ends of each interval.
    """
    intervals = np.diff(inputCoordinates).reshape((-1,) + (1,) * (inputValues.ndim - 1))
    slopes = np.diff(inputValues, axis=0) / intervals
    thirdDividedDifferences = firstDerivatives[:-1] + firstDerivatives[1:] - 2.0 * slopes

    secondDerivatives = np.empty_like(inputValues)
    thirdDerivatives = np.empty_like(inputValues)
    secondDerivatives[:-1] = 2.0 * (slopes - firstDerivatives[:-1] - thirdDividedDifferences) / intervals
    thirdDerivatives[:-1] = (thirdDividedDifferences / intervals) * (6.0 / intervals)

    # *** the last coordinate continues the last cubic polynomial
    secondDerivatives[-1] = secondDerivatives[-2] + intervals[-1] * thirdDerivatives[-2]
    thirdDerivatives[-1] = thirdDerivatives[-2]

    return inputValues, firstDerivatives, secondDerivatives, thirdDerivatives

def evaluateCubicCoefficients(
    inputCoordinates: np_types.NDArray,
    cubicCoefficients: CubicCoefficientsType,
    outputCoordinates: np_types.NDArray
) -> np_types.NDArray:
    """
    Evaluates piecewise cubic coefficients, as SU `intcub`.
    \nOutside the input coordinates, the first and last cubic polynomials are extrapolated.
    """
    values, firstDerivatives, secondDerivatives, thirdDerivatives = cubicCoefficients

    intervalIndices = np.clip(
        np.searchsorted(inputCoordinates, outputCoordinates, side='right') - 1,
        0,
        len(inputCoordinates) - 1
    )
    distances = outputCoordinates - inputCoordinates[intervalIndices]
    distances = distances.reshape((-1,) + (1,) * (values.ndim - 1))

    return values[intervalIndices] + distances * (
        firstDerivatives[intervalIndices] + distances * (
            secondDerivatives[intervalIndices] / 2.0 + distances * (
                thirdDerivatives[intervalIndices] / 6.0
            )
        )
    )
