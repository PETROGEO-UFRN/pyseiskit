from pathlib import Path
import numpy as np

def readVelanPicks(filePath):
    """
    Reads a SU `velan` picks file: one `cdp=` line listing the picked CDPs,
    then one `tnmo=` and one `vnmo=` line per CDP, in the same order.
    Returns the picks keyed by CDP, as {cdp: {"times": [...], "velocity": [...]}}.
    """
    path = Path(filePath)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    pickedCdps = np.array([], dtype=int)
    pickedTimes = []
    pickedVelocities = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue

        key, values = line.split("=", 1)
        parsedValues = np.array(values.split(","), dtype=float)
        if key == "cdp":
            pickedCdps = parsedValues.astype(int)
            continue
        if key == "tnmo":
            pickedTimes.append(parsedValues.tolist())
            continue
        if key == "vnmo":
            pickedVelocities.append(parsedValues.tolist())

    if not (len(pickedCdps) == len(pickedTimes) == len(pickedVelocities)):
        raise ValueError("The picks file must have one tnmo= and one vnmo= line per CDP.")

    velocityPicks = {}
    for cdp, times, velocities in zip(pickedCdps, pickedTimes, pickedVelocities):
        velocityPicks[int(cdp)] = {"times": times, "velocity": velocities}
    return velocityPicks
