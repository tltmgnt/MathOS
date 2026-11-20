"""Exact arithmetic, infinite congruence certificate and anti-overclaim guards."""
import unittest
from mathos.research.bsd_cubic_descent_07 import (
    D, cubic_coeffs, cubic_at_mod, cubic_discriminant_in_s,
    omega_exact, minkowski_ceiling_from_D, rank_bound, audit,
)


class BSDCubicDescent07(unittest.TestCase):
    def test_discriminant_symbolic_and_infinite_congruence_proof_inputs(self):
        self.assertEqual(
            cubic_discriminant_in_s(),
            (256*37,256*60,256*34,256*10,256)
        )
        # The proof is symbolic: for u=24k, 3|u, 8|u.
        # This finite regression is not the proof of an infinite statement.
        for u in (-48,-24,0,24,48):
            self.assertEqual(D(u)%8,5)
            self.assertEqual(D(u)%3,1)
            self.assertTrue(all(cubic_at_mod(cubic_coeffs(u),x,3)!=0
                                for x in range(3)))

    def test_exact_integer_arithmetic(self):
        self.assertEqual(D(0),37)
        self.assertEqual(D(24),131772276037)
        self.assertEqual(D(-24),94536886789)
        self.assertEqual(omega_exact(37),1)
        self.assertEqual(omega_exact(131772276037),1)
        self.assertEqual(omega_exact(94536886789),2)
        self.assertEqual(minkowski_ceiling_from_D(37),22)

    def test_parameter_dependent_bound_not_rank_certificate(self):
        for u in (-24,0,24):
            result = rank_bound(u)
            self.assertGreaterEqual(
                result['rank_bound_minkowski_proved_using_external_descent_theorems'],
                3
            )
            self.assertIs(result['uniform_rank_3_over_infinite_set_proved'],False)
            self.assertIs(result['rank_3_for_this_fiber_certified'],False)
            self.assertIs(result['bounded_constant_upper_rank_for_infinite_set_proved'],False)
            self.assertIs(result['BSD_proved'],False)
        self.assertEqual(
            rank_bound(0)['rank_bound_minkowski_proved_using_external_descent_theorems'],
            23
        )
        with self.assertRaises(ValueError):
            rank_bound(2)

    def test_epistemic_scope(self):
        report = audit(1)
        self.assertTrue(report['theorem_valid_for_all_k'])
        self.assertIs(report['external_cubic_descent_theorem_reproved_in_program'],False)
        self.assertIs(report['canonical_researchos_controller_executed'],False)
        self.assertEqual(report['canonical_TECT_state'],'UNVERIFIED')
        self.assertIs(report['uniform_rank_3_proved'],False)


if __name__ == '__main__':
    unittest.main()
