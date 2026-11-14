"""Regression checks for exact nonlinear Navier--Stokes and 3-CNF proofs."""
import copy
import unittest

from mathos.research.millennium_attacks_002 import (
    abc_identities, abc_modes, brute_force_3cnf_unsat, convection, curl,
    divergence, gradient, half_squared_speed, laplacian,
    lift_parity_cycle_3cnf, negative_vector, research_report,
    resolution_refutation, verify_resolution_refutation,
)


class ExactNonlinearNavierStokesTests(unittest.TestCase):
    def test_abc_field_has_expected_modes_and_nonconstant_pressure(self):
        field = abc_modes()
        self.assertEqual(len(field), 6)
        self.assertEqual(field[(0, 0, 1)][0], -0.5j)
        self.assertEqual(field[(0, 1, 0)][0], 0.5)
        self.assertEqual(field[(1, 0, 0)][1], -0.5j)
        self.assertEqual(field[(0, 0, -1)][1], 0.5)
        self.assertEqual(field[(0, 1, 0)][2], -0.5j)
        self.assertEqual(field[(1, 0, 0)][2], 0.5)
        self.assertTrue(convection(field))
        self.assertTrue(gradient(half_squared_speed(field)))

    def test_exact_fourier_equations_hold(self):
        field = abc_modes()
        self.assertFalse(divergence(field))
        self.assertEqual(curl(field), field)
        self.assertEqual(laplacian(field), negative_vector(field))
        self.assertEqual(convection(field), gradient(half_squared_speed(field)))

    def test_exact_nontrivial_nonlinear_residual_and_energy(self):
        check = abc_identities()
        self.assertTrue(check["divergence_zero"])
        self.assertTrue(check["curl_equals_velocity"])
        self.assertTrue(check["laplacian_equals_negative_velocity"])
        self.assertTrue(check["convection_equals_pressure_gradient_cancelled"])
        self.assertTrue(check["convection_nonzero"])
        self.assertEqual(check["mean_squared_speed"], 3.0)
        self.assertEqual(check["nonlinear_modes"], 12)


class Resolution3SatTests(unittest.TestCase):
    def test_exactly_three_literals_and_both_signs(self):
        for n in (3, 4, 6, 8, 12):
            with self.subTest(n=n):
                clauses = lift_parity_cycle_3cnf(n)
                self.assertEqual(len(clauses), 4 * n)
                self.assertTrue(all(len(c) == 3 for c in clauses))
                signs = {literal for c in clauses for literal in c}
                self.assertEqual(signs, {sign * i for i in range(1, 3*n+1)
                                         for sign in (-1, 1)})
                self.assertFalse(any(len(c) == 1 for c in clauses))
                self.assertTrue(all(set(c).isdisjoint({-lit for lit in c})
                                    for c in clauses))

    def test_resolution_certificate_length_and_empty_clause(self):
        for n in (3, 4, 6, 8, 12, 20):
            with self.subTest(n=n):
                proof = resolution_refutation(n)
                self.assertEqual(proof['total_variables'], 3 * n)
                self.assertEqual(len(proof['initial_clauses']), 4 * n)
                self.assertEqual(len(proof['steps']), 4 * n - 1)
                self.assertTrue(verify_resolution_refutation(proof))
                self.assertEqual(proof['steps'][-1]['clause'], [])

    def test_corrupted_certificate_is_rejected(self):
        proof = resolution_refutation(4)
        for corruption in ("wrong_literal", "bad_pivot", "future_parent", "not_empty"):
            p = copy.deepcopy(proof)
            if corruption == "wrong_literal":
                p['steps'][0]['clause'] = [123]
            elif corruption == "bad_pivot":
                p['steps'][0]['pivot'] = 99
            elif corruption == "future_parent":
                p['steps'][0]['left'] = 1000
            else:
                p['steps'][-1]['clause'] = [1]
            with self.subTest(corruption=corruption):
                self.assertFalse(verify_resolution_refutation(p))

    def test_exhaustive_satisfiability_baseline(self):
        for n in (3, 4):
            self.assertTrue(brute_force_3cnf_unsat(n))

    def test_pointwise_lifting_equivalence(self):
        from itertools import product
        from mathos.research.millennium_attacks_001 import parity_cycle_2cnf
        n = 3
        original = parity_cycle_2cnf(n)
        lifted = lift_parity_cycle_3cnf(n)
        for assignment in product((False, True), repeat=3*n):
            truth_old = all(any(assignment[abs(lit)-1] == (lit>0)
                                    for lit in clause) for clause in original)
            truth_new = all(any(assignment[abs(lit)-1] == (lit>0)
                                    for lit in clause) for clause in lifted)
            self.assertEqual(truth_old, truth_new)


class ResearchScopeTests(unittest.TestCase):
    def test_report_has_noncertification_and_scope(self):
        report = research_report()
        self.assertEqual(report['certification'], 'NOT_CERTIFIED')
        self.assertIn('torus', report['navier_stokes']['domain'])
        self.assertIn('not_proved', report['navier_stokes'])
        self.assertIn('not_proved', report['p_vs_np'])
        self.assertTrue(report['p_vs_np']['no_lower_bound_claim'])
        self.assertTrue(all(x['refutation_verified'] for x in report['p_vs_np']['proofs']))


if __name__ == '__main__':
    unittest.main()
