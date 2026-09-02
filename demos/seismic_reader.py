import numpy as np
import segyio
from pathlib import Path

def read_seismic_file(filepath, gather_key=None, gather_index=None):
    """
    Reads a .su or .sgy file and returns the data, times, and offsets.
    If gather_key and gather_index are provided, it only loads traces
    matching that specific gather (e.g. a specific fldr or cdp).
    """
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    is_su = path.suffix.lower() == '.su'
    
    # Open the file depending on its extension
    if is_su:
        dataset = segyio.su.open(str(path), "r", ignore_geometry=True, endian='little')
    else:
        dataset = segyio.open(str(path), "r", ignore_geometry=True)
        
    try:
        if gather_key is not None and gather_index is not None:
            # Group traces by their gather key (e.g. all traces sharing the same fldr)
            key_to_trace_indices = {}
            for i in range(dataset.tracecount):
                val = int(dataset.header[i][gather_key])
                if val not in key_to_trace_indices:
                    key_to_trace_indices[val] = []
                key_to_trace_indices[val].append(i)
                
            available_gathers = sorted(key_to_trace_indices.keys())
            if not available_gathers:
                raise ValueError(f"No valid values found for header key {gather_key}")
                
            # Safely select the requested gather index
            safe_index = max(0, min(gather_index, len(available_gathers) - 1))
            selected_gather_val = available_gathers[safe_index]
            trace_indices = key_to_trace_indices[selected_gather_val]
            
            print(f"Selected gather {safe_index} (Header value: {selected_gather_val}) containing {len(trace_indices)} traces.")
                
            raw_traces = np.stack([dataset.trace[i] for i in trace_indices])
            
            offsets = np.array([
                dataset.header[i][segyio.TraceField.offset] 
                for i in trace_indices
            ], dtype=float)
            
            # If the offset header is missing or all zero, fallback to trace indices
            if len(offsets) > 1 and np.all(offsets == offsets[0]):
                print("Warning: Trace offsets are all identical (likely missing header). Falling back to trace indices.")
                offsets = np.arange(len(trace_indices), dtype=float)
        else:
            # Load all traces into memory
            raw_traces = dataset.trace.raw[:]
            offsets = np.arange(raw_traces.shape[0], dtype=float)
            
        # We transpose so that data is (samples x traces) for wiggle plotting
        data = raw_traces.T
        
        # Calculate times based on sample interval
        if is_su:
            dt_micros = dataset.header[0][segyio.TraceField.TRACE_SAMPLE_INTERVAL]
        else:
            dt_micros = dataset.bin[segyio.BinField.Interval]
            
        dt_seconds = dt_micros / 1e6
        num_samples = len(dataset.samples)
        times = np.arange(num_samples) * dt_seconds
        
        return data, offsets, times
        
    finally:
        dataset.close()
