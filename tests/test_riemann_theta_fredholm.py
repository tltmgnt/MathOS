"""Adversarial tests for entire theta-derived Fredholm determinant representation."""
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_theta_fredholm import (
    FIRST_ZERO_HEIGHT, audit, determinant_approx, theta_tail, u_kernel,
)


class ThetaFredholmTests(unittest.TestCase):
    def test_theta_tail_at_one(self):
        a = theta_tail(1, 8)
        self.assertGreater(a, math.exp(-math.pi))
        self.assertLess(a, 0.05)
        self.assertAlmostEqual(a, theta_tail(1, 20), places=14)

    def test_removable_endpoint_poles(self):
        self.assertAlmostEqual(determinant_approx(0).real, 0.5, places=14)
        self.assertAlmostEqual(determinant_approx(1).real, 0.5, places=14)

    def test_gamma_normalization_xi_at_two(self):
        # xi(2)=(2*1/2)*pi^-1 Gamma(1) zeta(2)=pi/6.
        value = determinant_approx(2)
        self.assertAlmostEqual(value.real, math.pi/6, delta=2e-9)
        self.assertAlmostEqual(value.imag, 0, places=12)

    def test_functional_equation_numeric(self):
        for s in [.5+4j, .7+2j, -2+1j, 2+0j]:
            with self.subTest(s=s):
                self.assertLess(abs(determinant_approx(s)-determinant_approx(1-s)), 1e-9)

    def test_family_itself_respects_reflection(self):
        for x in [1, 1.5, 3, 6]:
            with self.subTest(x=x):
                self.assertLess(abs(u_kernel(.7+2j, x)-u_kernel(.3-2j, x)), 1e-12)

    def test_known_zero_is_only_a_numeric_diagnostic(self):
        result = determinant_approx(.5 + FIRST_ZERO_HEIGHT*1j)
        self.assertLess(abs(result), 1e-6)
        self.assertGreaterEqual(abs(result), 0)

    def test_noncritical_complex_parameters_are_finite(self):
        for s in [.7+2j, .25+7j, .8+FIRST_ZERO_HEIGHT*1j]:
            out = determinant_approx(s)
            self.assertTrue(math.isfinite(out.real))
            self.assertTrue(math.isfinite(out.imag))

    def test_quadrature_refinement(self):
        a = determinant_approx(.7+2j, panels=2048)
        b = determinant_approx(.7+2j, panels=4096)
        self.assertLess(abs(a-b), 2e-9)

    def test_reject_bad_parameters(self):
        for s in [complex(float("nan"),0), 40j, 8]:
            with self.subTest(s=s), self.assertRaises(ValueError):
                determinant_approx(s)
        for panels in [1, 511, 513, 40000, 512.0]:
            with self.subTest(panels=panels), self.assertRaises(ValueError):
                determinant_approx(0.5, panels=panels)
        with self.assertRaises(ValueError):
            theta_tail(0.9)
        with self.assertRaises(ValueError):
            determinant_approx(.5, xmax=3)

    def test_entire_rank_one_but_not_self_adjoint_hilbert_polya(self):
        report = audit(2048)
        operator = report["operator"]
        self.assertTrue(operator["zero_correspondence_is_from_preexisting_xi_identity"])
        self.assertFalse(operator["is_fixed_self_adjoint_operator"])
        self.assertFalse(operator["is_hilbert_polya_spectral_realization"])
        self.assertFalse(any(report["assurance"].values()))
        self.assertFalse(report["computation"]["numerical_zero_certification"])

    def test_cli_report(self):
        with tempfile.TemporaryDirectory() as directory:
            outfile = Path(directory)/"xi.json"
            subprocess.run(
                [sys.executable, "-m", "mathos.research.riemann_theta_fredholm",
                 "--panels", "2048", "--xmax", "12", "--output", str(outfile)],
                check=True, capture_output=True, text=True,
            )
            result = json.loads(outfile.read_text(encoding="utf-8"))
            self.assertEqual(result["schema"], "mathos_tectx_theta_fredholm_xi/1")
            self.assertEqual(len(result["computation"]["samples"]), 7)
            self.assertFalse(result["assurance"]["rh_proved"])


if __name__ == "__main__":
    unittest.main()
