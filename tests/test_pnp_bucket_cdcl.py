import copy
import json
import random
import unittest
from mathos.research import pnp_bucket_cdcl as optimized
from mathos.research import pnp_bucket_cdcl_portfolio as portfolio
from mathos.research import pnp_conflict_learning as frozen
from mathos.research import pnp_indexed_rup as indexed
from mathos.research.pnp_structural_kernel import Budget
from mathos.research.pnp_bucket_cdcl_external import manifest
from mathos.research.pnp_conflict_frontier import bitset20
from mathos.research.pnp_unified_portfolio import DEFAULT_PLANS


def budget():
    return Budget(seconds=15,max_steps=1_000_000,max_cells=200_000)


class BucketTests(unittest.TestCase):
    def test_exact_search_equivalence(self):
        rng=random.Random(192610)
        for n in range(1,11):
            for _ in range(60):
                f=[[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),rng.randrange(min(n,3)+1))]
                    for __ in range(rng.randrange(1,30))]
                a,b=frozen.propose(n,f,budget()),optimized.propose(n,f,budget())
                self.assertEqual(a,b)
                self.assertEqual(b["decision"]=="sat",bitset20(n,f))
                indexed.verify(n,f,b,budget())

    def test_dense_conflict_equivalence(self):
        rng=random.Random(192611)
        for n in (8,10,12,16):
            for _ in range(12):
                f=[[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3)]
                   for __ in range(5*n)]
                a,b=frozen.propose(n,f,budget()),optimized.propose(n,f,budget())
                self.assertEqual(a,b)
                r=optimized.attempt(n,f,100000,5)
                self.assertNotEqual(r["decision"],"unknown")
                indexed.replay(n,f,json.loads(json.dumps(r)),100000)

    def test_root_empty_unused_and_tautology(self):
        for n,f in ((0,[]),(0,[[]]),(5,[[1],[-1]]),(8,[[1,-1],[2]]),
                    (6,[[1],[2],[-1,3],[-3,4]])):
            self.assertEqual(frozen.propose(n,f,budget()),optimized.propose(n,f,budget()))

    def test_sparse_branch_work(self):
        # All variables have same initial score and no conflicts.
        # Every decision retains the original tie-breaking order.
        n=200
        f=[[i,i+1] for i in range(1,n,2)]
        a,b=budget(),budget()
        self.assertEqual(frozen.propose(n,f,a),optimized.propose(n,f,b))
        self.assertLess(b.steps,a.steps)

    def test_modes_and_manifest(self):
        self.assertEqual(portfolio.quota("optimized_half",100000,5),(50000,2.5))
        self.assertEqual(portfolio.quota("candidate",100000,5)[0],66666)
        self.assertEqual(len(manifest()["cases"]),56)
        self.assertEqual(len({c["blob"] for c in manifest()["cases"]}),56)
        policy={"order":[{"plan":list(p),"suggested_cap":50000} for p in DEFAULT_PLANS]}
        plan=["min_product",8]
        for mode in portfolio.MODES:
            r=portfolio.solve(2,[[1,2]],policy,plan,mode=mode)
            portfolio.verify(2,[[1,2]],policy,plan,json.loads(json.dumps(r)),mode=mode)
            q=copy.deepcopy(r)
            q["mode"]="forged"
            with self.assertRaises(ValueError):
                portfolio.verify(2,[[1,2]],policy,plan,q,mode=mode)


if __name__=="__main__":
    unittest.main()
