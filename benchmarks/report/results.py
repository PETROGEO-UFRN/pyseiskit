"""Load pyperf result files."""
from typing import Dict

import pyperf


def medians(path: str) -> Dict[str, float]:
    """Median seconds of every benchmark in a pyperf JSON file, by benchmark name."""
    return {b.get_name(): b.median() for b in pyperf.BenchmarkSuite.load(path).get_benchmarks()}
