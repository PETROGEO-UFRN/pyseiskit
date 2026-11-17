from pydantic.dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Callable
import numpy as np
import pyseiskit as pyseiskit

from ..engines.pyseiskitEngine import DatasetProps
from .getDatasetFilePath import getDatasetFilePath

class DATASET_FILE_NAMES(StrEnum):
    # Whole line: 37824 traces x 1001 samples, dt 4 ms, 160 MB
    TAC_204RL239 = "tac-204RL239.su" 
    # one shot gather (from tac-204RL239.su): 96 traces x 1001 samples, dt 4 ms, 0.4 MB
    SHOT_50 = "shot50.su"  

@dataclass(frozen=True)
class BenchmarkCase:
    datasetFilePath: Path
    pyseiskitWorkflow: Callable[[DatasetProps], np.ndarray]
    suWorkflow: Callable[[], str]  # the SU pipe that gives the same result, read from stdin


CASES = [
    BenchmarkCase(
        datasetFilePath=getDatasetFilePath(DATASET_FILE_NAMES.SHOT_50),
        pyseiskitWorkflow=lambda props: pyseiskit.gain.applyTimePowerGain(props.data, 2.0, props.dt),
        suWorkflow=lambda: "sugain tpow=2",
    ),
    BenchmarkCase(
        datasetFilePath=getDatasetFilePath(DATASET_FILE_NAMES.SHOT_50),
        pyseiskitWorkflow=lambda props: pyseiskit.gain.applyAmplitudePowerGain(
            pyseiskit.gain.applyTimePowerGain(props.data, 2.0, props.dt), 0.5
        ),
        suWorkflow=lambda: "sugain tpow=2 | sugain gpow=0.5",
    ),
    BenchmarkCase(
        datasetFilePath=getDatasetFilePath(DATASET_FILE_NAMES.TAC_204RL239),
        pyseiskitWorkflow=lambda props: pyseiskit.gain.applyTimePowerGain(props.data, 2.0, props.dt),
        suWorkflow=lambda: "sugain tpow=2",
    ),
    BenchmarkCase(
        datasetFilePath=getDatasetFilePath(DATASET_FILE_NAMES.TAC_204RL239),
        pyseiskitWorkflow=lambda props: pyseiskit.gain.applyAmplitudePowerGain(
            pyseiskit.gain.applyTimePowerGain(props.data, 2.0, props.dt), 0.5
        ),
        suWorkflow=lambda: "sugain tpow=2 | sugain gpow=0.5",
    ),
]
