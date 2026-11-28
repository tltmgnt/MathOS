import itertools
import json
import random
import tempfile
from pathlib import Path
import unittest

from mathos.research.pnp_constraint_algebra import MODES, propose, verify, solve, verify_solution
from mathos.research.pnp_algebra_frontier import xor_block, controls, run
from mathos.research.pnp_structural_kernel import Budget, brute


class TestAlgebra(unittest.TestCase):
    def test_every_ternary_relation(self):
        bits=list(itertools.product((False,True),repeat=3))
        for mask in range(256):
            allowed={b for i,b in enumerate(bits) if mask>>i&1}
            f=[tuple(-v if b else v for v,b in enumerate(pattern,1))
               for pattern in bits if pattern not in allowed]
            # Known closure characterizations, independent of compiler.
            maj=all(tuple(sum(x)>=2 for x in zip(a,b,c)) in allowed
                    for a,b,c in itertools.product(allowed,repeat=3))
            affine=all(tuple(x^y^z for x,y,z in zip(a,b,c)) in allowed
                       for a,b,c in itertools.product(allowed,repeat=3))
            for mode,expected in zip(MODES,(maj,affine)):
                a=propose(3,f,mode,Budget())
                self.assertEqual(a is not None,expected)
                if a is not None:
                    self.assertTrue(verify(3,f,json.loads(json.dumps(a)),Budget()))
                    self.assertEqual(not a["clauses"],bool(allowed))

    def test_random_affine_systems(self):
        rng=random.Random(707)
        for _ in range(150):
            n=rng.randint(2,8)
            f=[]
            for _ in range(rng.randint(0,12)):
                support=sorted(rng.sample(range(1,n+1),rng.randint(1,min(4,n))))
                f.extend(xor_block(support,rng.randrange(2)))
            a=propose(n,f,"affine",Budget())
            self.assertIsNotNone(a)
            self.assertTrue(verify(n,f,a,Budget()))
            self.assertEqual(not a["clauses"],brute(n,f,Budget()))

    def test_random_mixed_soundness(self):
        rng=random.Random(708)
        for _ in range(120):
            n=rng.randint(3,7)
            f=[]
            for _ in range(rng.randint(1,8)):
                if rng.randrange(2):
                    f.extend(xor_block(sorted(rng.sample(range(1,n+1),3)),rng.randrange(2)))
                else:
                    f.append(tuple(v if rng.randrange(2) else -v
                                   for v in rng.sample(range(1,n+1),2)))
            a=solve(n,f,Budget())
            if a is not None:
                self.assertTrue(verify_solution(n,f,json.loads(json.dumps(a)),Budget()))
                self.assertEqual(not a["clauses"],brute(n,f,Budget()))

    def test_global_xor_conflict(self):
        f=xor_block((1,2),0)+xor_block((2,3),0)+xor_block((1,3),1)
        a=propose(3,f,"affine",Budget())
        self.assertEqual(a["decision_certificate"]["kind"],"xor_conflict")
        self.assertTrue(verify(3,f,a,Budget()))
        with self.assertRaises(ValueError):
            verify(3,f,{**a,"decision_certificate":{"kind":"xor_conflict","rows":[0]}},Budget())
        with self.assertRaises(ValueError):
            verify(3,f,{**a,"blocks":[]},Budget())

    def test_mixed_and_unknown(self):
        for name,n,f,expected in controls():
            a=solve(n,f,Budget())
            if name=="unrecognized":
                self.assertIsNone(a)
                continue
            self.assertEqual(not a["clauses"],expected)
            self.assertTrue(verify_solution(n,f,a,Budget()))
            if name.startswith("mixed"):
                self.assertEqual(a["kind"],"conditioned")
                self.assertIsNone(solve(n,f,Budget(),condition_limit=0))
            if name=="mixed_unsat":
                with self.assertRaises(ValueError):
                    verify_solution(n,f,{**a,"branches":a["branches"][:1]},Budget())

    def test_checkpoint_governance(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"checkpoint.json"
            r=run(Budget(),checkpoint_path=p)
            self.assertEqual(r["completion"],"scoped_algebra_research_completed")
            self.assertEqual(len(r["controls"]),6)
            self.assertEqual(json.loads(p.read_text())["universal_obligation"],"unresolved")
            self.assertFalse(r["p_equals_np_established"])
            self.assertFalse(r["p_not_equals_np_established"])
            self.assertFalse(r["novel_theorem_verified"])
            self.assertEqual(run(Budget(max_steps=1))["completion"],"resource_exhausted")


if __name__=="__main__":
    unittest.main()
