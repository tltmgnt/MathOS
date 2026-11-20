"""Regression tests for the standalone educational zeta / TDA laboratory."""
from fractions import Fraction
import math
import unittest

from lab import (
    SQUARE, LINE,
    cycle_spectral_closed, cycle_spectral_zeta,
    cycle_ihara, cycle_ihara_adaptive,
    demo, rank_f2_bitvectors, rips_betti01,
)


class StandaloneCurriculumLabTests(unittest.TestCase):
    def test_known_cycle_spectral_special_values(self):
        self.assertEqual(cycle_spectral_closed(3, 1), Fraction(2, 3))
        self.assertEqual(cycle_spectral_closed(3, 2), Fraction(2, 9))
        self.assertEqual(cycle_spectral_closed(4, 1), Fraction(5, 4))
        self.assertEqual(cycle_spectral_closed(4, 2), Fraction(9, 16))
        for n in range(3, 23):
            for s in (1, 2):
                self.assertTrue(
                    math.isclose(cycle_spectral_zeta(n, s),
                                 float(cycle_spectral_closed(n, s)),
                                 rel_tol=1e-10),
                    (n, s),
                )

    def test_ihara_fixed_probe_distinguishes_and_adaptive_aliases(self):
        self.assertAlmostEqual(cycle_ihara(3, 0.5), 64 / 49)
        self.assertAlmostEqual(cycle_ihara(5, 0.5), 1024 / 961)
        self.assertNotAlmostEqual(cycle_ihara(3, 0.5), cycle_ihara(5, 0.5))
        for t in (0.5, 1.0, 2.0):
            expected = cycle_ihara_adaptive(t)
            for n in (3, 4, 5, 11, 29):
                self.assertTrue(
                    math.isclose(cycle_ihara(n, math.exp(-t / n)),
                                 expected, rel_tol=1e-11)
                )

    def test_binary_boundary_matrix_rank(self):
        self.assertEqual(rank_f2_bitvectors([]), 0)
        self.assertEqual(rank_f2_bitvectors([0, 0]), 0)
        self.assertEqual(rank_f2_bitvectors([0b011, 0b110, 0b101]), 2)
        self.assertEqual(rank_f2_bitvectors([1, 2, 4]), 3)

    def test_square_filtration_birth_and_filling_of_one_loop(self):
        far = rips_betti01(SQUARE, 0.9)
        self.assertEqual((far["vertices"], far["edges"], far["triangles"]), (4, 0, 0))
        self.assertEqual((far["betti_0"], far["betti_1"]), (4, 0))
        loop = rips_betti01(SQUARE, 1.0)
        self.assertEqual((loop["vertices"], loop["edges"], loop["triangles"]), (4, 4, 0))
        self.assertEqual((loop["rank_boundary_1"], loop["rank_boundary_2"]), (3, 0))
        self.assertEqual((loop["betti_0"], loop["betti_1"]), (1, 1))
        filled = rips_betti01(SQUARE, math.sqrt(2))
        self.assertEqual((filled["vertices"], filled["edges"], filled["triangles"]), (4, 6, 4))
        self.assertEqual((filled["rank_boundary_1"], filled["rank_boundary_2"]), (3, 3))
        self.assertEqual((filled["betti_0"], filled["betti_1"]), (1, 0))

    def test_line_control_has_no_loop(self):
        line = rips_betti01(LINE, 1.0)
        self.assertEqual((line["vertices"], line["edges"], line["triangles"]), (4, 3, 0))
        self.assertEqual((line["betti_0"], line["betti_1"]), (1, 0))

    def test_input_validation_prevents_accidental_misreadings(self):
        for n in (True, 2, 3.0, 10001):
            with self.assertRaises(ValueError):
                cycle_spectral_closed(n, 1)
        for s in (0, 3, True, 1.0):
            with self.assertRaises(ValueError):
                cycle_spectral_zeta(3, s)
        for u in (0, 1, -1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                cycle_ihara(3, u)
        for t in (0, -1, float("nan")):
            with self.assertRaises(ValueError):
                cycle_ihara_adaptive(t)
        for radius in (-1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                rips_betti01(SQUARE, radius)
        with self.assertRaises(ValueError):
            rips_betti01(((0, 0), (0, 0)), 1)
        with self.assertRaises(ValueError):
            rank_f2_bitvectors([-1])

    def test_demo_is_bounded_and_says_no_math_problem_was_solved(self):
        report = demo()
        self.assertEqual(len(report["graphs"]), 3)
        self.assertEqual(report["status"], "BOUNDED_EDUCATIONAL_DEMO_NOT_RH_PROOF")
        self.assertEqual(report["square_at_radius"]["betti_1"], 1)
        self.assertEqual(report["square_filled_at_sqrt2"]["betti_1"], 0)
        self.assertEqual(report["line_at_radius_one"]["betti_1"], 0)
        self.assertEqual(report["genuine_riemann_zero_count"], 0)
        for flag in ("rh_proved", "bsd_proved", "selmer_infinitude_proved"):
            self.assertIs(report[flag], False)


if __name__ == "__main__":
    unittest.main()
