"""Text table of the speedup rows."""
from typing import Optional, Sequence

from .speedups import Row

HEADER = ("benchmark", "SU", "pyseiskit", "end to end", "SU compute*", "pyseiskit", "compute")
FOOTNOTE = ("* SU compute = SU time - SU io time on the same input. "
            "Speeds are pyseiskit relative to SU.")


def ms(seconds: Optional[float]) -> str:
    return "-" if seconds is None else f"{seconds * 1e3:.2f} ms"


def render(rows: Sequence[Row]) -> str:
    lines = [HEADER] + [(r.name, ms(r.su_total), ms(r.py_total), r.total_speed,
                         ms(r.su_compute), ms(r.py_compute), r.compute_speed) for r in rows]
    widths = [max(len(line[i]) for line in lines) for i in range(len(HEADER))]
    table = ["  ".join(cell.ljust(w) for cell, w in zip(line, widths)).rstrip() for line in lines]
    return "\n".join(table) + "\n\n" + FOOTNOTE
