import copy
import json
import unittest
from mathos.research.pnp_cross_model import prism,propose,verify,first_step_width
from mathos.research.pnp_cross_model_frontier import run,audit,budget
from mathos.research.pnp_structural_kernel import brute
from mathos.research.pnp_algebra_frontier import xor_block


class TestCrossModel(unittest.TestCase):
    def test_small_family(self):
        for m in (3,4):
            for i in (True,False):
                n,f,rows=prism(m,inconsistent=i)
                self.assertEqual((n,len(f)),(3*m,8*m))
                self.assertEqual(brute(n,f,budget()),not i)
                a=propose(n,f,budget())
                self.assertIsNotNone(a)
                self.assertTrue(verify(n,f,json.loads(json.dumps(a)),budget()))
                self.assertEqual(a["xor_rhs"],int(i))
                self.assertEqual(first_step_width(n,f,budget()),4)

    def test_rejected_scopes(self):
        f=xor_block((1,2,3),0)+xor_block((1,2,4),1)
        self.assertIsNone(propose(4,f,budget()))
        n,f,_=prism(3)
        self.assertIsNone(propose(n,f[:-1],budget()))

    def test_forgery(self):
        n,f,_=prism(3)
        c=propose(n,f,budget())
        for key,value in (("first_derived_width_lower",3),("xor_rhs",0),("rows",c["rows"][:-1])):
            with self.assertRaises(ValueError):
                verify(n,f,{**c,key:value},budget())
        r=copy.deepcopy(c)
        vs,b=r["rows"][0]
        r["rows"][0]=(vs,1-b)
        with self.assertRaises(ValueError):
            verify(n,f,r,budget())
        with self.assertRaises(ValueError):
            verify(n,f[:-1],c,budget())

    def test_pipeline(self):
        r=run()
        self.assertEqual(r["completion"],"completed")
        self.assertTrue(audit(json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["width_three_blocked"],12)
        self.assertEqual(r["summary"]["affine_decisions"],12)
        with self.assertRaises(ValueError):
            audit({**r,"rows":r["rows"][:-1]})
        with self.assertRaises(ValueError):
            audit({**r,"p_not_equals_np_established":True})


if __name__=="__main__":
    unittest.main()
