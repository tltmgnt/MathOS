import unittest
from copy import deepcopy
from fractions import Fraction
from math import comb
from mathos.research.pnp_overlap_asymptotic import (
    probability_bound,sample,check_obstruction,evidence,has_full_projections)
from mathos.research.pnp_overlap_order import recover_fast

class AsymptoticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ds,cls.rs,cls.cert,cls.trial=sample(64,16,2)

    def test_integer_probability_bounds(self):
        for n in (1,2,3,4,16):
            c,h,t=64*n,16*n,n
            out=probability_bound(n)
            self.assertEqual(out["minimum_order_lower"],n+1)
            bad_distance=Fraction(sum(comb(c,s)*3**s for s in range(1,t+1)),2**h)
            bad_sat=Fraction(2**h*3**c,4**c)
            bad_rank=Fraction(2**h-1,2**(2*c))
            for actual,exponent in zip((bad_distance,bad_sat,bad_rank),out["bad_probability_upper_terms"]):
                self.assertLess(actual,Fraction(1,2**exponent))
            self.assertLess(sum(Fraction(1,2**e) for e in out["bad_probability_upper_terms"]),1)

    def test_finite_sample(self):
        self.assertEqual((len(self.ds),len(self.cert["directions"]),self.cert["minimum_order_lower"]),(64,16,3))
        self.assertTrue(check_obstruction(self.ds,self.rs,self.cert))

    def test_small_recovery_stalls(self):
        ds,rs,cert,_=sample(24,8,1)
        self.assertTrue(check_obstruction(ds,rs,cert))
        out,trace,empty=recover_fast(ds,rs,1)
        self.assertEqual((out,trace,empty),(rs,[],None))

    def test_projection_rank(self):
        self.assertFalse(has_full_projections(2,[1,2],2))
        self.assertTrue(has_full_projections(2,[1,2,4,8],2))

    def test_mutations(self):
        for change in (lambda c:c["directions"].pop(),
                       lambda c:c["directions"].__setitem__(0,0),
                       lambda c:c["directions"].append(c["directions"][0]),
                       lambda c:c.update(minimum_order_lower=4),
                       lambda c:c.update(closed_order=0),
                       lambda c:c.update(anchor=1<<128)):
            bad=deepcopy(self.cert)
            change(bad)
            self.assertFalse(check_obstruction(self.ds,self.rs,bad))
        self.assertFalse(check_obstruction([(15,15)]*64,self.rs,self.cert))

    def test_budgets_and_evidence(self):
        with self.assertRaises(ValueError):
            sample(64,17,1)
        with self.assertRaises(ValueError):
            sample(64,16,4)
        data=evidence()
        self.assertEqual(data["finite"]["full_projection_subsets"],2016)
        self.assertTrue(data["finite"]["checker_accepted"])
