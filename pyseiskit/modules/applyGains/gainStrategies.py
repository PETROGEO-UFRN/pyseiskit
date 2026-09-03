from .adapters import (
    createClipAdapter, 
    createAmplitudePowerGainAdapter, 
    createAsymmetricClipAdapter,
    createGenericGainAdapter
)
from .contracts import GainKeyType, GainStrategyProtocol

from ..gain import applyAGC, applyGAGC, applyTimePowerGain, applyExponentialGain, applyAmplitudePowerGain
from ..clip import applyPercentileClip, applyAbsoluteClip, applyAsymmetricClip

gainStrategies: dict[GainKeyType, GainStrategyProtocol] = {
    'AGC': createGenericGainAdapter(applyAGC),
    'GAUSSIAN_AGC': createGenericGainAdapter(applyGAGC),
    'TIME_POWER_GAIN': createGenericGainAdapter(applyTimePowerGain),
    'EXPONENTIAL_GAIN': createGenericGainAdapter(applyExponentialGain),
    'AMPLITUDE_POWER_GAIN': createAmplitudePowerGainAdapter(applyAmplitudePowerGain),

    # *** Clipping methods merged with gain domain
    # *** justified by historical usage, besides formal definition
    'PERCENTILE_CLIPPING': createClipAdapter(applyPercentileClip),
    'ABSOLUTE_CLIPPING': createClipAdapter(applyAbsoluteClip),
    'ASYMMETRIC_CLIPPING': createAsymmetricClipAdapter(applyAsymmetricClip)
}
