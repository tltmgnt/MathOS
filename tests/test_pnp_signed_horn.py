import random
import unittest
from itertools import product
from mathos.research.pnp_signed_horn import propose, verify_trace, polarity, normalized, rename
from mathos.research.pnp_library_ablation import independent_replay, oracle
from mathos.research.pnp_structural_kernel import Budget


class TestSignedHorn(unittest.TestCase):
    def test_signed_wide_chain(self):
        # a conjunction body of arity 3, not merely a binary implication.
        f=[(-1,), (2,), (-3,), (1,-2,3,4), (-4,)]
        r=propose(4,f,Budget())
        self.assertEqual(r["status"],"verified")
        self.assertTrue(independent_replay(4,f,r["proof"]))
        self.assertEqual(verify_trace(4,f,r["certificate"],Budget()),r["proof"])
        self.assertEqual(propose(4,f[:-1]+[(4,)],Budget())["status"],"not_found")
        for cert in ({**r["certificate"],"signs":[True]*4},
                     {**r["certificate"],"trace":[4]},
                     {**r["certificate"],"trace":[999]},
                     {**r["certificate"],"trace":r["certificate"]["trace"]+[0]}):
            with self.assertRaises(ValueError):
                verify_trace(4,f,cert,Budget())
        self.assertEqual(propose(4,f,Budget(max_steps=1))["status"],"resource_exhausted")

    def test_recognition_against_exhaustive_signs(self):
        rng=random.Random(17471)
        for _ in range(150):
            n=rng.randint(2,6)
            f=[tuple(v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),rng.randint(1,min(3,n))))
               for _ in range(3*n)]
            cs=normalized(n,f,Budget())
            possible=any(all(sum(x>0 for x in rename(c,s))<=1 for c in cs if c is not None)
                         for s in product((-1,1),repeat=n))
            signs=polarity(n,cs,Budget())
            self.assertEqual(signs is not None,possible)
            r=propose(n,f,Budget())
            if possible:
                self.assertEqual(r["status"]=="verified",not oracle(n,f))
            else:
                self.assertEqual(r["status"],"not_renamable")
            if r["status"]=="verified":
                self.assertTrue(independent_replay(n,f,r["proof"]))

    def test_horn_subset_and_empty(self):
        f=[(1,),(-1,),(1,2,3),(-1,-2,3),(1,-2,-3),(-1,2,-3)]
        r=propose(3,f,Budget(),signed=False)
        self.assertEqual(r["status"],"verified")
        self.assertTrue(independent_replay(3,f,r["proof"]))
        self.assertEqual(propose(3,[()],Budget())["status"],"verified")
        self.assertEqual(propose(3,[],Budget())["status"],"not_found")


if __name__=="__main__":
    unittest.main()
