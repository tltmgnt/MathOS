import copy
import json
import random
import unittest
from mathos.research import pnp_affine_projected as projected
from mathos.research import pnp_affine_projected_portfolio as portfolio
from mathos.research import pnp_xor_subsystem as xor
from mathos.research.pnp_affine_projected_frontier import manifest,reference,lifted
from mathos.research.pnp_xor_frontier import encode,graph_case
from mathos.research.pnp_conflict_frontier import bitset20
from mathos.research.pnp_structural_kernel import Budget
from mathos.research.pnp_unified_portfolio import DEFAULT_PLANS


def budget():
    return Budget(seconds=5,max_steps=100000,max_cells=200000)


class ProjectedTests(unittest.TestCase):
    def test_residual_unsat_and_forgery(self):
        f=sum((encode([v,v+4],0) for v in range(1,5)),[])
        f += [[5,6],[-5,7],[-6,7],[-7,8],[-7,-8]]
        self.assertFalse(bitset20(8,f))
        r=projected.propose(8,f,budget())
        self.assertEqual((r["decision"],r["kind"]),("unsat","projected_rup"))
        projected.verify(8,f,json.loads(json.dumps(r)),budget())
        for mutation in ("rhs","sources","provenance","proof","dimension"):
            q=copy.deepcopy(r)
            p=q["certificate"]
            if mutation=="rhs": p["forms"][0]["rhs"]^=1
            elif mutation=="sources": p["rows"][0]["sources"].pop()
            elif mutation=="provenance": p["forms"][0]["rows"]=[]
            elif mutation=="dimension": p["projected_n"]+=1
            else: p["proof"]=[]
            with self.assertRaises(ValueError):
                projected.verify(8,f,q,budget())
        with self.assertRaises(ValueError):
            projected.verify(8,f[:-1],r,budget())

    def test_gate_truth_table_and_lift(self):
        f=encode([1,2,3],1)+encode([2,4,5],0)+[[3,5],[-3,4]]
        rows=xor.extract(f,budget())
        forms,dual=projected.parameterize(5,rows,budget())
        self.assertIsNone(dual)
        projected.check_parameterization(5,f,rows,forms,budget())
        a=projected.compile_residual(5,f,rows,forms,budget())
        b=projected.compile_residual(5,f,rows,forms,budget(),checker=True)
        self.assertEqual(a[0],b[0])
        self.assertEqual(set(a[1]),set(b[1]))
        self.assertEqual(a[2],b[2])
        self.assertEqual(bitset20(a[0],a[1]),bitset20(5,f))
        r=projected.propose(5,f,budget())
        self.assertEqual(r["decision"],"sat")
        projected.verify(5,f,r,budget())

    def test_dual_and_exhaustion(self):
        f=encode([1,2,3],0)+encode([1,2,3],1)
        r=projected.attempt(3,f,100000,5)
        self.assertEqual(r["proof"]["kind"],"dual")
        projected.replay(3,f,r,100000)
        r=projected.attempt(3,f,1,5)
        self.assertEqual(r["decision"],"unknown")
        projected.replay(3,f,r,1)

    def test_random_small(self):
        rng=random.Random(192107)
        for n in range(3,9):
            for _ in range(100):
                f=[]
                for _ in range(rng.randrange(1,5)):
                    f.extend(encode(sorted(rng.sample(range(1,n+1),3)),rng.randrange(2)))
                f += [[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3)]
                      for _ in range(rng.randrange(15))]
                r=projected.attempt(n,f,100000,5)
                self.assertNotEqual(r["decision"],"unknown")
                projected.replay(n,f,json.loads(json.dumps(r)),100000)
                self.assertEqual(r["decision"]=="sat",bitset20(n,f))

    def test_lifted_and_portfolio(self):
        f=[[1,2],[-1,3],[-2,3],[-3,4],[-3,-4]]
        g=lifted(4,f,192106)
        self.assertFalse(bitset20(13,g))
        self.assertEqual(projected.attempt(13,g,100000,5)["decision"],"unsat")
        policy={"order":[{"plan":list(p),"suggested_cap":50000} for p in DEFAULT_PLANS]}
        plan=["min_product",8]
        c=graph_case(32,False,True)
        for n,h,want in ((c["n"],c["clauses"],"sat"),(2,[[1,2]],"sat")):
            r=portfolio.solve(n,h,policy,plan)
            self.assertEqual(r["decision"],want)
            portfolio.verify(n,h,policy,plan,json.loads(json.dumps(r)))
            q=copy.deepcopy(r)
            q["work_steps"]+=1
            with self.assertRaises(ValueError):
                portfolio.verify(n,h,policy,plan,q)

    def test_manifest(self):
        cases=manifest()
        self.assertEqual(len(cases),171)
        self.assertEqual(len({c["id"] for c in cases}),171)
        for c in cases:
            self.assertIs(type(reference(c)),bool)


if __name__=="__main__":
    unittest.main()
