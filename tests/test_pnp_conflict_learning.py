import copy
import itertools
import json
import random
import unittest
from mathos.research import pnp_conflict_learning as cdcl
from mathos.research import pnp_conflict_portfolio as portfolio
from mathos.research.pnp_conflict_frontier import manifest, reference, bitset20, parity_cycle
from mathos.research.pnp_v16_stress import chain, bitset_reference, pigeon
from mathos.research.pnp_unified_portfolio import DEFAULT_PLANS
from mathos.research.pnp_structural_kernel import Budget


class ConflictTests(unittest.TestCase):
    def test_conflict_learning_and_independent_replay(self):
        f = [[1,2],[1,-2],[-1,2],[-1,-2]]
        r = cdcl.attempt(2,f,10000,5)
        self.assertEqual(r["decision"],"unsat")
        self.assertGreaterEqual(r["proof"]["conflicts"],2)
        self.assertGreaterEqual(len(r["proof"]["certificate"]),2)
        cdcl.replay(2,f,json.loads(json.dumps(r)),10000)
        bad = copy.deepcopy(r)
        bad["proof"]["certificate"] = [[]]
        with self.assertRaises(ValueError):
            cdcl.replay(2,f,bad,10000)
        with self.assertRaises(ValueError):
            cdcl.replay(2,f[:-1],r,10000)

    def test_exhaustive_two_variable_formulas(self):
        clauses = [list(c) for k in range(3) for c in itertools.product((-1,1),repeat=k)]
        # Distinct variable identifiers, all non-tautological clauses.
        clauses = [[],[1],[-1],[2],[-2],[1,2],[1,-2],[-1,2],[-1,-2]]
        for bits in range(1<<len(clauses)):
            f = [c for i,c in enumerate(clauses) if bits>>i&1]
            r = cdcl.attempt(2,f,10000,5)
            self.assertNotEqual(r["decision"],"unknown")
            self.assertEqual(r["decision"]=="sat",bitset_reference(2,f))
            cdcl.replay(2,f,json.loads(json.dumps(r)),10000)

    def test_random_redundant_and_adversarial(self):
        rng = random.Random(191904)
        for n in range(1,9):
            for _ in range(200):
                f = [[rng.choice((-1,1))*rng.randint(1,n)
                      for _ in range(rng.randrange(5))] for _ in range(rng.randrange(35))]
                r = cdcl.attempt(n,f,100000,5)
                self.assertNotEqual(r["decision"],"unknown")
                self.assertEqual(r["decision"]=="sat",bitset_reference(n,f))
                cdcl.replay(n,f,r,100000)
        for n,f in ((0,[]),(0,[[]]),(1,[[1,1],[-1,1]])):
            self.assertEqual(cdcl.attempt(n,f,10000,5)["decision"]=="sat",bitset20(n,f))

    def test_iterative_chain_and_budget(self):
        for bad in (False,True):
            f = chain(96,bad)
            r = cdcl.attempt(96,f,100000,5)
            self.assertEqual(r["decision"],"unsat" if bad else "sat")
            cdcl.replay(96,f,r,100000)
        r = cdcl.attempt(96,chain(96,True),1,5)
        self.assertEqual(r["decision"],"unknown")
        cdcl.replay(96,chain(96,True),r,1)

    def test_parity_labels_and_reference(self):
        for k in (4,6,8):
            for bad in (False,True):
                f = parity_cycle(k,bad)
                self.assertEqual(bitset20(k+1,f),not bad)
                self.assertEqual(bitset20(k+1,f),bitset_reference(k+1,f))
        cases = manifest()
        self.assertEqual(len(cases),129)
        self.assertEqual(len({c["id"] for c in cases}),129)
        for c in cases:
            self.assertIs(type(reference(c)),bool)

    def test_portfolio_and_tampering(self):
        policy = {"order":[{"plan":list(p),"suggested_cap":50000} for p in DEFAULT_PLANS]}
        plan = ["min_product",8]
        for n,f,decision in ((96,chain(96,True),"unsat"),(30,pigeon(6,5),"unsat"),
                             (2,[[1,2]],"sat")):
            r = portfolio.solve(n,f,policy,plan)
            self.assertEqual(r["decision"],decision)
            self.assertEqual(r["eligible"],n==96)
            portfolio.verify(n,f,policy,plan,json.loads(json.dumps(r)))
            bad = copy.deepcopy(r)
            bad["work_steps"] += 1
            with self.assertRaises(ValueError):
                portfolio.verify(n,f,policy,plan,bad)


if __name__=="__main__":
    unittest.main()
