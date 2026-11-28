import copy
import json
import random
import unittest
from mathos.research import pnp_xor_subsystem as xor
from mathos.research import pnp_xor_portfolio as portfolio
from mathos.research.pnp_xor_frontier import manifest,reference,encode,graph_case
from mathos.research.pnp_conflict_frontier import bitset20
from mathos.research.pnp_structural_kernel import Budget
from mathos.research.pnp_unified_portfolio import DEFAULT_PLANS
from mathos.research.pnp_v16_stress import pigeon


def budget():
    return Budget(seconds=5,max_steps=100000,max_cells=200000)


class XorTests(unittest.TestCase):
    def test_dual_with_nonaffine_residual(self):
        f=encode([1,2,3],0)+encode([1,2,4],0)+encode([3,4],1)+[[5,6,7]]
        r=xor.propose(7,f,budget())
        self.assertEqual(r["decision"],"unsat")
        self.assertFalse(bitset20(7,f))
        xor.verify(7,f,json.loads(json.dumps(r)),budget())
        for mutation in ("rhs","scope","sources","dual"):
            q=copy.deepcopy(r)
            row=q["certificate"][0]
            if mutation=="rhs": row["rhs"]^=1
            elif mutation=="scope": row["scope"][0]=True
            elif mutation=="sources": row["sources"].pop()
            else: q["certificate"].pop()
            with self.assertRaises(ValueError):
                xor.verify(7,f,q,budget())

    def test_partial_not_equivalent(self):
        f=encode([1,2,3],0)+[[1,2,3]]
        r=xor.propose(3,f,budget())
        self.assertEqual(r["decision"],"sat")
        xor.verify(3,f,r,budget())
        # A consistent affine system with an inconsistent extra CNF
        # that is not recognized by the bounded equation extractor.
        g=encode([1,2,3],0)+[[4,5,6,7,8],[-4],[-5],[-6],[-7],[-8]]
        self.assertFalse(bitset20(8,g))
        self.assertIsNone(xor.propose(8,g,budget()))

    def test_duplicate_tautology_and_budget(self):
        f=encode([1,2,3],1)
        g=[c+[c[0]] for c in f]+[[1,-1,2],f[0]]
        r=xor.attempt(3,g,100000,5)
        self.assertEqual(r["decision"],"sat")
        xor.replay(3,g,r,100000)
        r=xor.attempt(3,g,1,5)
        self.assertEqual(r["decision"],"unknown")
        xor.replay(3,g,r,1)

    def test_random_against_exhaustive(self):
        rng=random.Random(192005)
        credited=0
        for n in range(3,9):
            for _ in range(200):
                f=[]
                for _ in range(rng.randrange(1,6)):
                    f.extend(encode(sorted(rng.sample(range(1,n+1),rng.choice((2,3)))),rng.randrange(2)))
                f += [[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3)]
                      for _ in range(rng.randrange(8))]
                r=xor.propose(n,f,budget())
                if r is not None:
                    credited+=1
                    xor.verify(n,f,json.loads(json.dumps(r)),budget())
                    self.assertEqual(r["decision"]=="sat",bitset20(n,f))
        self.assertGreater(credited,0)

    def test_graph_duals(self):
        for k in (20,32,48,64):
            for mixed in (False,True):
                c=graph_case(k,True,mixed)
                r=xor.attempt(c["n"],c["clauses"],25000,5)
                self.assertEqual(r["decision"],"unsat")
                xor.replay(c["n"],c["clauses"],r,25000)
            c=graph_case(k,False,False)
            r=xor.attempt(c["n"],c["clauses"],25000,5)
            self.assertEqual(r["decision"],"sat")
            xor.replay(c["n"],c["clauses"],r,25000)

    def test_portfolio(self):
        policy={"order":[{"plan":list(p),"suggested_cap":50000} for p in DEFAULT_PLANS]}
        plan=["min_product",8]
        c=graph_case(32,True,True)
        for n,f,want in ((c["n"],c["clauses"],"unsat"),(30,pigeon(6,5),"unsat"),(2,[[1,2]],"sat")):
            r=portfolio.solve(n,f,policy,plan)
            self.assertEqual(r["decision"],want)
            portfolio.verify(n,f,policy,plan,json.loads(json.dumps(r)))
            q=copy.deepcopy(r)
            q["work_steps"]+=1
            with self.assertRaises(ValueError):
                portfolio.verify(n,f,policy,plan,q)

    def test_manifest(self):
        cases=manifest()
        self.assertEqual(len(cases),153)
        self.assertEqual(len({c["id"] for c in cases}),153)
        for c in cases:
            self.assertIs(type(reference(c)),bool)


if __name__=="__main__":
    unittest.main()
