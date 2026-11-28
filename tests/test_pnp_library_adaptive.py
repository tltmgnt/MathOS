import random
import unittest
from mathos.research.pnp_library_adaptive import search, adaptive_reuse
from mathos.research.pnp_library_ablation import independent_replay, oracle
from mathos.research.pnp_proof_library import Index
from mathos.research.pnp_structural_kernel import Budget


class TestAdaptiveReuse(unittest.TestCase):
    def setUp(self):
        self.fragment={"n":2,"axioms":((1,),(-1,2)),"steps":((2,),),"edges":()}
        self.core={"n":1,"axioms":((1,),(-1,)),"steps":((),),"edges":()}
        self.index=Index([self.core,self.fragment])

    def test_signed_search(self):
        e,status=search(self.fragment,{(-3,), (3,-2)},Budget(),subsumption=False)
        self.assertEqual(status,"matched")
        self.assertEqual(e,(-3,-2))
        e,status=search(self.fragment,{(-3,), (3,-2),(-2,)},Budget(),
                        subsumption=False)
        self.assertIsNone(e)

    def test_composition(self):
        f=[(1,),(-1,2),(-2,3),(-3,)]
        r=adaptive_reuse(3,f,self.index,Budget())
        self.assertEqual(r["status"],"verified")
        self.assertTrue(independent_replay(3,f,r["proof"]))
        self.assertFalse(oracle(3,f))

    def test_randomized(self):
        rng=random.Random(17172)
        for _ in range(100):
            f=[tuple(v if rng.randrange(2) else -v for v in rng.sample(range(1,5),rng.randint(1,3)))
               for _ in range(8)]
            r=adaptive_reuse(4,f,self.index,Budget())
            if r["status"]=="verified":
                self.assertFalse(oracle(4,f))
                self.assertTrue(independent_replay(4,f,r["proof"]))
        self.assertNotEqual(adaptive_reuse(3,[(1,),(-1,)],self.index,
                            Budget(max_steps=1))["status"],"verified")


if __name__=="__main__":
    unittest.main()
