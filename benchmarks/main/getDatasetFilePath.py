from pathlib import Path

DATASETS_DIRECTORY: Path = Path(__file__).resolve().parent.parent / "data"

def getDatasetFilePath(filePath: str) -> Path:
	datasetFilePath = DATASETS_DIRECTORY / filePath

	return datasetFilePath
