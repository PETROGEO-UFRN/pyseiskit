import numpy as np
from numpy import typing as np_types
from typing import Tuple, List

MIDPOINT_INDEX_OFFSET = 0.5

def _interpolateLobeCoordinates(
    timeSampleInstants: np_types.NDArray,
    traceAmplitudes: np_types.NDArray,
    traceOffset: float
) -> Tuple[List[float], List[float]]:
    """
    Finds all active amplitudes and calculates the exact zero-crossing interpolation 
    points, returning the sorted boundary coordinates for the filled lobes of a single trace.
    Expects data to be pre-flipped if positive lobes are desired.
    """
    currentAmplitudes = traceAmplitudes[:-1]
    nextAmplitudes = traceAmplitudes[1:]
    currentTime = timeSampleInstants[:-1]
    nextTime = timeSampleInstants[1:]

    # Capture strictly negative values (since we flip the data if filling positive)
    negativeMask = currentAmplitudes <= 0
    negativeIndices = np.where(negativeMask)[0]

    xs_neg = traceOffset + currentAmplitudes[negativeMask]
    ys_neg = currentTime[negativeMask]

    # Capture exact zero crossings
    crossingMask = (
        (currentAmplitudes < 0) & (nextAmplitudes > 0)
    ) | (
        (currentAmplitudes > 0) & (nextAmplitudes < 0)
    )
    crossingIndices = np.where(crossingMask)[0]

    # Linear interpolation to find the exact time at zero
    # Handle potential divide by zero just in case
    diffAmp = nextAmplitudes[crossingMask] - currentAmplitudes[crossingMask]
    safeDiffAmp = np.where(diffAmp == 0, 1e-10, diffAmp)
    
    crossingTimes = (
        currentTime[crossingMask] + (
            nextTime[crossingMask] - currentTime[crossingMask]
        ) * (0 - currentAmplitudes[crossingMask]) / safeDiffAmp
    )

    xs_cross = np.full(len(crossingIndices), traceOffset)
    ys_cross = crossingTimes

    # Combine and sort to preserve the chronological order
    sortOrder = np.argsort(np.concatenate(
        [negativeIndices, crossingIndices + MIDPOINT_INDEX_OFFSET]
    ))

    new_xs = np.concatenate([xs_neg, xs_cross])[sortOrder].tolist()
    new_ys = np.concatenate([ys_neg, ys_cross])[sortOrder].tolist()

    # Add the last point if it is part of the lobe
    if traceAmplitudes[-1] <= 0:
        new_xs.append(float(traceOffset + traceAmplitudes[-1]))
        new_ys.append(float(timeSampleInstants[-1]))
        
    return new_xs, new_ys


def wigglePatchesDataFactory(
    data: np_types.NDArray,
    offsetPosition: np_types.NDArray,
    timeSampleInstants: np_types.NDArray,
    fill_mode: str = "positive"
) -> Tuple[List[List[float]], List[List[float]]]:
    """
    Generates polygon coordinates for rendering filled wiggle lobes.
    
    This function calculates sub-sample exact zero-crossings using linear interpolation 
    to create mathematically smooth filled areas. It is plotting-library agnostic.
    
    Args:
        data: 2D array of rescaled amplitudes (samples x traces).
        offsetPosition: 1D array of horizontal trace locations.
        timeSampleInstants: 1D array of time/depth values for the vertical axis.
        fill_mode: "positive" to fill right-swinging lobes, "negative" for left-swinging.
        
    Returns:
        A dictionary `{"xs": [...], "ys": [...]}` where:
            xs: List of lists containing the X coordinates for each trace's filled polygon.
            ys: List of lists containing the Y coordinates for each trace's filled polygon.
    """
    if fill_mode not in ["positive", "negative"]:
        raise ValueError("fill_mode must be 'positive' or 'negative'")

    # The internal algorithm extracts negative values. 
    # If the user wants to fill positive lobes, we simply flip the polarity of the data.
    working_data = -data if fill_mode == "positive" else data

    xs_patches = []
    ys_patches = []

    for traceOffset, traceAmplitude in zip(offsetPosition, working_data.T):
        lobeAmplitudes, lobeTimes = _interpolateLobeCoordinates(
            timeSampleInstants,
            traceAmplitude,
            traceOffset
        )
    
        # Skip if the trace has no lobes of the requested polarity
        if not lobeAmplitudes:
            xs_patches.append([])
            ys_patches.append([])
            continue

        # Build the single continuous polygon: Lobe path + return path along the baseline
        # Note: We must invert the amplitude back to normal if we flipped it earlier
        if fill_mode == "positive":
            actualAmplitudes = [traceOffset - (amp - traceOffset) for amp in lobeAmplitudes]
        else:
            actualAmplitudes = lobeAmplitudes
            
        polygonOffsetCoordinates = [traceOffset] * len(actualAmplitudes) + actualAmplitudes[::-1]
        polygonTimeCoordinates = lobeTimes + lobeTimes[::-1]

        xs_patches.append(polygonOffsetCoordinates)
        ys_patches.append(polygonTimeCoordinates)

    return {"xs": xs_patches, "ys": ys_patches}
