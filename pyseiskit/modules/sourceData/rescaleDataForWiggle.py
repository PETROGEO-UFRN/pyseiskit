import numpy as np
from numpy import typing as np_types

def rescaleDataForWiggle(
    data: np_types.NDArray,
    offsetPosition: np_types.NDArray,
    overlap: float = 1.0,
    percentile: float = 100.0
) -> np_types.NDArray:
    """
    Rescales seismic data amplitudes to physical horizontal offsets for wiggle trace plotting.

    Args:
        data: 2D array of amplitudes (samples x traces).
        offsetPosition: 1D array of horizontal trace locations.
        overlap: Controls the maximum horizontal swing. A value of 1.0 (Seismic Unix 'xcur' equivalent)
            means a maximum amplitude peak will swing exactly 1.0 trace spacing, touching the baseline
            of the adjacent trace.
        percentile: Percentile of absolute amplitudes used as the maximum for scaling.
            Values < 100.0 (e.g., 99.0) ignore extreme outlier spikes when determining the
            normalization reference, mirroring the behavior of Seismic Unix's 'perc' parameter.
    """
    # Determine maximum scale reference using the specified percentile
    if percentile < 100.0:
        dataMax = np.percentile(np.abs(data), percentile)
    else:
        dataMax = np.max(np.abs(data))

    if dataMax == 0:
        return data.copy()

    dataNormalized = data / dataMax

    # For a single trace there is no inter-trace spacing to reference,
    # so the normalized data is already the final result.
    if data.shape[1] == 1:
        return dataNormalized

    # Calculate trace spacing robustly (median of non-zero absolute differences)
    abs_diffs = np.abs(np.diff(offsetPosition))
    valid_diffs = abs_diffs[abs_diffs > 0]
    
    if len(valid_diffs) == 0:
        # Fallback if all traces are literally on the exact same physical offset
        minTraceSpacing = 1.0
    else:
        minTraceSpacing = np.min(valid_diffs)
        
    # Scale normalized data so the maximum deflection equals overlap * trace spacing
    dataRescaled = dataNormalized * (minTraceSpacing * overlap)

    return dataRescaled
