from typing import TypedDict, List
from numpy import typing as np_types

class WiggleCoordinatesType(TypedDict):
    amplitudeCoordinates: List[np_types.NDArray]
    timeCoordinates: List[np_types.NDArray]
