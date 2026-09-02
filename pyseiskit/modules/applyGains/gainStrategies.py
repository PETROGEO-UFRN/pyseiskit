from .adapters import createClipAdapter

from ..gain.contracts import GenericGainProtocol
from ..gain import applyAGC, applyGAGC
from ..clip import applyPercentileClip

gainStrategies: dict[str, GenericGainProtocol] = {
    'AGC': applyAGC,
    'GAUSSIAN_AGC': applyGAGC,
    'PERCENTILE_CLIPPING': createClipAdapter(applyPercentileClip)
}
