"""Adversarial checks for the TECT-X Riemann spectral toy obstruction."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_spectral_obstruction import (
    build_report, positive_circle_eigen_count,
)


class SpectralObstructionTests(unittest.TestCase):
    def test_periodic_exact_counts(self):
        self.assertEqual([positive_circle_eigen_count(Fraction(n)) for n in range(5)],
                         [0, 1, 2, 3, 4])

    def test_twisted_exact_counts(self):
        half = Fraction(1, 2)
        self.assertEqual(positive_circle_eigen_count(Fraction(0), half), 0)
        self.assertEqual(positive_circle_eigen_count(Fraction(1, 3), half), 0)
        self.assertEqual(positive_circle_eigen_count(half, half), 1)
        self.assertEqual(positive_circle_eigen_count(Fraction(3, 2), half), 2)
        self.assertEqual(positive_circle_eigen_count(Fraction(5, 2), half), 3)

    def test_phase_normalization(self):
        self.assertEqual(positive_circle_eigen_count(Fraction(5), Fraction(1, 3)), 5)

    def test_negative_radius_rejected(self):
        with self.assertRaises(ValueError):
            positive_circle_eigen_count(Fraction(-1))

    def test_bad_phase_rejected(self):
        for phase in [Fraction(-1, 2), Fraction(1)]:
            with self.subTest(phase=phase), self.assertRaises(ValueError):
                positive_circle_eigen_count(Fraction(10), phase)

    def test_reject_nonexact_float(self):
        with self.assertRaises(ValueError):
            positive_circle_eigen_count(1.0)
        with self.assertRaises(ValueError):
            positive_circle_eigen_count(Fraction(2), 0.5)

    def test_every_normalized_unit_interval_has_one_eigenvalue(self):
        for phase in [Fraction(0), Fraction(1, 2), Fraction(2, 7), Fraction(99, 100)]:
            for k in range(1, 70):
                count = positive_circle_eigen_count(Fraction(k), phase)
                before = positive_circle_eigen_count(Fraction(k-1), phase)
                self.assertEqual(count-before, 1)

    def test_report_is_unconditionally_noncertifying(self):
        report = build_report(10, Fraction(1, 3))
        self.assertEqual(len(report["fixed_log_interval"]["exact_sample_rows"]), 10)
        self.assertFalse(any(report["assurance"].values()))
        self.assertTrue(report["fixed_log_interval"]["comparison_is_analytic"])
        self.assertIn("Riemann-von Mangoldt", report["fixed_log_interval"]["zeta_counting_input"])

    def test_source_digest_is_stable(self):
        self.assertEqual(build_report(3)["source_sha256"], build_report(4)["source_sha256"])

    def test_max_radius_bounds(self):
        for n in [0, 2001, True, 1.0]:
            with self.subTest(n=n), self.assertRaises(ValueError):
                build_report(n)

    def test_cli_writes_json_with_no_proof_promotion(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "spectral.json"
            subprocess.run(
                [sys.executable, "-m", "mathos.research.riemann_spectral_obstruction",
                 "--max-radius", "4", "--phase-numerator", "1",
                 "--phase-denominator", "2", "--output", str(dest)],
                check=True, capture_output=True, text=True,
            )
            report = json.loads(dest.read_text(encoding="utf-8"))
            self.assertEqual(report["fixed_log_interval"]["exact_sample_rows"][-1]["positive_eigenvalue_count"], 4)
            self.assertFalse(report["assurance"]["riemann_hypothesis_proved"])

    def test_negative_denominator_rejected_when_phase_invalid(self):
        with self.assertRaises(ValueError):
            build_report(3, Fraction(-1, 3))


if __name__ == "__main__":
    unittest.main()
