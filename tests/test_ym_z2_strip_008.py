"""Exact tests for the finite 2D Z2 gauge strip: NOT a 4D YM mass gap."""
import itertools
import unittest
from fractions import Fraction

from mathos.research.ym_z2_strip_008 import (
    audit, boundary_parity, closed_form, edge_count, exhaustive_strip,
    gauge_transform, plaquette_parities, scaling_row,
)


class YMZ2Strip008Tests(unittest.TestCase):
    def test_single_plaquette_has_equal_even_and_odd_wilson_signs(self):
        counts = {0: 0, 1: 0}
        for edges in itertools.product((0, 1), repeat=4):
            parity, = plaquette_parities(1, edges)
            counts[parity] += 1
            self.assertEqual(boundary_parity(1, edges), parity)
        self.assertEqual(counts, {0: 8, 1: 8})

    def test_all_vertex_gauge_transformations_preserve_plaquettes(self):
        for n in (0, 1, 2, 3):
            for edges in itertools.product((0, 1), repeat=edge_count(n)):
                original = plaquette_parities(n, edges)
                wilson = boundary_parity(n, edges)
                for vertex in range(n+1):
                    for row in (0, 1):
                        transformed = gauge_transform(n, edges, row, vertex)
                        self.assertEqual(plaquette_parities(n, transformed), original)
                        self.assertEqual(boundary_parity(n, transformed), wilson)
                        self.assertEqual(
                            gauge_transform(n, transformed, row, vertex), edges,
                        )

    def test_exact_independent_enumeration_and_closed_form(self):
        for n in range(6):
            for t in (1, 2, 5):
                with self.subTest(n=n, t=t):
                    report = exhaustive_strip(n, t, verify_gauge=False)
                    expected = closed_form(n, t)
                    self.assertEqual(report["configurations_checked"], 2**(3*n+1))
                    self.assertEqual(report["distinct_plaquette_parity_words"], 2**n)
                    self.assertEqual(report["per_parity_fiber"], 2**(2*n+1))
                    self.assertEqual(report["partition"], expected["partition"])
                    self.assertEqual(report["wilson_numerator"], expected["boundary_wilson_numerator"])
                    self.assertEqual(report["expectation"], expected["boundary_wilson_expectation"])
                    self.assertEqual(
                        Fraction(**report["expectation"]),
                        Fraction(t-1, t+1)**n,
                    )

    def test_boundary_telescope_is_independent_of_interior_vertical_links(self):
        n = 4
        for top_bottom in itertools.product((0, 1), repeat=2*n):
            for initial_last in itertools.product((0, 1), repeat=2):
                initial, last = initial_last
                measurements = set()
                for internal in itertools.product((0, 1), repeat=n-1):
                    edges = top_bottom + (initial,) + internal + (last,)
                    measurements.add(boundary_parity(n, edges))
                    self.assertEqual(
                        sum(plaquette_parities(n, edges)) % 2,
                        boundary_parity(n, edges),
                    )
                self.assertEqual(len(measurements), 1)

    def test_rational_scaling_sequence_has_no_uniform_decay_rate(self):
        for k in (1, 2, 3, 4, 5, 8, 16, 32, 64):
            with self.subTest(k=k):
                row = scaling_row(k)
                q = Fraction(**row["single_step_q"])
                self.assertEqual(q, Fraction(k*k, k*k+2))
                self.assertGreater(q, 0)
                self.assertLess(q, 1)
                self.assertEqual(
                    Fraction(**row["unit_distance_wilson_factor"]), q**k,
                )
                self.assertLessEqual(
                    1-q**k, Fraction(2, k),
                )
                self.assertTrue(row["rational_inequality_verified"])

    def test_report_never_promotes_2d_abelian_toy_to_yang_mills_prize(self):
        report = audit(5, 16)
        self.assertEqual(report["status"], "EXACT_TWO_DIMENSIONAL_Z2_TOY_AUDIT_ONLY")
        self.assertTrue(report["finite_abelian_not_compact_simple"])
        self.assertEqual(len(report["cases"]), 18)
        self.assertEqual(report["total_link_configurations_checked"], 224694)
        for flag in (
            "proves_4d_yang_mills_exists",
            "constructs_continuum_qft",
            "constructs_physical_hilbert_space",
            "establishes_positive_physical_spectral_gap",
            "independent_external_review_completed",
            "novel_mathematics_claimed",
        ):
            self.assertFalse(report[flag])

    def test_invalid_inputs_rejected_strictly(self):
        invalid_bits = (
            (True, 0, 0, 0), (2, 0, 0, 0), (0,), "0000", None,
        )
        for bad in invalid_bits:
            with self.subTest(edges=bad):
                with self.assertRaises(ValueError):
                    plaquette_parities(1, bad)
        for n in (-1, True, 1.2, "2"):
            with self.subTest(n=n):
                with self.assertRaises(ValueError):
                    edge_count(n)
        with self.assertRaises(ValueError):
            gauge_transform(1, (0, 0, 0, 0), 2, 0)
        with self.assertRaises(ValueError):
            gauge_transform(1, (0, 0, 0, 0), 0, 2)
        for n, t in ((6, 2), (1, 10), (1, 0), (True, 2)):
            with self.subTest(n=n, t=t):
                with self.assertRaises(ValueError):
                    exhaustive_strip(n, t)
        for k in (0, -1, True, "3", 2.5):
            with self.subTest(k=k):
                with self.assertRaises(ValueError):
                    scaling_row(k)
        with self.assertRaises(ValueError):
            audit(6, 16)
        with self.assertRaises(ValueError):
            audit(5, 65)


if __name__ == "__main__":
    unittest.main()
