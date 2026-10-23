import shutil
import subprocess
import tempfile
from pathlib import Path
import numpy as np

def isSeismicUnixAvailable() -> bool:
    return shutil.which("unisam2") is not None

def runSeismicUnix(command: str, numberSamples: int, inputModel=None) -> np.ndarray:
    """
    Runs a Seismic Unix shell pipeline in a temporary folder and returns its `output.bin`.

    Binary files are C-style float32 with one trace per CDP, as SU binary programs and
    `sustrip` use them, read back as a model [2D: samples x cdps].
    When inputModel [2D: samples x cdps] is given, it is written as `input.bin` first.
    Pipelines run in that folder, so programs that need disk files (e.g. `suwind skip=`)
    can create intermediate files there.
    """
    with tempfile.TemporaryDirectory() as workFolder:
        workPath = Path(workFolder)
        if inputModel is not None:
            np.ascontiguousarray(inputModel.T, dtype='<f4').tofile(workPath / "input.bin")

        result = subprocess.run(
            command,
            shell=True,
            cwd=workPath,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Seismic Unix failed: {result.stderr}")

        outputData = np.fromfile(workPath / "output.bin", dtype='<f4')
        return outputData.reshape(-1, numberSamples).T.astype(float)
