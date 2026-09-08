import numpy as np
from numpy import typing as np_types
from typing import List, Dict, Any
from .WiggleCoordinatesType import WiggleCoordinatesType

def wiggleLinesDataFactory(
    data: np_types.NDArray,
    offsetPosition: np_types.NDArray,
    timeSampleInstants: np_types.NDArray,
) -> WiggleCoordinatesType:
    # *** Positioning each trace at its corresponding amplitude offset
    broadcastOffsetPosition = np.broadcast_to(offsetPosition, data.shape)
    dataRepositioned = data + broadcastOffsetPosition
    
    # Broadcast times to match the 2D shape of traces
    broadcastTimes = np.broadcast_to(timeSampleInstants[:, None], data.shape)

    # list() natively unpacks the first dimension (traces) into a list of 1D arrays
    amplitudeCoordinates = list(dataRepositioned.T)
    timeCoordinates = list(broadcastTimes.T)

    return {"amplitudeCoordinates": amplitudeCoordinates, "timeCoordinates": timeCoordinates}
