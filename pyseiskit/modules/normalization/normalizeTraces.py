import numpy.typing as np_types
from typing import Dict

from .contracts import NormalizationContract, NormalizationMethodType, NormalizationStrategyType

from .maxStrategy import applyMaxNormalization
from .rmsStrategy import applyRmsNormalization
from .medianStrategy import applyMedianNormalization
from .balanceMedianStrategy import applyBalanceMedianNormalization

normalizationStrategies: Dict[NormalizationMethodType, NormalizationStrategyType] = {
    'max': applyMaxNormalization,
    'rms': applyRmsNormalization,
    'med': applyMedianNormalization,
    'balmed': applyBalanceMedianNormalization,
}

@NormalizationContract
def normalizeTraces(
    gatherAmplitudes: np_types.NDArray,
    method: NormalizationMethodType = 'max'
) -> np_types.NDArray:
    """
    Normalizes seismic traces individually using the specified built-in strategy.

    Parameters
    ----------
    gatherAmplitudes : np_types.NDArray
        Input data array [2D: samples x traces]
    method : NormalizationMethodType
        The normalization strategy to apply. Options are 'max', 'rms', 'med', 'balmed'.

    Returns
    -------
    np_types.NDArray
        Normalized seismic data array.
    """
    if gatherAmplitudes.ndim != 2:
        raise ValueError("Data must be a 2D array of shape (samples, traces).")

    normalizationStrategy = normalizationStrategies.get(method)
    if normalizationStrategy is None:
        raise ValueError(f"Unknown method '{method}'. Valid options: {list(normalizationStrategies.keys())}")

    return normalizationStrategy(gatherAmplitudes)
