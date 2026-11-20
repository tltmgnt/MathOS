"""Bounded adversarial tests for Weil arithmetic Gram diagnostics and trust boundary."""
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_weil_gram import (
    PI, audit, digamma_real, fourier_h, l2_entry,
    symmetric_eigenvalues, weil_entry,
)


class WeilGramTests(unittest.TestCase):
    def test_digamma_quarter_exact_reference(self):
        euler_gamma = 0.5772156649015329
        expected = -euler_gamma - PI/2 - 3*math.log(2)
        self.assertAlmostEqual(digamma_real(0), expected, places=11)

    def test_gaussian_fourier_at_zero(self):
        for a in [0.02, 0.05]:
            self.assertAlmostEqual(fourier_h(0, 0, 0, a), math.sqrt(PI/a), places=12)

    def test_gaussian_fourier_symmetry(self):
        for u in [0.0, 0.8, 2.0]:
            x = fourier_h(u, 0.2, 0.5, 0.02)
            self.assertAlmostEqual(x, fourier_h(-u, 0.2, 0.5, 0.02))
            self.assertAlmostEqual(x, fourier_h(u, 0.5, 0.2, 0.02))

    def test_L2_psd_analytic_comparison(self):
        centers = (0.0, 0.2, 0.5)
        matrix = [[l2_entry(c,d,0.02) for d in centers] for c in centers]
        self.assertGreaterEqual(min(symmetric_eigenvalues(matrix)), -1e-9)

    def test_indefinite_matrix_rejected_by_eigen_diagnostic(self):
        # The eigenvalue routine must not silently claim every symmetric form is PSD.
        self.assertEqual(symmetric_eigenvalues([[1.0, 2.0], [2.0, 1.0]]), [-1.0, 3.0])

    def test_off_diagonal_weil_entry_symmetry(self):
        a=weil_entry(0.2, 0.5, 0.02, 45.0, 2048, 256)
        b=weil_entry(0.5, 0.2, 0.02, 45.0, 2048, 256)
        self.assertAlmostEqual(a["total_approx"], b["total_approx"], places=10)

    def test_prime_and_archimedean_terms_present(self):
        item=weil_entry(0.0, 0.0, 0.02, 45, 2048, 256)
        self.assertGreater(item["pole"], 0)
        self.assertLess(item["finite_prime_power_term"], 0)
        self.assertTrue(math.isfinite(item["archimedean_approx"]))
        self.assertAlmostEqual(item["total_approx"], 0.03708258, delta=3e-5)

    def test_default_finite_matrix_numerically_positive_not_certified(self):
        out=audit(panels=2048, prime_bound=256)
        self.assertEqual(len(out["finite_Weil_Gram"]["matrix"]),3)
        self.assertGreater(out["finite_Weil_Gram"]["approx_min_eigenvalue"], 0)
        self.assertFalse(out["finite_Weil_Gram"]["claim_of_global_psd"])
        self.assertFalse(out["numerics"]["all_tail_and_roundoff_errors_rigorously_enclosed"])
        self.assertFalse(any(out["assurance"].values()))

    def test_prime_cutoff_stability_is_not_proof(self):
        a=weil_entry(0.0,0.2,0.02,45,2048,256)["total_approx"]
        b=weil_entry(0.0,0.2,0.02,45,2048,512)["total_approx"]
        self.assertLess(abs(a-b),1e-8)

    def test_numerical_refinement(self):
        a=weil_entry(0.2,0.5,0.02,45,2048,256)["total_approx"]
        b=weil_entry(0.2,0.5,0.02,45,4096,256)["total_approx"]
        self.assertLess(abs(a-b),1e-8)

    def test_input_guards(self):
        for centers in [(),(-1.0,),(2.0,),tuple(range(7))]:
            with self.subTest(centers=centers),self.assertRaises(ValueError):
                audit(centers,panels=2048)
        for a in [0.0, -1, 0.2, float("nan")]:
            with self.subTest(a=a),self.assertRaises(ValueError):
                audit(a=a,panels=2048)
        with self.assertRaises(ValueError):
            audit(panels=2049)
        with self.assertRaises(ValueError):
            audit(prime_bound=12)
        with self.assertRaises(ValueError):
            digamma_real(float("nan"))

    def test_small_dimension_is_not_hilbert_completion(self):
        out=audit((0.0,),panels=2048,prime_bound=256)
        self.assertFalse(out["conditional_Hilbert_space"]["global_positivity_proved"])
        self.assertFalse(out["conditional_Hilbert_space"]["self_adjoint_zeta_operator_constructed"])
        self.assertFalse(out["independent_positive_L2_comparison"]["is_the_Weil_form"])

    def test_cli_generated_report(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/"weil.json"
            subprocess.run([
                sys.executable,"-m","mathos.research.riemann_weil_gram",
                "--panels","2048","--prime-bound","256",
                "--output",str(target)
            ],check=True,capture_output=True,text=True)
            r=json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(r["status"],"FINITE_UNCERTIFIED_WEIL_FORM_TEST_NOT_RH")
            self.assertFalse(r["assurance"]["riemann_hypothesis_proved"])
            self.assertFalse(r["numerics"]["can_certify_Weil_psd"])


if __name__ == "__main__":
    unittest.main()
