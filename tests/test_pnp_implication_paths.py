import copy
import random
import unittest
from mathos.research.pnp_implication_paths import propose, verify_paths
from mathos.research.pnp_library_ablation import independent_replay, oracle
from mathos.research.pnp_structural_kernel import Budget


class TestImplicationPaths(unittest.TestCase):
    def test_unbounded_schema_controls(self):
        for n in (1,2,10,64,128):
            f=[(1,)]+[(-i,i+1) for i in range(1,n)]+[(-n,)]
            r=propose(n,f,Budget())
            self.assertEqual(r["status"],"verified")
            self.assertEqual(verify_paths(n,f,r["certificate"],Budget()),r["proof"])
            self.assertTrue(independent_replay(n,f,r["proof"]))
            self.assertEqual(propose(n,f[:-1]+[(n,)],Budget())["status"],"not_found")

    def test_signed_mixed_formula_and_forgery(self):
        f=[(-1,), (1,2), (-2,), (2,3,4)]
        r=propose(4,f,Budget())
        self.assertEqual(r["status"],"verified")
        self.assertTrue(independent_replay(4,f,r["proof"]))
        cert=r["certificate"]
        with self.assertRaises(ValueError):
            verify_paths(4,f,{**cert,"pivot":True},Budget())
        with self.assertRaises(ValueError):
            verify_paths(4,[(1,2),(-2,)],cert,Budget())
        for bad in ([0,-1],[True,-1],[1,4,-1],[1,1,-1]):
            with self.assertRaises(ValueError):
                verify_paths(4,f,{**cert,"forward":bad},Budget())
        self.assertEqual(propose(4,[()],Budget())["status"],"input_empty")
        self.assertEqual(propose(4,[],Budget())["status"],"not_found")
        self.assertEqual(propose(4,f,Budget(max_steps=1))["status"],"resource_exhausted")

    def test_randomized_complete_on_binary(self):
        rng=random.Random(17371)
        for _ in range(160):
            n=rng.randint(2,7)
            f=[tuple(v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),rng.randint(1,2)))
               for _ in range(2*n)]
            r=propose(n,f,Budget())
            self.assertEqual(r["status"]=="verified",not oracle(n,f))
            if r["status"]=="verified":
                self.assertTrue(independent_replay(n,f,r["proof"]))

    def test_ternary_only_unknown(self):
        f=[(1,2,3),(-1,-2,-3)]
        self.assertEqual(propose(3,f,Budget())["status"],"not_found")


if __name__=="__main__":
    unittest.main()
