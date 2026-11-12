"""Command line: python -m benchmarks.report.cli su.json pyseiskit.json"""
import argparse

from .results import medians
from .speedups import rows
from .table import render


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        prog="python -m benchmarks.report.cli",
        description="Speedups of pyseiskit over SU, end to end and for the computation alone.")
    parser.add_argument("su", help="pyperf JSON from --impl su")
    parser.add_argument("pyseiskit", help="pyperf JSON from --impl pyseiskit")
    args = parser.parse_args(argv)
    print(render(rows(medians(args.su), medians(args.pyseiskit))))


if __name__ == "__main__":
    main()
