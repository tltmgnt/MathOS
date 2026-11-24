import unittest
from unittest.mock import patch

from mathos.research import tga_proctor_mixed_routing as m
from mathos.research import tga_proctor_combined_boundary as c
from mathos.research import tga_proctor_capacity as cap
from mathos.research import tga_proctor_xor_cnf as x


class MixedRoutingTests(unittest.TestCase):
    def test_controls(self):
        r=m.controls()
        self.assertEqual(sum(r["outcomes"].values()),3000)
        self.assertEqual(len(r["fixtures"]),12)

    def test_limits_and_prefix(self):
        n,cs=c.guarded_php(4)
        full=m.derive(n,cs)
        self.assertEqual(len(full["steps"]),45)
        for sig,steps in ((0,100),(100,0),(5,100),(1000,1)):
            d=m.derive(n,cs,sig,steps)
            self.assertLessEqual(d["signature_count"],sig)
            self.assertLessEqual(d["resolution_steps"],steps)
            self.assertEqual(c.replay(n,cs,d["steps"]),d["clauses"])
            self.assertEqual(d["steps"],full["steps"][:len(d["steps"])])
        r=m.solve(n,cs,0,0,signature_limit=0)
        self.assertEqual(r["status"],"UNKNOWN")
        self.assertFalse(m.verify(n,cs,r))

    def test_augmented_route_and_tamper(self):
        # Resolving selector pair gives a unit; original opposite unit
        # is required for an XOR contradiction in the augmented scope.
        cs=((1,2),(1,-2),(-1,))
        # Disable BVE here so it cannot find the contradiction first.
        r=m.solve(2,cs,0,0)
        self.assertEqual((r["status"],r["route"]),("UNSAT","MIXED"))
        steps,scope,tag,p=r["proof"]
        self.assertEqual(scope,"AUGMENTED")
        with patch.object(m,"derive",side_effect=AssertionError("no derivation search")), \
             patch.object(m,"_infer",side_effect=AssertionError("no inference search")):
            self.assertTrue(m.verify(2,cs,r))
            for bad in ((steps,"DERIVED",tag,p),(steps,"OTHER",tag,p),
                        (steps,scope,"OTHER",p),((),scope,tag,p),
                        (steps,scope,tag,{**p,"status":"UNKNOWN"})):
                self.assertFalse(m.verify(2,cs,{**r,"proof":bad}))
            self.assertFalse(m.verify(2,cs,{**r,"status":"SAT"}))

    def test_no_derived_sat_promotion(self):
        cs=((1,2),(1,-2),(-1,3))
        r=m.solve(3,cs,0,0)
        self.assertEqual(r["status"],"UNKNOWN")
        r=m.solve(3,cs,0,100)
        self.assertEqual(r["status"],"SAT")
        self.assertTrue(m.verify(3,cs,r))

    def test_prior_route_and_pair_accounting(self):
        parity=x.encode_parity((1,2,3),0)+x.encode_parity((1,2,3),1)
        r=m.solve(3,parity,0,0)
        self.assertNotEqual(r["route"],"MIXED")
        self.assertEqual(r["status"],"UNSAT")
        self.assertEqual(r["mixed_stop"],"NOT_RUN")
        self.assertTrue(m.verify(3,parity,r))
        cs=((1,2,3),(-1,4,5))
        r=m.solve(5,cs,1,100)
        self.assertLessEqual(r["pair_tests"],1)
        self.assertTrue(m.verify(5,cs,r))

    def test_invalid_limits(self):
        for kw in ({"signature_limit":-1},{"step_limit":True},{"pair_limit":-1},
                   {"node_limit":True},{"allow_wide":1}):
            with self.assertRaises(ValueError):
                m.solve(0,(),**kw)


if __name__=="__main__":
    unittest.main()
