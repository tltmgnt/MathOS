import random
import unittest
from mathos.research.pnp_composite_paths import propose, verify_recipe
from mathos.research.pnp_implication_paths import propose as raw_paths
from mathos.research.pnp_library_ablation import independent_replay, oracle
from mathos.research.pnp_structural_kernel import Budget


class TestCompositePaths(unittest.TestCase):
    def test_genuine_composition(self):
        f=[(3,),(-3,1,2),(-3,1,-2),(-3,-1,2),(-3,-1,-2)]
        self.assertEqual(raw_paths(3,f,Budget())["status"],"not_found")
        self.assertEqual(propose(3,f,Budget(),compose=False)["status"],"not_found")
        r=propose(3,f,Budget())
        self.assertEqual(r["status"],"verified")
        self.assertEqual(r["recipe"]["kind"],"paths")
        self.assertEqual(len(r["recipe"]["reductions"]),4)
        self.assertTrue(independent_replay(3,f,r["proof"]))
        self.assertTrue(oracle(3,f[:-1]))
        self.assertEqual(propose(3,f[:-1],Budget())["status"],"not_found")
        for bad in ({**r["recipe"],"units":[]},
                    {**r["recipe"],"reductions":[(0,(1,2))]},
                    {**r["recipe"],"reductions":[]},
                    {**r["recipe"],"units":[True]}):
            with self.assertRaises(ValueError):
                verify_recipe(3,f,bad,Budget())

    def test_unit_only(self):
        for f in ([(1,),(-1,2),(-2,)], [()], [(1,),(-1,)]):
            r=propose(2,f,Budget())
            self.assertEqual(r["recipe"]["kind"],"unit")
            self.assertTrue(independent_replay(2,f,r["proof"]))
        self.assertEqual(propose(2,[(1,)],Budget(max_steps=1))["status"],"resource_exhausted")

    def test_randomized(self):
        rng=random.Random(17571)
        for _ in range(200):
            n=rng.randint(2,7)
            f=[tuple(v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),rng.randint(1,min(4,n))))
               for _ in range(3*n)]
            r=propose(n,f,Budget())
            if r["status"]=="verified":
                self.assertFalse(oracle(n,f))
                self.assertTrue(independent_replay(n,f,r["proof"]))


if __name__=="__main__":
    unittest.main()
