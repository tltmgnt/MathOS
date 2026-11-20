"""Exact-rational all-index signed bounds and canonical Weil topology safeguards."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_weil_all_index_bridge import (
    M, CERTIFIED_PREFIX, HEAD_SQUARE_WEIGHT, TAIL_SQUARE_WEIGHT,
    SHARP_TAIL_SQRT_RATIONAL, PREFIX3_LOWER,
    all_index_lower, certified_prefix3_all_index_lower,
    generic_positive_prefix_tail_bound, enumerate_compact_bumps, report,
)


class WeilAllIndexBridgeTests(unittest.TestCase):
    def test_unconditional_all_dimension_lower_exact(self):
        for m in (0,1,2,3,4,16,32,64,1024):
            self.assertEqual(all_index_lower(m),
                             -Fraction(M,3)*(1-Fraction(1,4**m)))

    def test_unconditional_floor_is_negative_not_psd(self):
        self.assertEqual(all_index_lower(0),0)
        for m in (1,2,3,64):
            self.assertLess(all_index_lower(m),0)
        self.assertGreater(all_index_lower(32),-Fraction(M,3))

    def test_certified_3d_prefix_improves_every_later_lower_floor(self):
        self.assertEqual(PREFIX3_LOWER,-Fraction(1875,4))
        self.assertLessEqual(HEAD_SQUARE_WEIGHT*TAIL_SQUARE_WEIGHT,
                             SHARP_TAIL_SQRT_RATIONAL**2)
        self.assertEqual(HEAD_SQUARE_WEIGHT,Fraction(21,64))
        self.assertEqual(TAIL_SQUARE_WEIGHT,Fraction(1,192))
        for m in (3,4,8,100,4096):
            self.assertEqual(certified_prefix3_all_index_lower(m),
                             -Fraction(1875,4))

    def test_conditional_prefix_sequence_tends_towards_zero(self):
        for k in (1,2,3,4,16,32):
            self.assertLess(generic_positive_prefix_tail_bound(k),0)
            self.assertGreater(generic_positive_prefix_tail_bound(k+1),
                               generic_positive_prefix_tail_bound(k))
        self.assertEqual(generic_positive_prefix_tail_bound(3),
                         -Fraction(10000,3)*(Fraction(1,8)+Fraction(1,64)))

    def test_growing_dimension_does_not_turn_fixed_prefix_floor_positive(self):
        a=report(3)
        b=report(256)
        self.assertEqual(
            a["existing_signed_operator"]["given_prefix3_bound_for_all_m_ge_3"],
            b["existing_signed_operator"]["given_prefix3_bound_for_all_m_ge_3"])
        self.assertFalse(b["existing_signed_operator"]["nonnegative_floor_for_all_dimensions_proved"])

    def test_invalid_indices_rejected(self):
        for value in (-1,4097,True,1.5):
            with self.subTest(value=value),self.assertRaises(ValueError):
                all_index_lower(value)
            with self.subTest(value=value),self.assertRaises(ValueError):
                generic_positive_prefix_tail_bound(value)
        for value in (0,1,2,4097,True,3.0):
            with self.subTest(value=value),self.assertRaises(ValueError):
                certified_prefix3_all_index_lower(value)

    def test_canonical_bump_family_is_explicit_and_compactly_supported(self):
        bumps=enumerate_compact_bumps(100)
        self.assertEqual(len(bumps),100)
        ids={(b["n"],b["center"]) for b in bumps}
        self.assertEqual(len(ids),100)
        self.assertIn((1,"0/1"),ids)
        self.assertIn((1,"1/1"),ids)
        self.assertIn((1,"-1/1"),ids)
        for item in bumps:
            left=Fraction(item["support_left"])
            middle=Fraction(item["center"])
            right=Fraction(item["support_right"])
            h=Fraction(item["half_support_width"])
            self.assertEqual(right-left,2*h)
            self.assertEqual(middle-left,h)
            self.assertEqual(right-middle,h)

    def test_bump_enumeration_rejects_invalid_counts(self):
        for value in (-1,0,301,True,1.5):
            with self.subTest(value=value),self.assertRaises(ValueError):
                enumerate_compact_bumps(value)

    def test_true_weil_domain_distinct_from_gaussian_l2_density(self):
        r=report(8,8)
        space=r["canonical_weil_domain"]
        self.assertTrue(space["span_dense_in_D_LF_topology"])
        self.assertTrue(space["W_continuous_on_D"])
        self.assertTrue(space["Weil_Hermitian_form_jointly_continuous_on_each_fixed_support_D_K"])
        self.assertFalse(space["all_finite_bump_Gram_psd_proved"])
        self.assertFalse(space["Weil_RH_equivalence_proved_by_this_software"])
        gaussian=r["gaussian_vs_compact_bump"]
        self.assertFalse(gaussian["prior_family_inside_Cc_infinity_log_coordinate"])
        self.assertFalse(gaussian["prior_L2_density_entails_D_density"])

    def test_continuity_and_density_do_not_establish_rh(self):
        r=report(32,24)
        self.assertFalse(any(r["assurance"].values()))
        self.assertFalse(r["existing_signed_operator"]["fixed_prefix_bounds_tend_to_zero_as_m_grows"])
        self.assertEqual(len(r["canonical_weil_domain"]["sample_bumps"]),24)

    def test_all_index_report_4096(self):
        r=report(4096,1)
        self.assertEqual(r["existing_signed_operator"]["dimension"],4096)
        self.assertEqual(r["existing_signed_operator"]["given_prefix3_bound_for_all_m_ge_3"],"-1875/4")

    def test_cli_portable_exact_rational_bound_and_rh_flags(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"topology.json"
            subprocess.run([
                sys.executable,"-m","mathos.research.riemann_weil_all_index_bridge",
                "--dimension","32","--bump-count","24","--output",str(path)
            ],check=True,capture_output=True,text=True)
            r=json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(r["schema"],"mathos_tectx_weil_all_index_test_topology_bridge/1")
            self.assertEqual(Fraction(r["existing_signed_operator"]["unconditional_all_index_lower"]),
                             all_index_lower(32))
            self.assertFalse(any(r["assurance"].values()))


if __name__=="__main__":
    unittest.main()
