from typing import Dict, List, TypedDict

class VelocityPickType(TypedDict):
    """
    Velocity analysis picks of a single CDP, as written by SU `velan` pick files
    (`tnmo=` and `vnmo=` lines).
    """
    times: List[float]
    velocity: List[float]

# *** Picks of a whole line, keyed by CDP number
VelocityPicksType = Dict[int, VelocityPickType]
