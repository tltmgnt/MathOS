"""Adversarial exact rational gap, L2 conditioning, and prime-19 tests."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_weil_lattice_topology_audit import (
    WIDTH, STEP, FIFTH_PRIME_POWERS, atanh_positive_bounds,
    rational_log_integer, prime_power_base, translated_support,
    convolution_support, prime_inventory, fifth_prime19_lower, report,
)


class TECTXLatticeTopologyAuditTests(unittest.TestCase):
    def test_infinite_lattice_support_gap_is_exact(self):
        self.assertEqual(STEP,Fraction(3,4))
        self.assertEqual(WIDTH,Fraction(1,8))
        self.assertEqual(translated_support(0),(-Fraction(1,8),Fraction(1,8)))
        self.assertEqual(translated_support(1),(Fraction(5,8),Fraction(7,8)))
        self.assertEqual(translated_support(4),(Fraction(23,8),Fraction(25,8)))

    def test_disjoint_supports_at_arbitrary_indices(self):
        for i in (0,1,3,10,1000):
            a,b=translated_support(i)
            c,d=translated_support(i+1)
            self.assertLess(b,c)
            self.assertEqual(c-b,Fraction(1,2))

    def test_L2_reference_is_dimension_independent_and_full_domain_non_dense(self):
        r=report()["lattice"]
        self.assertEqual(r["ordinary_L2_reference_Gram"],"alpha * I_m for EVERY m, no off-diagonal overlaps")
        self.assertEqual(r["all_m_coefficient_to_L2_condition_number"],1)
        self.assertEqual(Fraction(r["alpha_strict_lower"]),Fraction(1,18))
        self.assertEqual(Fraction(r["alpha_strict_upper"]),Fraction(1,4))
        self.assertFalse(r["span_dense_in_L2_R"])
        self.assertFalse(r["span_dense_in_LF_Cc_infinity_R"])
        self.assertTrue(r["every_f_j_identically_zero_on_gap"])

    def test_exact_rational_log2_bracket_and_window(self):
        a,b=rational_log_integer(2)
        self.assertLess(Fraction(69,100),a)
        self.assertLess(b,Fraction(70,100))
        self.assertIsInstance(a,Fraction)
        self.assertIsInstance(b,Fraction)

    def test_rational_log_endpoints_for_fifth_window(self):
        a,b=rational_log_integer(15)
        c,d=rational_log_integer(16)
        e,f=rational_log_integer(25)
        g,h=rational_log_integer(26)
        self.assertLess(b,Fraction(11,4))
        self.assertGreater(c,Fraction(11,4))
        self.assertLess(f,Fraction(13,4))
        self.assertGreater(g,Fraction(13,4))
        self.assertLess(a,b)
        self.assertLess(g,h)

    def test_prime_power_exact_factorization(self):
        expected={16:2,17:17,19:19,23:23,25:5}
        for n in range(16,26):
            self.assertEqual(prime_power_base(n),expected.get(n))
        for n in (1,0,-2):
            self.assertIsNone(prime_power_base(n))

    def test_fifth_prime_window_exact_complete(self):
        p=prime_inventory(4,0)
        self.assertEqual(p["support"],["11/4","13/4"])
        self.assertEqual([v["integer"] for v in p["candidate_prime_powers"]],list(FIFTH_PRIME_POWERS))
        self.assertEqual([v["von_mangoldt_base"] for v in p["candidate_prime_powers"]],
                         [2,17,19,23,5])

    def test_neighboring_windows_remain_consistent(self):
        self.assertEqual([v["integer"] for v in prime_inventory(1,0)["candidate_prime_powers"]],[2])
        self.assertEqual([v["integer"] for v in prime_inventory(2,0)["candidate_prime_powers"]],[4,5])
        self.assertEqual([v["integer"] for v in prime_inventory(3,0)["candidate_prime_powers"]],[8,9,11])

    def test_nonzero_prime19_strict_rational_bound(self):
        p=fifth_prime19_lower()
        self.assertEqual(p["convolution_at_log19_strictly_greater"],"1/72")
        self.assertEqual(p["prime19_term_strictly_less"],"-49/6000")
        self.assertTrue(p["prime19_contribution_nonzero"])

    def test_bilateral_supports_reflect_without_changing_integer_inventory(self):
        pos=convolution_support(4,0)
        neg=convolution_support(0,4)
        self.assertEqual(neg,(-pos[1],-pos[0]))
        self.assertEqual([v["integer"] for v in prime_inventory(4,0)["candidate_prime_powers"]],
                         [v["integer"] for v in prime_inventory(0,4)["candidate_prime_powers"]])

    def test_rational_log_monotonic_and_shrinking_intervals(self):
        for n in (3,11,19,26):
            a,b=rational_log_integer(n,8)
            c,d=rational_log_integer(n,16)
            self.assertLessEqual(a,c)
            self.assertLessEqual(d,b)
            self.assertLess(d-c,b-a)

    def test_invalid_inputs_fail_closed(self):
        for n in (0,-1,2.0,True):
            with self.subTest(n=n),self.assertRaises(ValueError):
                rational_log_integer(n)
        for t in (Fraction(-1,4),Fraction(1,2),0.2):
            with self.subTest(t=t),self.assertRaises(ValueError):
                atanh_positive_bounds(t)
        with self.assertRaises(ValueError):
            translated_support(-1)

    def test_missing_fifth_schur_and_global_theorem_are_explicit(self):
        r=report()
        self.assertFalse(r["fifth_direction"]["all_pole_arch_prime_terms_fully_enclosed"])
        self.assertFalse(r["fifth_direction"]["fifth_Weil_Gram_eigenvalues_certified"])
        self.assertFalse(r["fifth_direction"]["fifth_Schur_complement_certified"])
        self.assertFalse(any(r["assurance"].values()))

    def test_cli_json_contains_exact_rational_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"fifth.json"
            subprocess.run([sys.executable,"-m",
                            "mathos.research.riemann_weil_lattice_topology_audit",
                            "--output",str(output)],
                           check=True,capture_output=True,text=True)
            data=json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["schema"],"mathos_tectx_weil_lattice_topology_fifth_prime_audit/1")
            self.assertEqual(data["fifth_direction"]["actual_new_prime_powers"],[16,17,19,23,25])
            self.assertFalse(data["assurance"]["Riemann_hypothesis_proved"])


if __name__=="__main__":
    unittest.main()
