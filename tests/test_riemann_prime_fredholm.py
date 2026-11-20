"""Tests for arithmetic Fredholm half-plane identities and fail-closed scope."""
import cmath
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_prime_fredholm import (
    build_report, prime_spectral_data, primes_up_to,
)


class PrimeFredholmTests(unittest.TestCase):
    def test_small_prime_sieve(self):
        self.assertEqual(primes_up_to(2), [2])
        self.assertEqual(primes_up_to(30), [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])

    def test_invalid_prime_bounds(self):
        for x in [0, 1, -2, 1.3, True, 100001]:
            with self.subTest(x=x), self.assertRaises(ValueError):
                primes_up_to(x)

    def test_reject_critical_strip(self):
        for sigma in [1, 0.5, 0, -1, float("nan"), float("inf")]:
            with self.subTest(sigma=sigma), self.assertRaises(ValueError):
                prime_spectral_data(sigma, 0.0, 101)

    def test_reject_bad_depth_or_height(self):
        for depth in [0, 51, 3.0, True]:
            with self.subTest(depth=depth), self.assertRaises(ValueError):
                prime_spectral_data(2.0, 0.0, 31, depth)
        with self.assertRaises(ValueError):
            prime_spectral_data(2.0, float("nan"), 31)

    def test_known_euler_product_real(self):
        result = prime_spectral_data(2.0, 0.0, 10000)
        product = result["finite_determinant"][0]
        exact_inverse_zeta2 = 6.0 / (math.pi * math.pi)
        self.assertGreaterEqual(product, exact_inverse_zeta2)
        self.assertLess(product - exact_inverse_zeta2, 0.0002)
        self.assertAlmostEqual(result["finite_determinant"][1], 0.0, places=13)

    def test_log_zeta_tail_is_bounded(self):
        for sigma in [1.1, 1.5, 2.0, 3.0]:
            for bound in [29, 97, 997]:
                with self.subTest(sigma=sigma, bound=bound):
                    x = prime_spectral_data(sigma, 0, bound)
                    y = prime_spectral_data(sigma, 0, 10000)
                    # -log(det) is the finite Euler log ζ.
                    observed = x["finite_log_determinant"][0] - y["finite_log_determinant"][0]
                    self.assertGreaterEqual(observed + 1e-12, 0)
                    self.assertLessEqual(observed, x["finite_log_zeta_real_axis_error_bound"] + 1e-12)

    def test_trace_powers_equal_prime_sum(self):
        bound = 29
        depth = 4
        result = prime_spectral_data(2.0, 0.0, bound, depth)
        for k, trace in enumerate(result["finite_power_traces"], 1):
            expected = sum(p ** (-2*k) for p in primes_up_to(bound))
            self.assertAlmostEqual(trace[0], expected, places=13)
            self.assertAlmostEqual(trace[1], 0.0, places=13)

    def test_complex_phase_finite_determinant(self):
        result = prime_spectral_data(1.8, 2.3, 97, 4)
        direct = 1+0j
        for p in primes_up_to(97):
            direct *= (1-cmath.exp(-complex(1.8, 2.3)*math.log(p)))
        reported = complex(*result["finite_determinant"])
        self.assertAlmostEqual(abs(reported-direct), 0, delta=1e-12)

    def test_prime_power_log_derivative(self):
        r = prime_spectral_data(2.0, 0, 97, 40)
        # Truncated expansion to k=40 is effectively converged here.
        d1 = r["logarithmic_derivative"][0]
        d2 = r["finite_prime_power_derivative"][0]
        self.assertAlmostEqual(d1, d2, places=12)

    def test_no_global_proof_promotion(self):
        report = build_report(2, 0, 101, 4)
        self.assertEqual(report["status"], "PROVED_HALF_PLANE_ONLY_GLOBAL_ZERO_CORRESPONDENCE_OPEN")
        self.assertEqual(report["operator_theorem"]["global_identity"], "NOT_DERIVED")
        self.assertFalse(any(report["assurance"].values()))

    def test_cli_roundtrip(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/"report.json"
            subprocess.run(
                [sys.executable, "-m", "mathos.research.riemann_prime_fredholm",
                 "--sigma", "2", "--height", "1.25", "--prime-bound", "211",
                 "--output", str(path)], check=True, capture_output=True, text=True,
            )
            output = json.loads(path.read_text(encoding="utf-8"))
            self.assertFalse(any(output["assurance"].values()))
            self.assertEqual(output["inputs"]["max_prime"], 211)


if __name__ == "__main__":
    unittest.main()
