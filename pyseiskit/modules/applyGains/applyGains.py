from typing import TypeGuard, get_args
from numpy import typing as np_types

from .gainStrategies import gainStrategies
from .contracts import GainKeyType, GainsDictType

def isValidGainKey(key: str) -> TypeGuard[GainKeyType]:
    return key in get_args(GainKeyType)

def applyGains(
    data: np_types.NDArray,
    gains: GainsDictType,
    intervalTimeSamples: float,
) -> np_types.NDArray:
    """
    Applies the specified gain to the input data.
    \nChecks for gain values, not keys.
    \nIn case of None or 0 values, the gain will be skipped.

    Parameters
    ----------
    data: np_types.NDArray
        Input data array [2D array]
    gains: GainsDictType [dict]
        Dictionary containing the gain values.
    intervalTimeSamples: float
        Time step between samples in seconds.

    Returns: np_types.NDArray
        The gained data array.
    """
    newData = data.copy()

    for gainType, gainValue in gains.items():
        # *** explicity type check
        # *** gains.items() erased the type hint.
        if not isValidGainKey(gainType):
            continue

        if gainValue is None:
            continue
            
        applyGainStrategy = gainStrategies.get(gainType)
        if applyGainStrategy is None:
            continue

        newData = applyGainStrategy(
            newData,
            gainValue,
            intervalTimeSamples
        )

    return newData
