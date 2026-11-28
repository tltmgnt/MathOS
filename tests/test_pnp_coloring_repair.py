import copy
import json
import random
import unittest
from itertools import combinations
from mathos.research import pnp_coloring_repair as c
from mathos.research import pnp_coloring_portfolio as portfolio
from mathos.research.pnp_coloring_external import manifest
from mathos.research.pnp_conflict_frontier import bitset20
from mathos.research.pnp_structural_kernel import Budget
from mathos.research.pnp_unified_portfolio import DEFAULT_PLANS


def encode(n,edges):
    f=[]
    for i in range(n):
        a=list(range(3*i+1,3*i+4))
        f.extend([[-x,-y] for x,y in combinations(a,2)])
        f.append(a)
    for i,j in edges:
        f.extend([[-(3*i+k),-(3*j+k)] for k in (1,2,3)])
    return f


class ColoringTests(unittest.TestCase):
    def test_recognize_and_witness(self):
        f=encode(4,[(0,1),(1,2),(2,3),(3,0)])
        r=c.attempt(12,f,100000,5)
        self.assertEqual(r["decision"],"sat")
        c.replay(12,f,json.loads(json.dumps(r)),100000)
        q=copy.deepcopy(r)
        q["proof"]["certificate"]=[False]*12
        with self.assertRaises(ValueError):
            c.replay(12,f,q,100000)
        self.assertIsNone(c.recognize(12,f[:-1],Budget()))
        self.assertIsNone(c.recognize(12,f[1:],Budget()))
        self.assertIsNone(c.recognize(12,f+[[1]],Budget()))

    def test_unsat_is_unknown(self):
        f=encode(4,list(combinations(range(4),2)))
        self.assertFalse(bitset20(12,f))
        r=c.attempt(12,f,2000,5)
        self.assertEqual(r["decision"],"unknown")
        c.replay(12,f,r,2000)

    def test_random_reference(self):
        rng=random.Random(192406)
        for n in range(2,7):
            for _ in range(20):
                f=encode(n,[e for e in combinations(range(n),2) if rng.random()<.55])
                rng.shuffle(f)
                r=c.attempt(3*n,f,5000,5)
                if r["decision"]=="sat":
                    self.assertTrue(bitset20(3*n,f))
                    c.replay(3*n,f,r,5000)
                else:
                    self.assertEqual(r["decision"],"unknown")

    def test_portfolio_and_budget(self):
        f=encode(22,[(i,(i+1)%22) for i in range(22)])
        policy={"order":[{"plan":list(p),"suggested_cap":50000} for p in DEFAULT_PLANS]}
        plan=["min_product",8]
        for n,g in ((66,f),(2,[[1,2]])):
            r=portfolio.solve(n,g,policy,plan)
            self.assertEqual(r["decision"],"sat")
            portfolio.verify(n,g,policy,plan,json.loads(json.dumps(r)))
            q=copy.deepcopy(r)
            q["work_steps"]+=1
            with self.assertRaises(ValueError):
                portfolio.verify(n,g,policy,plan,q)
        r=c.attempt(66,f,1,5)
        self.assertEqual(r["decision"],"unknown")
        c.replay(66,f,r,1)

    def test_manifest(self):
        m=manifest()
        self.assertEqual(len(m["cases"]),40)
        self.assertEqual(len({c["blob"] for c in m["cases"]}),40)
        self.assertEqual(sum(c["group"]=="flat_heldout" for c in m["cases"]),8)


if __name__=="__main__":
    unittest.main()
