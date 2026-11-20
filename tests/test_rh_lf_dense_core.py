"""Scoped regressions of the LF bump-sum *numerical demonstration*."""
from fractions import Fraction
import math
import unittest

from mathos.research.rh_lf_dense_core import (
    build_approximation, conditional_c0_error_bound,
    demo, numerical_mollifier, scheduled_parameters, unnormalized_bump
)


class LFBumpCoreTests(unittest.TestCase):
    def test_bump_support_and_evenness(self):
        for x in (-2.0, -1.0, 1.0, 2.0):
            self.assertEqual(unnormalized_bump(x), 0.0)
        for x in (0.0, 0.2, 0.7, 0.99):
            self.assertAlmostEqual(unnormalized_bump(x),
                                   unnormalized_bump(-x), places=14)
        self.assertGreater(unnormalized_bump(0.0), 0)

    def test_rational_sequence_is_symbolic_not_evaluated(self):
        self.assertEqual(scheduled_parameters(2),
                         (Fraction(1,2),Fraction(1,16)))
        self.assertEqual(scheduled_parameters(3),
                         (Fraction(1,3),Fraction(1,512)))
        self.assertRaises(ValueError, scheduled_parameters, 1)

    def test_discrete_sum_even_for_even_input(self):
        eps, h = Fraction(1,4), Fraction(1,64)
        a = build_approximation(unnormalized_bump, 1.0, eps, h)
        for x in (0.1, 0.5, 0.9, 1.0):
            self.assertAlmostEqual(a.evaluate(x),a.evaluate(-x),delta=1e-13)
        self.assertEqual(a.evaluate(1.3),0.0)
        self.assertEqual(a.evaluate(-1.3),0.0)
        self.assertEqual(a.support_enclosure,(-1.25,1.25))

    def test_smaller_scale_improves_demo_on_interior_grid(self):
        coarse = build_approximation(unnormalized_bump,1.0,
                                     Fraction(1,2),Fraction(1,16))
        fine = build_approximation(unnormalized_bump,1.0,
                                   Fraction(1,8),Fraction(1,128))
        grid = [i/16 for i in range(-16,17)]
        coarse_error = max(abs(coarse.evaluate(x)-unnormalized_bump(x))
                           for x in grid)
        fine_error = max(abs(fine.evaluate(x)-unnormalized_bump(x))
                         for x in grid)
        self.assertLess(fine_error,coarse_error)
        self.assertLess(fine_error,0.025)

    def test_conditional_C0_bound_shrinks_on_finer_mesh(self):
        e=Fraction(1,8)
        a=conditional_c0_error_bound(e,Fraction(1,50),1.0,4.0)
        b=conditional_c0_error_bound(e,Fraction(1,500),1.0,4.0)
        self.assertGreater(a,b)
        self.assertGreaterEqual(b,0)

    def test_fixed_support_window_obstruction(self):
        # Any function supported in [-1,1] vanishes at 2, but
        # translated bump f(x-2) has f(2)=exp(-1).
        self.assertGreater(unnormalized_bump(0.0),0.36)

    def test_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            build_approximation(unnormalized_bump,1.0,0.1,Fraction(1,10))
        with self.assertRaises(ValueError):
            build_approximation(unnormalized_bump,1.0,Fraction(1,4),
                                Fraction(1,10**8),max_samples=300)
        with self.assertRaises(ValueError):
            build_approximation(unnormalized_bump,1.0,Fraction(1,4),Fraction(0,1))
        with self.assertRaises(ValueError):
            numerical_mollifier(float("nan"),Fraction(1,4))
        with self.assertRaises(ValueError):
            conditional_c0_error_bound(Fraction(1,3),Fraction(1,5),-1.0,1.0)

    def test_json_scope_restrictions(self):
        r=demo()
        self.assertFalse(r["RH_relevant_Weil_density_proved"])
        self.assertFalse(r["Riemann_hypothesis_proved"])
        self.assertFalse(r["all_derivative_LF_convergence_checked_by_code"])
        self.assertGreater(r["terms"],0)


if __name__=="__main__":
    unittest.main()
