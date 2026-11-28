import unittest
from copy import deepcopy
from mathos.research.pnp_overlap_pebbling import (
    chain,search,check_chain_certificate,exact,check_exact,identity_terms,original_frame,evidence)
from mathos.research.pnp_overlap_degree import refute,check_degree
from mathos.research.pnp_overlap_boundary import solve,affine_solve
from mathos.research.pnp_overlap_order import recover_fast

class PebblingTests(unittest.TestCase):
    def test_small_exact_degree(self):
        for n in range(1,9):
            ds,rs=chain(n)
            d=n.bit_length()
            c=exact(n)
            self.assertTrue(check_exact(n,c))
            for k,kind in ((d-1,"no_refutation"),(d,"refutation")):
                p=refute(ds,rs,k)
                self.assertEqual(p["kind"],kind)
                self.assertTrue(check_degree(ds,rs,p))

    def test_identity_translation(self):
        for n in (1,2,3,5,7,15):
            ds,rs=chain(n)
            c=exact(n)
            a,dirs=original_frame(n)
            p={"kind":"refutation","anchor":a,"directions":dirs,
               "degree":c["minimum"],"terms":identity_terms(n,c["upper"])}
            self.assertTrue(check_degree(ds,rs,p))

    def test_lower_functional_translation(self):
        for n in (1,3,7):
            ds,rs=chain(n)
            c=exact(n)
            a,dirs=original_frame(n)
            p={"kind":"no_refutation","anchor":a,"directions":dirs,
               "degree":c["minimum"]-1,"functional":c["lower"]["configurations"]}
            self.assertTrue(check_degree(ds,rs,p))

    def test_easy_affine_recovery(self):
        for n in range(1,9):
            ds,rs=chain(n)
            self.assertIsNotNone(affine_solve(2*len(ds),rs))
            self.assertIsNone(solve(ds,rs))
            self.assertIsNotNone(recover_fast(ds,rs,1)[2])

    def test_mutations(self):
        c=exact(7)
        for mutate in (lambda p:p["lower"]["configurations"].pop(),
                       lambda p:p["upper"]["configurations"].pop(),
                       lambda p:p.update(minimum=4),
                       lambda p:p["upper"]["configurations"].insert(1,4),
                       lambda p:p["lower"]["configurations"].append(64)):
            bad=deepcopy(c)
            mutate(bad)
            self.assertFalse(check_exact(7,bad))
        with self.assertRaises(ValueError):
            search(63,10)

    def test_evidence(self):
        r=evidence()
        self.assertEqual([x["minimum_static_degree"] for x in r["cases"]],[1,2,3,4,5])
        self.assertTrue(all(x["checker_accepted"] for x in r["cases"]))
