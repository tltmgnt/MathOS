import unittest
import random
from mathos.research.pnp_schema_portfolio import solve, verify, checked_prefix, handoff
from mathos.research.pnp_proof_library import Index
from mathos.research.pnp_structural_kernel import Budget
from mathos.research.pnp_library_ablation import oracle, independent_replay

class TestSchemaPortfolio(unittest.TestCase):
    def test_composite_route(self):
        f=[(3,),(-3,1,2),(-3,1,-2),(-3,-1,2),(-3,-1,-2)]
        r=solve(3,f,Index([]),Budget())
        self.assertEqual(r["status"],"verified")
        self.assertEqual(r["recipe"]["kind"],"composite")
        self.assertTrue(independent_replay(3,f,r["proof"]))
        self.assertEqual(solve(3,f[:-1],Index([]),Budget())["status"],"not_found")

    def test_handoff(self):
        # Resolution fragment derives a unit without unit propagation.
        # It unlocks the guarded binary contradiction.
        t={"n":2,"axioms":((1,2),(-1,2)),"steps":((2,),),"edges":()}
        index=Index([t])
        f=[(1,3),(-1,3),(-3,4,5),(-3,-4,5),(-3,4,-5),(-3,-4,-5)]
        r=handoff(5,f,index,Budget())
        self.assertEqual(r["status"],"verified")
        self.assertEqual(r["recipe"]["kind"],"handoff")
        proof=verify(5,f,index,r["recipe"],Budget())
        self.assertTrue(independent_replay(5,f,proof))
        for recipe in ({**r["recipe"],"transfers":[]},
                       {**r["recipe"],"transfers":[(0,(1,1))]},
                       {**r["recipe"],"tail":None}):
            with self.assertRaises(ValueError):
                verify(5,f,index,recipe,Budget())

    def test_random_soundness_and_budget(self):
        rng=random.Random(17671)
        t={"n":2,"axioms":((1,2),(-1,2)),"steps":((2,),),"edges":()}
        for _ in range(80):
            f=[tuple(v if rng.randrange(2) else -v for v in rng.sample(range(1,6),rng.randint(1,3)))
               for _ in range(15)]
            r=solve(5,f,Index([t]),Budget())
            if r["status"]=="verified":
                self.assertFalse(oracle(5,f))
                self.assertTrue(independent_replay(5,f,r["proof"]))
        b=Budget(max_steps=1)
        self.assertNotEqual(solve(2,[(1,),(-1,)],Index([]),b)["status"],"verified")
        self.assertLessEqual(b.steps,1)

if __name__=="__main__":
    unittest.main()
