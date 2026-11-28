import copy
import json
import unittest

from mathos.research.pnp_inference_obstructions import (chain,cube,chain_certificate,cube_certificate,
    verify_chain,verify_cube,balanced_proof,depth_support)
from mathos.research.pnp_inference_complexity import run,audit,budget
from mathos.research.pnp_structural_kernel import brute


class TestInferenceObstructions(unittest.TestCase):
    def test_exact_depth(self):
        for n in range(1,33):
            f=chain(n)
            c=chain_certificate(n)
            self.assertTrue(verify_chain(n,f,c,budget()))
            p=balanced_proof(n,budget())
            s=depth_support(n,f,json.loads(json.dumps(p)),budget())
            self.assertEqual(s["depth"],n.bit_length())
            self.assertEqual(s["axiom_support"],n+1)
            self.assertEqual(s["derived_steps"],n)
            self.assertLessEqual(s["maximum_derived_width"],2)

    def test_minimality(self):
        for n in range(1,7):
            f=chain(n)
            self.assertFalse(brute(n,f,budget()))
            for j in range(len(f)):
                self.assertTrue(brute(n,f[:j]+f[j+1:],budget()))

    def test_width(self):
        for k in range(2,7):
            f=cube(k)
            self.assertFalse(brute(k,f,budget()))
            self.assertTrue(verify_cube(k,f,cube_certificate(k),budget()))

    def test_tampering(self):
        f=chain(5)
        c=chain_certificate(5)
        with self.assertRaises(ValueError):
            verify_chain(5,f,{**c,"minimum_depth":2},budget())
        with self.assertRaises(ValueError):
            verify_chain(5,f[:-1],c,budget())
        c=cube_certificate(4)
        with self.assertRaises(ValueError):
            verify_cube(4,cube(4),{**c,"minimum_first_derived_width":2},budget())
        p=balanced_proof(5,budget())
        p["steps"][0]["pivot"]=999
        with self.assertRaises(ValueError):
            depth_support(5,f,p,budget())

    def test_full_audit(self):
        r=run()
        self.assertEqual(r["completion"],"completed")
        self.assertTrue(audit(json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["chain_exact_depth_matches"],9)
        self.assertEqual(r["summary"]["cube_exact_width_matches"],6)
        self.assertEqual(r["summary"]["chain_four_wave_provably_blocked"],5)
        with self.assertRaises(ValueError):
            audit({**r,"p_not_equals_np_established":True})
        with self.assertRaises(ValueError):
            audit({**r,"chains":r["chains"][:-1]})
        forged=copy.deepcopy(r)
        forged["summary"]["chain_two_sat_escapes"]+=1
        with self.assertRaises(ValueError):
            audit(forged)


if __name__=="__main__":
    unittest.main()
