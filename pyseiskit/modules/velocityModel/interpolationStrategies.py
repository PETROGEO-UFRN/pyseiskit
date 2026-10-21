from typing import Dict

from .contracts import InterpolationMethodType, InterpolationStrategyType

from .linearInterpolationStrategy import interpolateLinear
from .monotonicInterpolationStrategy import interpolateMonotonic
from .akimaInterpolationStrategy import interpolateAkima
from .splineInterpolationStrategy import interpolateSpline

interpolationStrategies: Dict[InterpolationMethodType, InterpolationStrategyType] = {
    'linear': interpolateLinear,
    'mono': interpolateMonotonic,
    'akima': interpolateAkima,
    'spline': interpolateSpline,
}

def getInterpolationStrategy(method: InterpolationMethodType) -> InterpolationStrategyType:
    interpolationStrategy = interpolationStrategies.get(method)
    if interpolationStrategy is None:
        raise ValueError(f"Unknown method '{method}'. Valid options: {list(interpolationStrategies.keys())}")
    return interpolationStrategy
