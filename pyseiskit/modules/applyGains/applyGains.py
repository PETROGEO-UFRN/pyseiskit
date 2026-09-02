from typing import TypedDict
from numpy import typing as np_types

from .gainStrategies import gainStrategies

class GainType(TypedDict):
    """
    A dictionary defining the supported types of gain that can 
    be applied to seismic data.
    """
    AGC: float
    GAUSSIAN_AGC: float
    PERCENTILE_CLIPPING: float

def applyGains(
    data: np_types.NDArray,
    gains: GainType,
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
    gains: GainType [dict]
        Dictionary containing the gain values.
    intervalTimeSamples: float
        Time step between samples in seconds.

    Returns: np_types.NDArray
        The gained data array.
    """
    newData = data.copy()

    for gainType, gainValue in gains.items():
        newData = gainStrategies[gainType](newData, gainValue, intervalTimeSamples)

    return newData
