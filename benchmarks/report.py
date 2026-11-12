"""Speedups of pyseiskit over SU, end to end and for the computation alone.

    python -m benchmarks.report su.json pyseiskit.json

SU runs as a separate program, so its computation is estimated as the case's time minus
the `io` time (plain sugain: start, read, write) on the same input. pyseiskit's comes from
its own "compute only" benchmark. Medians; for significance tests use pyperf compare_to.
"""
import argparse

import pyperf


def medians(path):
    return {b.get_name(): b.median() for b in pyperf.BenchmarkSuite.load(path).get_benchmarks()}


def speed(su_s, py_s):
    if su_s is None or py_s is None:
        return "-"
    if su_s <= 0:
        return "below I/O noise"
    ratio = su_s / py_s
    return f"{ratio:.2f}x faster" if ratio >= 1 else f"{1 / ratio:.2f}x slower"


def rows(su, py):
    """One row per benchmark present on both sides: (name, SU total, pyseiskit total,
    end-to-end speed, SU compute estimate, pyseiskit compute, compute speed)."""
    table = []
    for name, su_total in su.items():
        if name not in py:
            continue
        label = name[name.rindex(" [") + 1:]
        io = su.get(f"io {label}")
        su_compute = None if name.startswith("io [") or io is None else su_total - io
        py_compute = py.get(f"{name} compute only")
        table.append((name, su_total, py[name], speed(su_total, py[name]),
                      su_compute, py_compute, speed(su_compute, py_compute)))
    return table


def ms(seconds):
    return "-" if seconds is None else f"{seconds * 1e3:.2f} ms"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Speedups of pyseiskit over SU, end to end and for the computation alone.")
    parser.add_argument("su", help="pyperf JSON from --impl su")
    parser.add_argument("pyseiskit", help="pyperf JSON from --impl pyseiskit")
    args = parser.parse_args(argv)
    header = ("benchmark", "SU", "pyseiskit", "end to end", "SU compute*", "pyseiskit",
              "compute")
    lines = [header] + [(r[0], ms(r[1]), ms(r[2]), r[3], ms(r[4]), ms(r[5]), r[6])
                        for r in rows(medians(args.su), medians(args.pyseiskit))]
    widths = [max(len(line[i]) for line in lines) for i in range(len(header))]
    for line in lines:
        print("  ".join(cell.ljust(width) for cell, width in zip(line, widths)).rstrip())
    print("\n* SU compute = SU time - SU io time on the same input. "
          "Speeds are pyseiskit relative to SU.")


if __name__ == "__main__":
    main()
