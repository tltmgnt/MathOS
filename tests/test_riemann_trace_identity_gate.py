"""Regression checks for fixed-operator xi/determinant trace identity obligations."""
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_arithmetic_spectral import FIRST_ZETA_ZERO_REFERENCE
from mathos.research.riemann_fixed_jacobi import jacobi_coefficients
from mathos.research.riemann_trace_identity_gate import (
    finite_symmetric_determinant, logdet_positive_jacobi,
    prime_power_dirichlet_prefix, report,
)


class TraceIdentityGateTests(unittest.TestCase):
    def test_two_by_two_determinant(self):
        d, b = [2.0, 4.0], [1.0]
        # H eigenvalues 3 +/- sqrt(2); determinant H = 7.
        self.assertAlmostEqual(logdet_positive_jacobi(d, b, 0), math.log(7), places=14)
        expected = ((2-1)*(4-1)-1)*((2+1)*(4+1)-1)/(7**2)
        self.assertAlmostEqual(finite_symmetric_determinant(1.0, d, b), expected, places=14)

    def test_zero_normalization(self):
        d, b = jacobi_coefficients(32)
        self.assertAlmostEqual(finite_symmetric_determinant(0, d, b), 1, places=12)

    def test_evenness_of_finite_spectral_determinant(self):
        d, b = jacobi_coefficients(80)
        for x in [1., 5., 10., 14.]:
            self.assertAlmostEqual(
                finite_symmetric_determinant(x, d, b),
                finite_symmetric_determinant(-x, d, b), places=12)

    def test_first_ordinate_is_strictly_below_floor(self):
        data = report(128)
        p = data["infinite_regularized_determinant"]
        self.assertGreater(p["spectral_floor_lower"], FIRST_ZETA_ZERO_REFERENCE)
        self.assertTrue(p["determinant_nonzero_at_first_zeta_ordinate"])
        self.assertFalse(p["zero_free_entire_multiplier_exists"])

    def test_no_proof_promotion(self):
        r = report(128)
        self.assertFalse(any(r["assurance"].values()))
        self.assertFalse(r["arithmetic_trace_obligation"]["global_identity_proved"])
        self.assertEqual(r["proof_obligations"]["RH.zero_identity"].split(":")[0], "OPEN")

    def test_prime_power_prefix_takes_prime_powers(self):
        expected = math.log(2)/2**2 + math.log(3)/3**2 + math.log(2)/4**2
        self.assertAlmostEqual(prime_power_dirichlet_prefix(2, 4), expected, places=14)

    def test_prime_power_sum_monotone_for_real_sigma(self):
        a = prime_power_dirichlet_prefix(2, 32)
        b = prime_power_dirichlet_prefix(2, 128)
        self.assertGreater(b, a)
        self.assertGreater(a, 0)

    def test_invalid_euler_domain(self):
        for sigma in [1, 0.5, -1, float("nan"), float("inf")]:
            with self.subTest(sigma=sigma), self.assertRaises(ValueError):
                prime_power_dirichlet_prefix(sigma, 100)

    def test_invalid_finite_matrix_domain(self):
        with self.assertRaises(ValueError):
            logdet_positive_jacobi([2., 4.], [1.], -2)
        with self.assertRaises(ValueError):
            logdet_positive_jacobi([2.], [1.], 0)
        with self.assertRaises(ValueError):
            finite_symmetric_determinant(19, *jacobi_coefficients(16))

    def test_invalid_sizes(self):
        for count in [0, 2, 4097, 32.0, True]:
            with self.subTest(count=count), self.assertRaises(ValueError):
                report(count)

    def test_finite_size_is_not_spectral_proof(self):
        a = report(64)
        b = report(128)
        self.assertEqual(a["infinite_regularized_determinant"]["spectral_floor_lower"],
                         b["infinite_regularized_determinant"]["spectral_floor_lower"])
        self.assertTrue(a["finite_diagnostic"]["finite_determinants_do_not_certify_infinite_zeros"])

    def test_cli_output(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "gate.json"
            run = subprocess.run(
                [sys.executable, "-m", "mathos.research.riemann_trace_identity_gate",
                 "--size", "64", "--output", str(destination)],
                capture_output=True, text=True, check=True,
            )
            self.assertEqual(run.returncode, 0)
            result = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "GLOBAL_ZERO_FREE_FACTOR_IDENTITY_REFUTED_FOR_FIXED_JACOBI")
            self.assertFalse(result["assurance"]["riemann_hypothesis_proved"])


if __name__ == "__main__":
    unittest.main()
