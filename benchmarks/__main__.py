"""Time Seismic Unix or pyseiskit on the same inputs with pyperf. See README.md."""
import argparse
import atexit
import os
import sys

import pyperf

from . import su
from .cases import IO, mismatch, select


def time_su(loops, argv, src, dst):
    start = pyperf.perf_counter()
    for _ in range(loops):
        su.run(argv, src, dst)
    return pyperf.perf_counter() - start


def time_pyseiskit(loops, fn, src, dst):
    """Read, compute and write: the same work as the SU program."""
    start = pyperf.perf_counter()
    for _ in range(loops):
        traces = su.read(src)
        su.write(traces, fn(*su.samples(traces)), dst)
    return pyperf.perf_counter() - start


def time_compute(loops, fn, src):
    data, dt = su.samples(su.read(src))   # untimed
    start = pyperf.perf_counter()
    for _ in range(loops):
        fn(data, dt)
    return pyperf.perf_counter() - start


def cpu_list(text):
    """'0-5,8,10-11' -> {0, 1, 2, 3, 4, 5, 8, 10, 11}"""
    cpus = set()
    for part in text.strip().split(","):
        first, _, last = part.partition("-")
        cpus.update(range(int(first), int(last or first) + 1))
    return cpus


def with_default_affinity(argv):
    """pyperf pins workers only when given --affinity, so default to one performance core.
    On hybrid Intel CPUs an efficiency core ran sugain 2.4x slower than a performance core.
    The last core is used because the first one usually handles more interrupts."""
    if "--worker" in argv or any(arg.startswith("--affinity") for arg in argv):
        return argv
    allowed = os.sched_getaffinity(0)
    try:
        with open("/sys/devices/cpu_core/cpus") as f:   # performance cores, hybrid CPUs only
            performance = cpu_list(f.read()) & allowed
    except (OSError, ValueError):
        performance = set()
    return [*argv, f"--affinity={max(performance or allowed)}"]


def forward(cmd, args):
    """Pass our options on to pyperf's worker processes."""
    cmd += ["--impl", args.impl]
    for flag, values in (("--case", args.case), ("--size", args.size),
                         ("--input", args.input), ("--skip", args.skip)):
        for value in values or ():
            cmd += [flag, value]


def main():
    sys.argv = with_default_affinity(sys.argv)
    runner = pyperf.Runner(program_args=("-m", "benchmarks"), add_cmdline_args=forward)
    parser = runner.argparser
    parser.add_argument("--impl", choices=("su", "pyseiskit"), required=True)
    parser.add_argument("--case", action="append", metavar="GLOB",
                        help="cases to run, e.g. 'sugain tpow*' (default: all)")
    parser.add_argument("--size", action="append", choices=list(su.SIZES),
                        help=f"generated input sizes (default: {', '.join(su.DEFAULT_SIZES)}, "
                             "unless --input)")
    parser.add_argument("--input", action="append", metavar="FILE",
                        help="your own SU file, e.g. from benchmarks/data/")
    # Benchmarks whose check failed in the parent. Workers must skip the same ones, because
    # pyperf matches a worker's task to the parent's by registration order.
    parser.add_argument("--skip", action="append", default=[], help=argparse.SUPPRESS)
    args = runner.parse_args()
    cases = select(args.case)
    sizes = [su.SIZES[name] for name in (args.size or (() if args.input else su.DEFAULT_SIZES))]
    inputs = [(size.name, su.input_path(size)) for size in sizes]
    inputs += [(os.path.basename(path), os.path.abspath(path)) for path in args.input or ()]
    labels = [label for label, _ in inputs]
    if len(set(labels)) != len(labels):
        sys.exit(f"inputs need distinct names, got {labels}: rename a file")

    out = os.path.join(su.OUT_DIR, f"pyseiskit-bench-{os.getpid()}.su")
    atexit.register(lambda: os.path.exists(out) and os.remove(out))

    if not args.worker:   # once, in the parent: make the inputs, check outputs match
        for size in sizes:
            su.generate(size)
        for label, src in inputs:
            for case in cases:
                name = f"{case.name} [{label}]"
                problem = mismatch(case, src, out)
                if problem:
                    print(f"FAILED {name}: pyseiskit differs from SU, not timed\n{problem}\n",
                          file=sys.stderr)
                    args.skip.append(name)

    for label, src in inputs:
        for case in (IO, *cases):
            name = f"{case.name} [{label}]"
            if name in args.skip:
                continue
            if args.impl == "su":
                runner.bench_time_func(name, time_su, case.su, src, out)
            else:
                runner.bench_time_func(name, time_pyseiskit, case.pyseiskit, src, out)
                if case is not IO:
                    runner.bench_time_func(f"{name} compute only", time_compute,
                                           case.pyseiskit, src)

    if args.skip and not args.worker:
        sys.exit(f"{len(args.skip)} benchmark(s) not timed because the check failed: "
                 + ", ".join(args.skip))


if __name__ == "__main__":
    main()
