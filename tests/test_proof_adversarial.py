from dataclasses import replace
from fractions import Fraction
import unittest
from mathos.proof_analysis.adversarial_analysis import (ATTACKS, ZERO, add, mul, gaussian_derivative,
    gaussian_field, ns_attack, rh_attack, sat_polynomial, sat_attack, rank,
    bsd_attack, hodge_attack, a5_certificate, poincare_attack, ym_attack,
    route_statuses, complex_mul)


class AdversarialTests(unittest.TestCase):
    def test_gaussian_derivative_constant(self):
        self.assertEqual(gaussian_derivative({ZERO: 1}, 0), {(1,0,0): -2})

    def test_gaussian_derivative_linear(self):
        self.assertEqual(gaussian_derivative({(1,0,0): 1}, 0), {ZERO:1, (2,0,0):-2})

    def test_ns_divergence_zero(self):
        self.assertEqual(gaussian_field()[1], {})

    def test_ns_curl_coefficients(self):
        self.assertEqual(gaussian_field()[2], [{(1,0,1):-4}, {(0,1,1):-4},
                         {ZERO:-4, (2,0,0):4, (0,2,0):4}])

    def test_ns_helicity_density_zero(self):
        self.assertEqual(gaussian_field()[3], {})

    def test_ns_arbitrarily_large_origin_vorticity(self):
        rows=ns_attack().witness['scale_examples']
        self.assertEqual([r['absolute_vorticity_at_origin'] for r in rows], [4,16,400,40000])
        self.assertEqual({r['helicity'] for r in rows}, {0})

    def test_complex_multiplication(self):
        self.assertEqual(complex_mul((0,1),(0,1)),(-1,0))

    def test_rh_exact_root_square(self):
        self.assertEqual(rh_attack().witness['root_squared'], ['0','1'])
        self.assertEqual(rh_attack().witness['root_fourth'], ['-1','0'])

    def test_sat_empty_product(self):
        self.assertEqual(sat_polynomial(0), {frozenset():1})

    def test_sat_boolean_truth(self):
        # All 64 assignments for three clauses, evaluated independently.
        poly=sat_polynomial(3)
        for bits in range(64):
            value=sum(c for variables,c in poly.items() if all(bits & (1<<v) for v in variables))
            expected=int(all((bits & (1<<(2*i))) or (bits & (1<<(2*i+1))) for i in range(3)))
            self.assertEqual(value,expected)

    def test_sat_counts(self):
        self.assertEqual(sat_attack().witness['counts_m_0_to_8'], [3**m for m in range(9)])

    def test_sat_resource_limit(self):
        for m in [-1,11,1.5]:
            with self.assertRaises(ValueError): sat_polynomial(m)

    def test_rank_exact_rationals(self):
        self.assertEqual(rank([[Fraction(1,3),Fraction(2,3)],[1,2]]),1)

    def test_rank_row_swap(self):
        self.assertEqual(rank([[0,1],[1,0]]),2)

    def test_rank_ragged_rejected(self):
        with self.assertRaises(ValueError): rank([[1],[1,2]])

    def test_bsd_nondegeneracy_dimensions(self):
        self.assertEqual(bsd_attack().witness['nondegenerate_alternating_form_dimensions'],[2,4,8])

    def test_hodge_image_is_proper(self):
        w=hodge_attack().witness
        self.assertLess(w['declared_cycle_image_dimension'],w['ambient_dimension'])

    def test_poincare_perfect_group(self):
        self.assertEqual(a5_certificate(),(60,60))
        self.assertEqual(poincare_attack().witness['abelianization_order'],1)

    def test_ym_positive_gaps_decrease(self):
        rows=ym_attack().witness['sequence']
        gaps=[Fraction(r['physical_gap']) for r in rows]
        self.assertTrue(all(g>0 for g in gaps))
        self.assertEqual(gaps,[Fraction(1,r['n']) for r in rows])
        self.assertEqual(gaps,sorted(gaps,reverse=True))

    def test_seven_distinct_findings(self):
        fs=[a() for a in ATTACKS]
        self.assertEqual(len({f.problem for f in fs}),7)
        self.assertTrue(all(f.limitation and f.next_obligation for f in fs))

    def test_challenge_does_not_refute_conjectures(self):
        routes=route_statuses([a() for a in ATTACKS])
        for r in routes.values():
            self.assertEqual(r['route_using_that_shortcut'],'CONTESTED')
            self.assertEqual(r['original_proof_obligations'],'UNRESOLVED')
            self.assertNotIn(r['underlying_problem'], ['SOLVED','REFUTED'])

    def test_duplicate_findings_rejected(self):
        f=rh_attack()
        with self.assertRaises(ValueError):route_statuses([f,f])

    def test_unrecognized_outcome_rejected(self):
        with self.assertRaises(ValueError):route_statuses([replace(rh_attack(), outcome='CERTIFIED')])


if __name__=='__main__':
    unittest.main()
