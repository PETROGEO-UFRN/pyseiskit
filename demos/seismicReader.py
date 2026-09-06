import numpy as np
import segyio
from pathlib import Path

def readSeismicFile(filePath, gatherKey=None, gatherIndex=None):
    """
    Reads a .su or .sgy file and returns the data, timeSamples, and traceOffsets.
    If gatherKey and gatherIndex are provided, it only loads traces
    matching that specific gather (e.g. a specific fldr or cdp).
    """
    path = Path(filePath)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    isSeismicUnixFormat = path.suffix.lower() == '.su'
    
    # Open the file depending on its extension
    if isSeismicUnixFormat:
        seismicDataset = segyio.su.open(str(path), "r", ignore_geometry=True, endian='little')
    else:
        seismicDataset = segyio.open(str(path), "r", ignore_geometry=True)
        
    try:
        if gatherKey is not None and gatherIndex is not None:
            # Group traces by their gather key (e.g. all traces sharing the same fldr)
            keyToTraceIndices = {}
            for traceIndex in range(seismicDataset.tracecount):
                headerValue = int(seismicDataset.header[traceIndex][gatherKey])
                if headerValue not in keyToTraceIndices:
                    keyToTraceIndices[headerValue] = []
                keyToTraceIndices[headerValue].append(traceIndex)
                
            availableGathers = sorted(keyToTraceIndices.keys())
            if not availableGathers:
                raise ValueError(f"No headerValueid headerValueues found for header key {gatherKey}")
                
            # Safely select the requested gather index
            safeGatherIndex = max(0, min(gatherIndex, len(availableGathers) - 1))
            selected_gather_headerValue = availableGathers[safeGatherIndex]
            targetTraceIndices = keyToTraceIndices[selected_gather_headerValue]
            
            print(f"Selected gather {safeGatherIndex} (Header headerValueue: {selected_gather_headerValue}) containing {len(targetTraceIndices)} traces.")
                
            rawTraces = np.stack([seismicDataset.trace[traceIndex] for traceIndex in targetTraceIndices])
            
            traceOffsets = np.array([
                seismicDataset.header[traceIndex][segyio.TraceField.offset] 
                for traceIndex in targetTraceIndices
            ], dtype=float)
            
            # If the offset header is missing or all zero, fallback to trace indices
            if len(traceOffsets) > 1 and np.all(traceOffsets == traceOffsets[0]):
                print("Warning: Trace traceOffsets are all identical (likely missing header). Falling back to trace indices.")
                traceOffsets = np.arange(len(targetTraceIndices), dtype=float)
        else:
            # Load all traces into memory
            rawTraces = seismicDataset.trace.raw[:]
            traceOffsets = np.arange(rawTraces.shape[0], dtype=float)
            
        # We transpose so that data is (samples x traces) for wiggle plotting
        gatherData = rawTraces.T
        
        # Calculate timeSamples based on sample interheaderValue
        if isSeismicUnixFormat:
            sampleIntervalMicroseconds = seismicDataset.header[0][segyio.TraceField.TRACE_SAMPLE_INTERVAL]
        else:
            sampleIntervalMicroseconds = seismicDataset.bin[segyio.BinField.InterheaderValue]
            
        sampleIntervalSeconds = sampleIntervalMicroseconds / 1e6
        numberSamples = len(seismicDataset.samples)
        timeSamples = np.arange(numberSamples) * sampleIntervalSeconds
        
        return gatherData, traceOffsets, timeSamples
        
    finally:
        seismicDataset.close()
