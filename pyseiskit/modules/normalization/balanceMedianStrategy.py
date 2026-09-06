import numpy as np
import numpy.typing as np_types
from .contracts import NormalizationStrategyContract
from .constants import SAMPLE_AXIS

@NormalizationStrategyContract
def applyBalanceMedianNormalization(gatherAmplitudes: np_types.NDArray) -> np_types.NDArray:
    shifts = np.median(
        gatherAmplitudes,
        axis=SAMPLE_AXIS
    )

    return gatherAmplitudes - shifts
