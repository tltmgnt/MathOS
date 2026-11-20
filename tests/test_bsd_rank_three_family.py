"""Exact symbolic algebra and no-proof-promotion checks for milestone 03."""
import unittest
from mathos.research.bsd_rank_three_family import (
    audit, invariants, evaluate, section_identity_twice, power
)


class BSDRankThreeFamilyTests(unittest.TestCase):
    def test_symbolic_invariants_and_smoothness_certificate(self):
        c4, delta = invariants()
        self.assertEqual(c4, (48, 24, 28, 8, 4))
        self.assertEqual(delta, (37, 60, 94, 78, 65, 34, 16, 4, 1))
        self.assertEqual(evaluate(delta, 2), 5077)
        self.assertEqual(evaluate(delta, -3), 5077)
        self.assertEqual(evaluate(delta, 1), 389)
        self.assertEqual(evaluate(delta, -2), 389)
        self.assertEqual(len(power(c4, 3))-1, 12)
        self.assertEqual(len(delta)-1, 8)

    def test_three_rational_sections_are_exact_identities(self):
        self.assertEqual(section_identity_twice((0,), (0,)), (0,))
        self.assertEqual(section_identity_twice((1,), (0,)), (0,))
        self.assertEqual(section_identity_twice((-1,), (0, 1)), (0,))
        self.assertNotEqual(section_identity_twice((-2,), (0, 1)), (0,))

    def test_nonpromotion(self):
        report = audit()
        self.assertTrue(report['three_sections_verified_as_polynomial_identities'])
        self.assertTrue(report['discriminant_positive_identity_verified'])
        for key in (
            'rank_three_generators_independently_proved_by_script',
            'Silverman_specialization_theorem_proved_by_script',
            'analytic_L_values_calculated',
            'effective_exceptional_set_computed',
            'exact_generic_rank_proved',
            'analytic_rank_exact_equality_for_infinite_family_proved',
            'mathematical_novelty_established',
            'BSD_proved',
        ):
            self.assertIs(report[key], False)


if __name__ == '__main__':
    unittest.main()
