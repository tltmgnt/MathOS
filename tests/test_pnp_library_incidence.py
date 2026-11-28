import random
import unittest
from itertools import permutations,product
from mathos.research.pnp_library_incidence import IncidenceFilter,indexed_reuse,pair_histogram
from mathos.research.pnp_proof_library import Index,mapped,reuse
from mathos.research.pnp_structural_kernel import Budget
from mathos.research.pnp_library_ablation import independent_replay


def has_embedding(f,n,known):
    for p in permutations(range(1,n+1),f["n"]):
        for s in product((-1,1),repeat=f["n"]):
            e=tuple(a*b for a,b in zip(p,s))
            if all(any(set(c)<=set(mapped(g,e)) for c in known) for g in f["axioms"]):
                return True
    return False


class TestIncidence(unittest.TestCase):
    def test_pair_rejection_and_growth(self):
        f={"n":2,"axioms":((1,2),(-1,2)),"steps":((2,),),"edges":()}
        gate=IncidenceFilter(Index([f]))
        known={(1,2),(3,4)}
        self.assertFalse(gate.allows(0,known,Budget()))
        self.assertEqual(gate.stats["pair_rejected"],1)
        known.add((-1,2))
        gate.invalidate()
        self.assertTrue(gate.allows(0,known,Budget()))
        known={(1,2)}
        gate.invalidate()
        self.assertFalse(gate.allows(0,known,Budget()))
        self.assertEqual(gate.stats["count_rejected"],1)
        known={(2,)}
        gate.invalidate()
        self.assertTrue(gate.allows(0,known,Budget()))

    def test_exhaustive_embeddings(self):
        rng=random.Random(171071)
        for _ in range(200):
            def clauses(n,count,width):
                return {tuple(sorted(v if rng.randrange(2) else -v for v in
                                     rng.sample(range(1,n+1),rng.randint(1,width))))
                        for _ in range(count)}
            guards=tuple(sorted(clauses(3,4,3)))
            f={"n":3,"axioms":guards,"steps":((),),"edges":()}
            known=clauses(4,5,3)
            gate=IncidenceFilter(Index([f]))
            if has_embedding(f,4,known):
                self.assertTrue(gate.allows(0,known,Budget()))

    def test_cap_and_replay(self):
        self.assertIsNone(pair_histogram([(i,) for i in range(1,101)],Budget()))
        f={"n":2,"axioms":((1,2),(-1,2),(1,-2),(-1,-2)),
           "steps":((2,),(-2,),()),"edges":()}
        for solver in (indexed_reuse,reuse):
            r=solver(2,f["axioms"],Index([f]),Budget())
            self.assertEqual(r["status"],"verified")
            self.assertTrue(independent_replay(2,f["axioms"],r["proof"]))
        self.assertEqual(indexed_reuse(2,f["axioms"],Index([f]),Budget(max_steps=1))["status"],
                         "resource_exhausted")

if __name__=="__main__":
    unittest.main()
