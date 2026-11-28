import copy
import itertools
import json
import random
import unittest
from mathos.research.pnp_sparse_degree import coordinates,derive,evaluation,verify
from mathos.research.pnp_degree_closure import derive as dense,verify as verify_dense
from mathos.research.pnp_sparse_degree_frontier import run,audit
from mathos.research.pnp_structural_kernel import Budget,Exhausted,normalize
from mathos.research.pnp_inference_complexity import budget


class TestSparseDegree(unittest.TestCase):
    def test_compressed_coordinates(self):
        t=coordinates(64,2,budget())
        self.assertEqual(len(t),2081)
        self.assertEqual(t[0],0)
        self.assertEqual(t[-1],(1<<63)|(1<<62))
        self.assertTrue(all(x.bit_count()<=2 for x in t))
        self.assertEqual(len(set(t)),len(t))
        with self.assertRaises(Exhausted):
            coordinates(64,4,budget())

    def test_exhaustive_differential(self):
        pool=[tuple((i+1)*s for i,s in enumerate(signs) if s)
              for signs in itertools.product((-1,0,1),repeat=2)]
        for mask in range(1<<len(pool)):
            f=[c for i,c in enumerate(pool) if mask>>i&1]
            a=derive(2,f,budget(),degree=2)
            b=dense(2,f,budget(),degree=2)
            self.assertTrue(verify(2,f,json.loads(json.dumps(a)),budget()))
            self.assertTrue(verify_dense(2,f,b,budget()))
            self.assertEqual(a["status"],b["status"])

    def test_random_differential(self):
        rng=random.Random(32032)
        for _ in range(60):
            n=rng.randint(3,6)
            f=[tuple(v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),rng.randint(1,3)))
               for _ in range(3*n)]
            for d in (3,4):
                a=derive(n,f,budget(),degree=d)
                b=dense(n,f,budget(),degree=d)
                self.assertTrue(verify(n,f,a,budget()))
                self.assertEqual(a["status"],b["status"])

    def test_tampering(self):
        f=[(1,2)]
        a=derive(2,f,budget(),degree=2)
        self.assertEqual(a["status"],"closed_no_refutation")
        for key,value in (("dimension",9),("functionals",[1]),("input_sha256","wrong")):
            with self.assertRaises(ValueError):
                verify(2,f,{**a,key:value},budget())
        f=[(1,),(-1,)]
        a=derive(1,f,budget(),degree=1)
        self.assertEqual(a["status"],"refuted")
        with self.assertRaises(ValueError):
            verify(1,f,{**a,"root":None},budget())
        with self.assertRaises(ValueError):
            evaluation(1,f,budget(),degree=1,assignment=0)
        with self.assertRaises(Exhausted):
            derive(1,f,Budget(max_steps=1),degree=1)

    def test_pipeline(self):
        r=run()
        self.assertEqual(r["completion"],"completed",r.get("reason"))
        self.assertTrue(audit(json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["cases"],26)
        self.assertEqual(r["summary"]["max_verified_variables"],64)
        self.assertGreaterEqual(r["summary"]["max_refuted_variables"],27)
        with self.assertRaises(ValueError):
            audit({**r,"rows":r["rows"][:-1]})
        with self.assertRaises(ValueError):
            audit({**r,"p_equals_np_established":True})


if __name__=="__main__":
    unittest.main()
