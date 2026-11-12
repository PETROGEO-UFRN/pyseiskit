# Benchmarks: pyseiskit vs Seismic Unix

Times pyseiskit against Seismic Unix (SU 44R28, the reference) on the same inputs, after
checking that both give the same output. Timing, statistics, CPU pinning, metadata and
comparisons come from [pyperf](https://pyperf.readthedocs.io), the tool behind CPython's
own benchmarks.

    python -m benchmarks.run --impl su        -o su.json
    python -m benchmarks.run --impl pyseiskit -o pyseiskit.json
    python -m benchmarks.report.cli su.json pyseiskit.json

The report gives each case's speed relative to SU twice: end to end, and for the
computation alone. Read both. SU pays for starting a program on every run, so on small
inputs pyseiskit can be faster end to end while its computation is slower.
`python -m pyperf compare_to su.json pyseiskit.json --table` adds significance tests,
for end-to-end times only.

Our options:

    --case GLOB    cases to run, e.g. 'sugain tpow*' (repeatable; default all)
    --size NAME    generated input: small, medium, large (repeatable;
                   default small and medium, unless --input is given)
    --input FILE   your own SU file, e.g. from benchmarks/data/ (repeatable)

Everything else is a pyperf option: `--fast` or `--rigorous`, `-p` processes, `-n` values
per process, `--affinity`. Without `--affinity`, runs are pinned to the last performance
core (from `/sys/devices/cpu_core/cpus` on hybrid Intel CPUs, where an efficiency core was
2.4x slower), or else to the last allowed CPU. Before numbers you want to publish, run
`python -m pyperf system tune` (needs root); see
[Tune the system](https://pyperf.readthedocs.io/en/latest/system.html). Inspect results
with `python -m pyperf show --stats su.json` or `pyperf hist`.

The two sides run one after the other, not interleaved, so a machine that drifts between
them (heat, background load) shows up as a difference: run both on a quiet machine,
back to back.

Needs Python 3.11+ (for pyperf) and SU on `PATH`.

## What is measured

    cases.py      every case: an SU command and the pyseiskit function that must match it
    su.py         SU inputs (suplane | suaddnoise, cached in ~/.cache/pyseiskit-benchmarks),
                  running SU, reading and writing SU files
    run.py        the pyperf script: checks every case, then registers the benchmarks
    report/       end-to-end and compute speedups from the two result files:
                  results.py loads them, speedups.py computes, table.py formats,
                  cli.py is the command line

For every case and input:

- `<case> [input]`, end to end, on both sides. SU: start the program, read, compute,
  write. pyseiskit: read, compute, write, each file in one pass as SU does. Python
  start-up and imports are not timed: this is pyseiskit used as a library.
- `io [input]`, the same with no computation: plain `sugain` (a documented no-op) against
  a pyseiskit read and write. The report estimates SU's computation as the case's time
  minus this.
- `<case> [input] compute only`, pyseiskit only: the function on data already in memory.

Before anything is timed, the parent process runs every case once on every input and
compares pyseiskit's output with SU's (`numpy.testing.assert_allclose`, rtol 1e-5 relative
to the largest sample). A case that differs, or fails on either side, is printed with the
differing elements and not timed; the others still run, and the run exits with 1.

Your own files must be in this machine's byte order (otherwise they are rejected) and,
for the time gains, start at delrt=0: pyseiskit's time gains count t from the first
sample, sugain from delrt. Outputs go to `/dev/shm` when it exists, so disk writeback adds
no noise. The generated inputs use a different `dt` per size, so a function that
hard-codes the sample interval fails the check.

## Adding a case

Add a `Case` to `CASES` in `cases.py`:

    Case("sugain tpow=1", ("sugain", "tpow=1"),
         lambda data, dt: gain.applyTimePowerGain(data, 1.0, dt))

`data` is (samples, traces) float32 and must not be modified. Take `dt` from the argument.
`python -m unittest benchmarks.test_benchmarks` checks every case against SU on a tiny
input, and that pyseiskit's write is byte-identical to SU's.
