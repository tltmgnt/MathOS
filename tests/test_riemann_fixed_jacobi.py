"""Tests for fixed, non-diagonal arithmetic self-adjoint Jacobi negative control."""
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_arithmetic_spectral import (
    FIRST_ZETA_ZERO_REFERENCE, inverse_main_term,
)
from mathos.research.riemann_fixed_jacobi import (
    PERTURBATION_NORM_UPPER, coupling, jacobi_coefficients, report,
    sturm_count_below,
)


class JacobiCandidateTests(unittest.TestCase):
    def test_prime_power_couplings_not_all_zero(self):
        self.assertGreater(coupling(1), 0)  # Lambda(2)
        self.assertGreater(coupling(3), 0)  # Lambda(4)
        self.assertEqual(coupling(5), 0.0)  # Lambda(6)
        self.assertGreater(coupling(8), 0)  # Lambda(9)

    def test_all_couplings_below_bound(self):
        for n in range(1, 257):
            self.assertLess(coupling(n), 0.2)
            self.assertGreaterEqual(coupling(n), 0)

    def test_sturm_on_independent_toy_matrix(self):
        # Eigenvalues of [[2,1],[1,2]] are 1 and 3.
        d, b = [2.0, 2.0], [1.0]
        self.assertEqual(sturm_count_below(0.5, d, b), 0)
        self.assertEqual(sturm_count_below(1.5, d, b), 1)
        self.assertEqual(sturm_count_below(3.5, d, b), 2)

    def test_zero_couplings_reduce_to_diagonal_counter(self):
        d = [3.0, 7.0, 11.0]
        for t, expected in [(1, 0), (4, 1), (8, 2), (12, 3)]:
            self.assertEqual(sturm_count_below(t, d, [0.0, 0.0]), expected)

    def test_invalid_matrix_rejected(self):
        with self.assertRaises(ValueError):
            sturm_count_below(1.0, [1.0], [1.0])
        with self.assertRaises(ValueError):
            sturm_count_below(float("nan"), [1.0], [])
        with self.assertRaises(ValueError):
            sturm_count_below(2.0, [float("nan")], [])

    def test_jacobi_coefficients_are_genuine(self):
        d, b = jacobi_coefficients(32)
        self.assertEqual(len(d), 32)
        self.assertEqual(len(b), 31)
        self.assertGreater(d[0], FIRST_ZETA_ZERO_REFERENCE + PERTURBATION_NORM_UPPER)
        self.assertGreater(sum(abs(v) for v in b), 0)

    def test_input_bounds(self):
        for invalid in [1, 4097, True, 2.0]:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                jacobi_coefficients(invalid)
        for invalid in [0, 4096, True]:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                coupling(invalid)

    def test_counting_minmax_bounds(self):
        result = report(256)
        op = result["operator"]
        self.assertTrue(op["is_fixed_self_adjoint"])
        self.assertFalse(op["is_parameter_dependent"])
        self.assertFalse(op["is_hilbert_polya_realization"])
        self.assertGreater(op["smallest_spectral_point_lower"],
                           FIRST_ZETA_ZERO_REFERENCE)
        for row in result["finite_diagnostic"]["counting_rows"]:
            self.assertLessEqual(row["unperturbed_lower"], row["jacobi_count_below"])
            self.assertLessEqual(row["jacobi_count_below"], row["unperturbed_upper"])
        self.assertFalse(any(result["assurance"].values()))

    def test_truncated_model_has_proved_spectral_floor_not_rh(self):
        d, _ = jacobi_coefficients(4)
        self.assertGreater(d[0] - PERTURBATION_NORM_UPPER, 14.5)
        result = report(256)
        self.assertFalse(result["assurance"]["spectral_zero_correspondence"])

    def test_smaller_truncation_rejected_when_insufficient(self):
        with self.assertRaisesRegex(ValueError, "too short"):
            report(16)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "fixed_jacobi.json"
            subprocess.run(
                [sys.executable, "-m", "mathos.research.riemann_fixed_jacobi",
                 "--count", "256", "--output", str(p)],
                capture_output=True, text=True, check=True,
            )
            result = json.loads(p.read_text(encoding="utf-8"))
            self.assertEqual(result["schema"], "mathos_tectx_fixed_jacobi_hilbert_polya_gate/1")
            self.assertFalse(any(result["assurance"].values()))


if __name__ == "__main__":
    unittest.main()
