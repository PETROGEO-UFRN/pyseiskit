import mmap
import multiprocessing
import time

import numpy as np

from ..consts.SCALE_CONVERSION import MICROSECONDS_TO_SECONDS
from .cgroupServices import (
    openAndResetMemoryPeak,
    readAndCloseMemoryPeak,
    readCgroupPath,
    readCPUMicroseconds,
    readMemoryCurrentBytes,
)

# Measurements come from the cgroup of the process calling start/stop: the kernel counts every
# process in it together, so SU programs and pipelines are measured like Python itself.

# one row per run
TelemetryRecordType = np.dtype([
    ("wallSeconds", np.float64),
    ("cpuSeconds", np.float64),
    ("peakMemoryIncreaseBytes", np.int64),  # peak during the run minus memory at its start
])


class PerformanceTelemetry:
    # Raw telemetry of one case: a table with room for `capacity` runs, in memory shared with
    # every process forked after it is created, so runs in any of them land in the same
    # table, in any order. Runs inside one cgroup must follow one another.
    def __init__(self, capacity: int):
        if capacity < 1:
            raise ValueError(f"capacity must be at least 1, got {capacity}")
        sharedMemory = mmap.mmap(-1, capacity * TelemetryRecordType.itemsize)  # anonymous, shared
        self.__recordTable = np.frombuffer(sharedMemory, dtype=TelemetryRecordType)
        self.__recordCount = multiprocessing.Value("q", 0)  # shared, with its own lock
        self.__memoryPeakFile = -1  # kept open during a run: its reset only holds for this file
        self.__startMemoryBytes = 0
        self.__startCPUMicroseconds = 0
        self.__startWallSeconds = 0.0

    @property
    def records(self) -> np.ndarray:
        # a copy of the rows written so far
        return self.__recordTable[:self.__recordCount.value].copy()

    def start(self):
        # start the measurement
        cgroup = readCgroupPath()
        self.__memoryPeakFile = openAndResetMemoryPeak(cgroup)
        self.__startMemoryBytes = readMemoryCurrentBytes(cgroup)
        self.__startCPUMicroseconds = readCPUMicroseconds(cgroup)
        self.__startWallSeconds = time.perf_counter()

    def stop(self):
        # stop the measurement
        wallSeconds = time.perf_counter() - self.__startWallSeconds
        cpuMicroseconds = readCPUMicroseconds(readCgroupPath()) - self.__startCPUMicroseconds
        cpuSeconds = cpuMicroseconds * MICROSECONDS_TO_SECONDS
        # Memory of every process in the cgroup, SU programs included. The kernel also counts
        # the file cache of files written during the run, such as SU's output file.
        peakMemoryIncreaseBytes = readAndCloseMemoryPeak(self.__memoryPeakFile) - self.__startMemoryBytes
        with self.__recordCount.get_lock():
            rowIndex = self.__recordCount.value
            if rowIndex >= len(self.__recordTable):
                raise RuntimeError(f"telemetry is full: room for {len(self.__recordTable)} runs")
            self.__recordCount.value = rowIndex + 1
        self.__recordTable[rowIndex] = (wallSeconds, cpuSeconds, peakMemoryIncreaseBytes)
