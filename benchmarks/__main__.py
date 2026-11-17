from .main.cases import CASES, BenchmarkCase
from .main.runCase import runCase

THREAD_GROUPS = [{10}]  # one performance core (0-11 here); 12-15 are slower efficiency cores
REPETITIONS = 10

def validateDatasets(cases: list[BenchmarkCase]) -> None:
    # fail before any run, not halfway through the list
    for case in cases:
        if not case.datasetFilePath.is_file():
            raise FileNotFoundError(f"dataset not found: {case.datasetFilePath}")


def main() -> None:
    validateDatasets(CASES)
    for case in CASES:
        runCase(case, THREAD_GROUPS, REPETITIONS)


if __name__ == "__main__":
    main()
