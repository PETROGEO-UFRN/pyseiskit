"""Seismic Unix files and programs: generate inputs, run SU, read and write traces."""
import os
import subprocess
import tempfile
from dataclasses import dataclass

import numpy as np

# Generated inputs are cached here; benchmarks/data/ is for your own datasets (--input).
CACHE_DIR = os.path.join(os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"),
                         "pyseiskit-benchmarks")
# Outputs go to RAM when possible, so disk writeback adds no noise to the timings.
OUT_DIR = "/dev/shm" if os.path.isdir("/dev/shm") else tempfile.gettempdir()

HEADER_BYTES = 240
NS_OFFSET, DT_OFFSET = 114, 116   # uint16 fields of the SU trace header; dt in microseconds


@dataclass(frozen=True)
class Size:
    name: str
    nt: int     # samples per trace
    ntr: int    # traces
    dt: float   # sample interval, seconds


# Different dt on purpose: a pyseiskit call that hard-codes dt fails on one of them.
SIZES = {s.name: s for s in (
    Size("small", 1001, 240, 0.004),      # ~1 MB
    Size("medium", 2001, 2400, 0.002),    # ~19 MB
    Size("large", 4001, 12000, 0.001),    # ~186 MB
)}
DEFAULT_SIZES = ("small", "medium")


def input_path(size: Size, directory: str = CACHE_DIR) -> str:
    """The name encodes every parameter, so a cached file is valid when its name matches."""
    return os.path.join(directory, f"{size.name}_{size.nt}x{size.ntr}_dt{size.dt * 1e6:.0f}us.su")


def generate(size: Size, directory: str = CACHE_DIR) -> str:
    """Dipping planes plus seeded noise, made by SU itself. Cached in `directory`."""
    path = input_path(size, directory)
    if not os.path.exists(path):
        os.makedirs(directory, exist_ok=True)
        planes, partial = path + ".planes", path + ".part"
        run(("suplane", f"nt={size.nt}", f"ntr={size.ntr}", f"dt={size.dt}"), os.devnull, planes)
        run(("suaddnoise", "sn=5", "seed=1"), planes, partial)
        os.remove(planes)
        os.replace(partial, path)
    return path


def run(argv, src: str, dst: str) -> None:
    """Run an SU program with `src` on stdin and `dst` on stdout."""
    with open(src, "rb") as stdin, open(dst, "wb") as stdout:
        done = subprocess.run(argv, stdin=stdin, stdout=stdout, stderr=subprocess.PIPE)
    if done.returncode:
        raise RuntimeError(f"{' '.join(argv)} exited with {done.returncode}: "
                           f"{done.stderr.decode(errors='replace').strip()}")


def read(path: str) -> np.ndarray:
    """Every trace (240 header bytes + float32 samples), in one read as an SU program does.

    SU files have no file header and use the machine's byte order, so the sample count
    comes from the first trace header, and a file in the other byte order is rejected."""
    with open(path, "rb") as f:
        first = f.read(HEADER_BYTES)
    ns = int(np.frombuffer(first, "=u2", 1, NS_OFFSET)[0]) if len(first) == HEADER_BYTES else 0
    trace = np.dtype([("header", f"V{HEADER_BYTES}"), ("data", "=f4", (ns,))])
    if ns == 0 or os.path.getsize(path) % trace.itemsize:
        raise ValueError(f"{path} is not an SU file in this machine's byte order "
                         "(convert it with suswapbytes)")
    return np.fromfile(path, trace)


def samples(traces: np.ndarray):
    """(samples x traces view, sample interval in seconds from the first header)."""
    dt_us = np.frombuffer(traces["header"][0].tobytes(), "=u2", 1, DT_OFFSET)[0]
    return traces["data"].T, int(dt_us) / 1e6


def write(traces: np.ndarray, data: np.ndarray, dst: str) -> None:
    """Write `data` with the headers of `traces`, in one pass. Reuses `traces`' memory."""
    traces["data"] = data.T
    traces.tofile(dst)
