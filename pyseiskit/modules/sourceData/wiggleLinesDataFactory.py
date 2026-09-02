import numpy as np
from numpy import typing as np_types


def wiggleLinesDataFactory(
    data: np_types.NDArray,
    offsetPosition: np_types.NDArray,
    timeSampleInstants: np_types.NDArray,
):
    tracesAmount = data.shape[1]

    # *** Positioning each trace at its corresponding X-axis offset
    broadcastOffsetPosition = np.broadcast_to(offsetPosition, data.shape)
    dataRepositioned = data + broadcastOffsetPosition

    dataPositioned = dataRepositioned.T.tolist()
    timesPositioned = [timeSampleInstants for _ in range(tracesAmount)]

    return {"xs": dataPositioned, "ys": timesPositioned}
