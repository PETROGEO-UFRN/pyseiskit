import numpy as np
import numpy.typing as np_types
from .contracts import NormalizationStrategyContract
from .constants import SAMPLE_AXIS, ZERO_SCALE, SAFE_SCALE

@NormalizationStrategyContract
def applyRmsNormalization(gatherAmplitudes: np_types.NDArray) -> np_types.NDArray:
    meanSquaredAmplitudes = np.mean(
        np.square(gatherAmplitudes),
        axis=SAMPLE_AXIS
    )

    scales = np.sqrt(meanSquaredAmplitudes)
    scales[scales == ZERO_SCALE] = SAFE_SCALE

    return gatherAmplitudes / scales
