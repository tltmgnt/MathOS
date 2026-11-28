import copy
import json
import random
import unittest
from itertools import combinations

from mathos.research.pnp_generalized_escape import propose, verify
from mathos.research.pnp_semantic_escape import propose as old_propose
from mathos.research.pnp_structural_kernel import Budget, Exhausted, brute


def paired_blocks(count, unsat=False):
    f = []
    for k in range(count):
        # Signed, complete-primal blocks: alternating planted assignment.
        vs = [6*k+i for i in range(1, 7)]
        for q in combinations(vs, 3):
            patterns = [(1,1,1), (-1,-1,-1)] if unsat and k == count-1 else [
                tuple(-1 if i == j else 1 for i in range(3)) for j in range(3)] + [
                tuple(1 if i == j else -1 for i in range(3)) for j in range(3)]
            for signs in patterns:
                f.append([v*s*(-1 if v%2 else 1) for v,s in zip(q,signs)])
    return 6*count, f


def separator(unsat=False):
    f = []
    for a in range(2, 20, 2):
        b = a+1
        f.extend([[1,a,b], [-1,-a,-b], [a], [-b]])
    if unsat:
        f.extend([[1], [-1]])
    return 19, f


class TestGeneralizedEscape(unittest.TestCase):
    def check_certificate(self, n, f, expected, depth=2):
        a = propose(n, f, Budget(), depth=depth)
        self.assertIsNotNone(a)
        a = json.loads(json.dumps(a))
        self.assertTrue(verify(n, f, a, Budget()))
        self.assertEqual(a["kind"], "sat_witness" if expected else "unsat_tree")
        self.assertEqual(a["clauses"], [] if expected else [[]])
        return a

    def test_paired_blocks_beyond_v4(self):
        for unsat in (False, True):
            n,f = paired_blocks(5, unsat)
            self.assertIsNone(old_propose(n,f,Budget()))
            self.check_certificate(n,f,not unsat,depth=0)

    def test_separator_and_unknown(self):
        for unsat in (False, True):
            n,f = separator(unsat)
            self.assertIsNone(propose(n,f,Budget(),depth=0))
            a = self.check_certificate(n,f,not unsat,depth=1)
            if unsat:
                self.assertEqual(a["proof"]["rule"], "split")
                bad = copy.deepcopy(a)
                del bad["proof"]["positive"]
                with self.assertRaises(ValueError):
                    verify(n,f,bad,Budget())

    def test_reference_random(self):
        rng = random.Random(501)
        for _ in range(220):
            n = rng.randrange(8)
            literals = [i for i in range(-n,n+1) if i]
            f = [rng.choices(literals,k=rng.randrange(5)) if literals else []
                 for _ in range(rng.randrange(15))]
            self.check_certificate(n,f,brute(n,f,Budget()))

    def test_forged_witness_and_refutation(self):
        n,f = 2, [[1],[-2]]
        a = self.check_certificate(n,f,True)
        for proof in ([1,2], [True,-2], [1,1]):
            with self.assertRaises(ValueError):
                verify(n,f,{**a,"proof":proof},Budget())
        b = {**a,"kind":"unsat_tree","clauses":[[]],"proof":{"rule":"enumerate"}}
        with self.assertRaises(ValueError):
            verify(n,f,b,Budget())
        b["proof"] = {"rule":"subset","indices":[-1],"child":{"rule":"enumerate"}}
        with self.assertRaises(ValueError):
            verify(n,f,b,Budget())

    def test_budget_and_limits(self):
        n,f = separator()
        with self.assertRaises(Exhausted):
            propose(n,f,Budget(max_steps=1))
        with self.assertRaises(ValueError):
            propose(n,f,Budget(),depth=5)
        a = self.check_certificate(n,f,True,depth=1)
        with self.assertRaises(Exhausted):
            verify(n,f,a,Budget(max_steps=1))


if __name__ == "__main__":
    unittest.main()
