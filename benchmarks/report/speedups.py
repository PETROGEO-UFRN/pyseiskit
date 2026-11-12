"""Speedups of pyseiskit over SU, from benchmark medians (pure).

SU runs as a separate program, so its computation is estimated as the case's time minus
the `io` time (plain sugain: start, read, write) on the same input. pyseiskit's comes from
its own "compute only" benchmark. For significance tests use pyperf compare_to.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Row:
    name: str
    su_total: float
    py_total: float
    total_speed: str
    su_compute: Optional[float]
    py_compute: Optional[float]
    compute_speed: str


def speed(su_s: Optional[float], py_s: Optional[float]) -> str:
    """pyseiskit relative to SU, e.g. '1.50x faster'."""
    if su_s is None or py_s is None:
        return "-"
    if su_s <= 0:
        return "below I/O noise"
    ratio = su_s / py_s
    return f"{ratio:.2f}x faster" if ratio >= 1 else f"{1 / ratio:.2f}x slower"


def rows(su: Dict[str, float], py: Dict[str, float]) -> List[Row]:
    """One row per benchmark present on both sides, in SU's order."""
    table = []
    for name, su_total in su.items():
        if name not in py:
            continue
        label = name[name.rindex(" [") + 1:]
        io = su.get(f"io {label}")
        su_compute = None if name.startswith("io [") or io is None else su_total - io
        py_compute = py.get(f"{name} compute only")
        table.append(Row(name, su_total, py[name], speed(su_total, py[name]),
                         su_compute, py_compute, speed(su_compute, py_compute)))
    return table
