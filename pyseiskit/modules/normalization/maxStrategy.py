import numpy as np
import numpy.typing as np_types
from .contracts import NormalizationStrategyContract
from .constants import SAMPLE_AXIS, ZERO_SCALE, SAFE_SCALE

@NormalizationStrategyContract
def applyMaxNormalization(gatherAmplitudes: np_types.NDArray) -> np_types.NDArray:
    scales = np.max(
        np.abs(gatherAmplitudes),
        axis=SAMPLE_AXIS
    )

    scales[scales == ZERO_SCALE] = SAFE_SCALE
    return gatherAmplitudes / scales
