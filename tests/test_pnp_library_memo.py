import random
import unittest
from mathos.research.pnp_library_memo import memo_find,memo_reuse
from mathos.research.pnp_proof_library import find,Index,mapped
from mathos.research.pnp_structural_kernel import Budget
from mathos.research.pnp_library_ablation import independent_replay

class TestMemo(unittest.TestCase):
    def test_repeated_states_and_cutoff(self):
        f={"n":2,"axioms":((1,2),)*4,"steps":((1,2),),"edges":()}
        known={(-2,-1),(-2,1),(-1,2),(1,2),(-2,),(-1,),(1,),(2,)}
        stats={}
        self.assertIsNone(memo_find(f,2,known,Budget(),limit=100000,stats=stats))
        self.assertGreater(stats["hits"],0)
        self.assertGreater(stats["stored"],0)
        tiny={}
        self.assertIsNone(memo_find(f,2,known,Budget(),limit=1,stats=tiny))
        self.assertEqual(tiny["stored"],0)
        self.assertEqual(tiny["cutoffs"],1)

    def test_same_order_when_search_completes(self):
        rng=random.Random(17971)
        f={"n":2,"axioms":((1,2),(-1,2)),"steps":((2,),),"edges":()}
        for _ in range(150):
            known={tuple(sorted(v if rng.randrange(2) else -v for v in rng.sample(range(1,5),rng.randint(1,3))))
                   for _ in range(8)}
            for sub in (False,True):
                a=find(f,4,known,Budget(),subsumption=sub,limit=100000)
                b=memo_find(f,4,known,Budget(),subsumption=sub,limit=100000)
                self.assertEqual(a,b)
                if b is not None:
                    for guard in f["axioms"]:
                        self.assertTrue(any(set(c)<=set(mapped(guard,b)) for c in known))

    def test_replay(self):
        f={"n":2,"axioms":((1,2),(-1,2),(1,-2),(-1,-2)),"steps":((2,),(-2,),()),"edges":()}
        r=memo_reuse(2,f["axioms"],Index([f]),Budget())
        self.assertEqual(r["status"],"verified")
        self.assertTrue(independent_replay(2,f["axioms"],r["proof"]))
        self.assertEqual(memo_reuse(2,f["axioms"],Index([f]),Budget(max_steps=1))["status"],
                         "resource_exhausted")

if __name__=="__main__":
    unittest.main()
