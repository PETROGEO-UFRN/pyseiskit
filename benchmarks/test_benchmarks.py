"""Every case matches SU, and pyseiskit's I/O writes what SU would. Needs SU on PATH."""
import os
import shutil
import tempfile
import unittest

import numpy as np

from . import su
from .cases import CASES, IO, Case, mismatch
from .report.speedups import rows
from .report.table import render
from .run import cpu_list

TINY = su.Size("tiny", 64, 8, 0.004)


@unittest.skipIf(shutil.which("sugain") is None, "Seismic Unix not on PATH")
class BenchmarksTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.src = su.generate(TINY, self.tmp)
        self.out = os.path.join(self.tmp, "out.su")

    def test_every_case_matches_su_and_keeps_its_input(self):
        data, dt = su.samples(su.read(self.src))
        for case in (IO, *CASES):
            with self.subTest(case.name):
                self.assertIsNone(mismatch(case, self.src, self.out))
                before = data.copy()
                case.pyseiskit(data, dt)
                np.testing.assert_array_equal(data, before)

    def test_a_wrong_result_is_reported(self):
        wrong = Case("wrong", ("sugain", "tpow=2"), lambda data, dt: data * 1.01)
        self.assertIn("Mismatched elements", mismatch(wrong, self.src, self.out) or "")
        failing = Case("fails", ("sugain", "agc=1", "wagc=-5"), lambda data, dt: data)
        self.assertIn("RuntimeError: sugain agc=1 wagc=-5 exited with",
                      mismatch(failing, self.src, self.out) or "")

    def test_write_is_byte_identical_to_su(self):
        su.run(("sugain", "scale=2"), self.src, self.out)
        traces = su.read(self.src)
        data, dt = su.samples(traces)
        self.assertEqual((data.shape, dt), ((64, 8), 0.004))
        mine = os.path.join(self.tmp, "mine.su")
        su.write(traces, data * 2, mine)
        with open(self.out, "rb") as a, open(mine, "rb") as b:
            self.assertEqual(a.read(), b.read())

    def test_other_byte_order_is_rejected(self):
        with open(self.src, "rb") as f:
            raw = bytearray(f.read())
        trace_bytes = su.HEADER_BYTES + 4 * TINY.nt
        for start in range(su.NS_OFFSET, len(raw), trace_bytes):   # swap every ns field
            raw[start], raw[start + 1] = raw[start + 1], raw[start]
        with open(self.out, "wb") as f:
            f.write(raw)
        with self.assertRaisesRegex(ValueError, "byte order"):
            su.read(self.out)


class PureTest(unittest.TestCase):
    def test_cpu_list(self):
        self.assertEqual(cpu_list("0-2,5,10-11\n"), {0, 1, 2, 5, 10, 11})

    def test_report_rows(self):
        su_s = {"io [small]": 0.010, "tpow [small]": 0.012}
        py_s = {"io [small]": 0.005, "tpow [small]": 0.008, "tpow [small] compute only": 0.004}
        (io, tpow) = rows(su_s, py_s)
        self.assertEqual((io.total_speed, io.compute_speed), ("2.00x faster", "-"))
        self.assertEqual(tpow.total_speed, "1.50x faster")
        self.assertIsNotNone(tpow.su_compute)
        self.assertAlmostEqual(tpow.su_compute or 0.0, 0.002)
        self.assertEqual(tpow.compute_speed, "2.00x slower")
        self.assertIn("tpow [small]  12.00 ms  8.00 ms    1.50x faster", render([io, tpow]))


if __name__ == "__main__":
    unittest.main()
