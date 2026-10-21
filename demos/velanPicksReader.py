from pathlib import Path
from pyseiskit.modules.velocityModel import VelocityPicksType

def readVelanPicks(filePath) -> VelocityPicksType:
    """
    Reads a SU `velan` picks file: one `cdp=` line listing the picked CDPs,
    then one `tnmo=` and one `vnmo=` line per CDP, in the same order.
    """
    path = Path(filePath)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    pickedCdps = []
    pickedTimes = []
    pickedVelocities = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue

        key, values = line.split("=", 1)
        parsedValues = [float(value) for value in values.split(",") if value.strip()]
        if key == "cdp":
            pickedCdps = [int(cdp) for cdp in parsedValues]
        elif key == "tnmo":
            pickedTimes.append(parsedValues)
        elif key == "vnmo":
            pickedVelocities.append(parsedValues)

    if not (len(pickedCdps) == len(pickedTimes) == len(pickedVelocities)):
        raise ValueError("The picks file must have one tnmo= and one vnmo= line per CDP.")

    return {
        cdp: {"times": times, "velocity": velocities}
        for cdp, times, velocities in zip(pickedCdps, pickedTimes, pickedVelocities)
    }
