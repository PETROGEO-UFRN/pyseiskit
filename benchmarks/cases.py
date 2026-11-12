"""What is compared: an SU command and the pyseiskit function that should match it."""
from dataclasses import dataclass
from fnmatch import fnmatch
from typing import Callable, Optional, Sequence, Tuple

import numpy as np
from pyseiskit import gain

from . import su


@dataclass(frozen=True)
class Case:
    name: str
    su: Tuple[str, ...]
    # (samples x traces, dt in seconds) -> result; must not modify its input
    pyseiskit: Callable[[np.ndarray, float], np.ndarray]
    rtol: float = 1e-5


# The inputs have delrt=0, where pyseiskit's time gains (t from the first sample) and
# sugain (t from delrt) agree.
CASES = (
    Case("sugain tpow=2", ("sugain", "tpow=2"),
         lambda data, dt: gain.applyTimePowerGain(data, 2.0, dt)),
    Case("sugain epow=0.5", ("sugain", "epow=0.5"),
         lambda data, dt: gain.applyExponentialGain(data, 0.5, dt)),
    Case("sugain gpow=0.5", ("sugain", "gpow=0.5"),
         lambda data, dt: gain.applyAmplitudePowerGain(data, 0.5)),
)

# Read and write only. Plain sugain is a documented no-op ("Required parameters: none").
IO = Case("io", ("sugain",), lambda data, dt: data)


def select(patterns: Optional[Sequence[str]]) -> Tuple[Case, ...]:
    if not patterns:
        return CASES
    chosen = tuple(c for c in CASES if any(fnmatch(c.name, p) for p in patterns))
    if not chosen:
        raise SystemExit(f"no case matches {list(patterns)}; cases: {[c.name for c in CASES]}")
    return chosen


def mismatch(case: Case, src: str, out: str) -> Optional[str]:
    """None when pyseiskit's output matches SU's on `src`, otherwise what went wrong."""
    try:
        su.run(case.su, src, out)
        expected, _ = su.samples(su.read(out))
        actual = case.pyseiskit(*su.samples(su.read(src)))
        np.testing.assert_allclose(actual, expected, rtol=case.rtol,
                                   atol=case.rtol * float(np.abs(expected).max()))
    except AssertionError as error:
        return str(error).strip()
    except Exception as error:   # SU failed, or pyseiskit raised: report it like a mismatch
        return f"{type(error).__name__}: {error}"
    return None
