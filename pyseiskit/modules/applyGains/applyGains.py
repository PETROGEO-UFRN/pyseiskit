from math import isfinite
from numbers import Real
from typing import Any, Mapping, TypeGuard, get_args
from numpy import typing as np_types

from .gainStrategies import gainStrategies
from .contracts import GainKeyType, GainsDictType

def isValidGainKey(key: str) -> TypeGuard[GainKeyType]:
    return key in get_args(GainKeyType)

def isValidNumber(value: Any) -> bool:
    # *** bool is a subclass of int, but never a meaningful gain value
    if isinstance(value, bool) or not isinstance(value, Real):
        return False
    return isfinite(value)

def isValidGainValue(gainType: GainKeyType, gainValue: Any) -> bool:
    if gainType == "ASYMMETRIC_CLIPPING":
        if not isinstance(gainValue, Mapping):
            return False
        return (
            isValidNumber(gainValue.get("lowerLimit"))
            and isValidNumber(gainValue.get("upperLimit"))
        )

    return isValidNumber(gainValue) and gainValue != 0

def applyGains(
    data: np_types.NDArray,
    gains: GainsDictType,
    intervalTimeSamples: float,
) -> np_types.NDArray:
    """
    Applies the specified gain to the input data.
    \nChecks for gain values, not keys.
    \nIn case of None, 0 or invalid values, the gain will be skipped.
    \nIf gains is not a dictionary, the data is returned unchanged.

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

    # *** gains may come from untyped sources (e.g. UI bridges)
    if not isinstance(gains, Mapping):
        return newData

    for gainType, gainValue in gains.items():
        # *** explicity type check
        # *** gains.items() erased the type hint.
        if not isValidGainKey(gainType):
            continue

        if not isValidGainValue(gainType, gainValue):
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
