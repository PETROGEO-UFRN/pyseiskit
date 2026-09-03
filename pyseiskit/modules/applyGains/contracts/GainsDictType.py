from typing import Literal, TypedDict

class AsymmetricClipParams(TypedDict):
    """Parameters for asymmetric clipping"""
    lowerLimit: float
    upperLimit: float

GainKeyType = Literal[
    "AGC", 
    "GAUSSIAN_AGC", 
    "TIME_POWER_GAIN", 
    "EXPONENTIAL_GAIN", 
    "AMPLITUDE_POWER_GAIN", 

    "PERCENTILE_CLIPPING", 
    "ABSOLUTE_CLIPPING", 
    "ASYMMETRIC_CLIPPING"
]

class GainsDictType(TypedDict, total=False):
    """
    A dictionary defining the supported types of gain that can 
    be applied to seismic data. All keys are optional.
    """
    AGC: float
    GAUSSIAN_AGC: float
    TIME_POWER_GAIN: float
    EXPONENTIAL_GAIN: float
    AMPLITUDE_POWER_GAIN: float

    # *** Clipping methods merged with gain domain
    # *** justified by historical usage, besides formal definition
    PERCENTILE_CLIPPING: float
    ABSOLUTE_CLIPPING: float
    ASYMMETRIC_CLIPPING: AsymmetricClipParams
