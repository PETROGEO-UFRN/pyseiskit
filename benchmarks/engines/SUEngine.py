import subprocess

from ..perf.PerformanceTelemetry import PerformanceTelemetry

def runSUEngine(
    workflowUnixString: str,
    telemetry: PerformanceTelemetry,
    datasetPath: str,
    outputPath: str
):
    with open(datasetPath, "rb") as inputFile, open(outputPath, "wb") as outputFile:
        telemetry.start()
        completedWorkflow = subprocess.run(
            workflowUnixString,
            shell=True,
            stdin=inputFile,
            stdout=outputFile,
            stderr=subprocess.PIPE,
            check=True
        )
        telemetry.stop()
    return completedWorkflow
