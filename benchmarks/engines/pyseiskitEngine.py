import sys
from dataclasses import dataclass
from typing import Callable

import numpy as np
import segyio

from ..consts.SCALE_CONVERSION import MICROSECONDS_TO_SECONDS
from ..perf.PerformanceTelemetry import PerformanceTelemetry

@dataclass(frozen=True)
class DatasetProps:
    # what a workflow can take from the dataset; only what the current functions need
    data: np.ndarray  # samples x traces
    dt: float         # sample interval, seconds

def readDatasetProps(datasetPath: str) -> DatasetProps:
    # SU files are in this machine's byte order; segyio.tools.dt() fails on SU, so the
    # sample interval comes from the first trace header (microseconds)
    with segyio.su.open(datasetPath, ignore_geometry=True, endian=sys.byteorder) as suFile:
        firstTraceInterval = suFile.attributes(segyio.TraceField.TRACE_SAMPLE_INTERVAL)[0]
        dtMicroseconds = int(firstTraceInterval[0])
        return DatasetProps(suFile.trace.raw[:].T, dtMicroseconds * MICROSECONDS_TO_SECONDS)

def runPyseiskitEngine(
    workflow: Callable[[DatasetProps], np.ndarray],
    telemetry: PerformanceTelemetry,
    datasetPath: str,
):
    # pyseiskit works on arrays: only the workflow is measured, no file reading or writing
    props = readDatasetProps(datasetPath)
    telemetry.start()
    workflowOutput = workflow(props)
    telemetry.stop()
    return workflowOutput
