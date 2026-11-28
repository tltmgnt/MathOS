import copy
import json
import random
import unittest
from itertools import product
from mathos.research import pnp_indexed_rup as indexed
from mathos.research import pnp_indexed_rup_portfolio as portfolio
from mathos.research import pnp_conflict_learning as cdcl
from mathos.research.pnp_proof_library import rup
from mathos.research.pnp_structural_kernel import Budget, Exhausted
from mathos.research.pnp_conflict_frontier import bitset20
from mathos.research.pnp_indexed_rup_external import manifest


def budget():
    return Budget(seconds=15,max_steps=4_000_000,max_cells=200_000)


class IndexedTests(unittest.TestCase):
    def test_watch_reset_differential(self):
        rng=random.Random(192507)
        for n in range(1,9):
            for _ in range(50):
                known=[]
                index=indexed.Index(n,known,budget())
                for __ in range(30):
                    c=tuple(sorted(v if rng.randrange(2) else -v
                                   for v in rng.sample(range(1,n+1),rng.randrange(min(n,4)+1))))
                    a=rup(known,c,budget())
                    self.assertEqual(index.rup(c,budget()),a)
                    if rng.randrange(4)==0:
                        # Input additions may be arbitrary axioms here;
                        # production verify only admits proved additions.
                        known.append(c)
                        index.add(c,budget())

    def test_proof_and_forgery(self):
        f=[[1,2],[1,-2],[-1,2],[-1,-2]]
        p={"decision":"unsat","certificate":[[1],[]]}
        self.assertTrue(indexed.verify(2,f,p,budget()))
        for g,c in ((f,[[]]),(f,[[1,1],[]]),(f,[[1,-1],[]]),
                    (f,[[1]]),(f[:-1],[[1],[]]),(f,[[3],[]])):
            with self.assertRaises(ValueError):
                indexed.verify(2,g,dict(p,certificate=c),budget())
        r=indexed.attempt(2,f,100000,5)
        self.assertEqual(r["decision"],"unsat")
        indexed.replay(2,f,json.loads(json.dumps(r)),100000)
        q=copy.deepcopy(r)
        q["replay_steps"]+=1
        with self.assertRaises(ValueError):
            indexed.replay(2,f,q,100000)
        self.assertEqual(indexed.attempt(2,f,1,5)["status"],"search_exhausted")

    def test_random_decisions(self):
        rng=random.Random(192508)
        for n in range(1,9):
            for _ in range(80):
                f=[[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),rng.randrange(min(3,n)+1))]
                   for __ in range(rng.randrange(2,25))]
                r=indexed.attempt(n,f,100000,5)
                self.assertEqual(r["decision"]=="sat",bitset20(n,f))
                self.assertNotEqual(r["decision"],"unknown")
                indexed.replay(n,f,json.loads(json.dumps(r)),100000)

    def test_profile_and_gate(self):
        f=[[1,2],[1,-2],[-1,2],[-1,-2]]
        r=indexed.profile(2,f)
        self.assertEqual(r["proof"]["decision"],"unsat")
        indexed.audit_profile(2,f,json.loads(json.dumps(r)),100000)
        self.assertFalse(portfolio.eligible(f))
        self.assertEqual(len(manifest()["cases"]),48)
        self.assertEqual(len({c["blob"] for c in manifest()["cases"]}),48)

    def test_units_empty_and_tautological_query(self):
        for f in ([],[()],[(1,),(-1,)],[(1,2),(-1,2)]):
            idx=indexed.Index(2,f,budget())
            for c in ((),(1,),(-1,),(-1,1),(2,),(-2,)):
                self.assertEqual(idx.rup(c,budget()),rup(f,c,budget()))


if __name__=="__main__":
    unittest.main()
