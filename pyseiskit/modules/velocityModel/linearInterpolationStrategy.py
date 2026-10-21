import numpy as np
import numpy.typing as np_types

from .contracts import InterpolationStrategyContract

@InterpolationStrategyContract
def interpolateLinear(
    inputCoordinates: np_types.NDArray,
    inputValues: np_types.NDArray,
    outputCoordinates: np_types.NDArray
) -> np_types.NDArray:
    """
    Linear interpolation, as SU `intlin` used by `unisam` and `unisam2` method=linear.
    \nOutside the input coordinates, the first and last input values are repeated.
    """
    numberInputs = len(inputCoordinates)
    if numberInputs == 1:
        return np.repeat(inputValues[:1], len(outputCoordinates), axis=0)

    lowerIndices = np.clip(
        np.searchsorted(inputCoordinates, outputCoordinates, side='right') - 1,
        0,
        numberInputs - 2
    )
    upperIndices = lowerIndices + 1

    weights = (
        (outputCoordinates - inputCoordinates[lowerIndices])
        / (inputCoordinates[upperIndices] - inputCoordinates[lowerIndices])
    )
    # *** clamp the weights to repeat the edge values outside the input coordinates
    weights = np.clip(weights, 0.0, 1.0)

    # *** broadcast weights over any trailing axis of inputValues
    weights = weights.reshape((-1,) + (1,) * (inputValues.ndim - 1))

    lowerValues = inputValues[lowerIndices]
    upperValues = inputValues[upperIndices]
    return lowerValues + weights * (upperValues - lowerValues)
