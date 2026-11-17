import os

import numpy as np

from ..consts.SCALE_CONVERSION import BYTES_TO_MEBIBYTES, SECONDS_TO_MILLISECONDS
from ..engines.CPUEngine import ThreadGroupType, runCaseOnThreadGroups
from ..engines.pyseiskitEngine import runPyseiskitEngine
from ..engines.SUEngine import runSUEngine
from ..perf.PerformanceTelemetry import PerformanceTelemetry
from .cases import BenchmarkCase

def __printSummary(name: str, telemetry: PerformanceTelemetry) -> None:
    records = telemetry.records
    wallMilliseconds = np.median(records["wallSeconds"]) * SECONDS_TO_MILLISECONDS
    cpuMilliseconds = np.median(records["cpuSeconds"]) * SECONDS_TO_MILLISECONDS
    peakMemoryIncreaseMebibytes = np.max(records["peakMemoryIncreaseBytes"]) * BYTES_TO_MEBIBYTES
    print(
        f"  {name}: {len(records)} runs, median wall {wallMilliseconds:.2f} ms, "
        f"median CPU {cpuMilliseconds:.2f} ms, peak memory increase {peakMemoryIncreaseMebibytes:.1f} MiB"
    )


def runCase(case: BenchmarkCase, threadGroups: list[ThreadGroupType], repetitions: int) -> None:
    suPipe = case.suWorkflow()
    datasetFilePath = str(case.datasetFilePath)

    # SU's output goes to /dev/null: a written file's cache would count as SU's memory
    suTelemetry = PerformanceTelemetry(repetitions)
    runCaseOnThreadGroups(
        threadGroups,
        repetitions,
        lambda: runSUEngine(suPipe, suTelemetry, datasetFilePath, os.devnull)
    )

    pyseiskitTelemetry = PerformanceTelemetry(repetitions)
    runCaseOnThreadGroups(
        threadGroups,
        repetitions,
        lambda: runPyseiskitEngine(case.pyseiskitWorkflow, pyseiskitTelemetry, datasetFilePath)
    )

    print(f"{suPipe} on {case.datasetFilePath.name}")
    __printSummary("SU", suTelemetry)
    __printSummary("pyseiskit", pyseiskitTelemetry)
