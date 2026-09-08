import numpy as np
from numpy import typing as np_types

from .WiggleCoordinatesType import WiggleCoordinatesType

def wigglePatchesDataFactory(
    data: np_types.NDArray,
    offsetPosition: np_types.NDArray,
    timeSampleInstants: np_types.NDArray,
    fillMode: str = "positive"
) -> WiggleCoordinatesType:
    """
    Generates polygon coordinates for rendering filled wiggle lobes.
    
    Uses flat 1D vectorization across the entire seismic dataset simultaneously.
    """
    if fillMode not in ["positive", "negative"]:
        raise ValueError("fillMode must be 'positive' or 'negative'")

    numTraces = data.shape[1]

    if fillMode == "positive":
        workingData = data
    else:
        workingData = -data

    # 1. Prepare 2D time grid
    times2D = np.broadcast_to(timeSampleInstants[:, None], workingData.shape).astype(float)

    currentAmplitudes = workingData[:-1, :]
    nextAmplitudes = workingData[1:, :]
    currentTimes = times2D[:-1, :]
    nextTimes = times2D[1:, :]

    # 2. Extract active points globally
    activeMask = workingData >= 0
    activeRowIndices, activeTraceIndices = np.where(activeMask)
    activeAmplitudesFlat = workingData[activeMask]
    activeTimesFlat = times2D[activeMask]
    activeSortKeys = activeRowIndices.astype(float)

    # 3. Calculate exact zero-crossings globally
    crossingMask = ((currentAmplitudes < 0) & (nextAmplitudes > 0)) | ((currentAmplitudes > 0) & (nextAmplitudes < 0))
    crossingRowIndices, crossingTraceIndices = np.where(crossingMask)

    amplitudeDifferences = nextAmplitudes[crossingMask] - currentAmplitudes[crossingMask]
    safeAmplitudeDifferences = np.where(amplitudeDifferences == 0, 1e-10, amplitudeDifferences)

    crossingTimesFlat = currentTimes[crossingMask] + (nextTimes[crossingMask] - currentTimes[crossingMask]) * (0 - currentAmplitudes[crossingMask]) / safeAmplitudeDifferences
    crossingAmplitudesFlat = np.zeros_like(crossingTimesFlat)
    crossingSortKeys = crossingRowIndices.astype(float) + 0.5

    # 4. Flatten all points
    allTraceIndices = np.concatenate([activeTraceIndices, crossingTraceIndices])
    allSortKeys = np.concatenate([activeSortKeys, crossingSortKeys])
    allAmplitudes = np.concatenate([activeAmplitudesFlat, crossingAmplitudesFlat])
    allTimes = np.concatenate([activeTimesFlat, crossingTimesFlat])

    # 5. Build full closed polygons in a flat 1D space
    numberOfPoints = len(allAmplitudes)
    polygonTraceIndices = np.concatenate([allTraceIndices, allTraceIndices])
    polygonSortKeys = np.concatenate([allSortKeys, -allSortKeys])
    polygonPhase = np.concatenate([np.zeros(numberOfPoints), np.ones(numberOfPoints)])

    # Forward path (baseline) and backward path (wiggles)
    baselineAmplitudes = offsetPosition[allTraceIndices]
    
    if fillMode == "positive":
        backwardAmplitudes = offsetPosition[allTraceIndices] + allAmplitudes
    else:
        backwardAmplitudes = offsetPosition[allTraceIndices] - allAmplitudes

    polygonAmplitudesFlat = np.concatenate([baselineAmplitudes, backwardAmplitudes])
    polygonTimesFlat = np.concatenate([allTimes, allTimes])

    # 6. Global sort to group by trace and properly order the polygon perimeter
    globalPolygonSortOrder = np.lexsort((polygonSortKeys, polygonPhase, polygonTraceIndices))

    sortedPolygonTraceIndices = polygonTraceIndices[globalPolygonSortOrder]
    sortedPolygonAmplitudes = polygonAmplitudesFlat[globalPolygonSortOrder]
    sortedPolygonTimes = polygonTimesFlat[globalPolygonSortOrder]

    # 7. Split into arrays per trace (returns a native Python list of 1D NumPy arrays)
    traceLengths = np.bincount(sortedPolygonTraceIndices, minlength=numTraces)
    splitIndices = np.cumsum(traceLengths)[:-1]

    amplitudeCoordinates = np.split(sortedPolygonAmplitudes, splitIndices)
    timeCoordinates = np.split(sortedPolygonTimes, splitIndices)

    return {
        "amplitudeCoordinates": amplitudeCoordinates,
        "timeCoordinates": timeCoordinates
    }
