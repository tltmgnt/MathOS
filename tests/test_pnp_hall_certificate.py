import copy
import json
import random
import unittest
from mathos.research import pnp_hall_certificate as hall
from mathos.research import pnp_hall_portfolio as portfolio
from mathos.research.pnp_hall_frontier import manifest, reference
from mathos.research.pnp_v16_stress import pigeon, bitset_reference
from mathos.research.pnp_structural_kernel import Budget, Exhausted
from mathos.research.pnp_unified_portfolio import DEFAULT_PLANS


def budget(steps=20_000):
    return Budget(seconds=5, max_steps=steps, max_cells=200_000)


class HallTests(unittest.TestCase):
    def test_previous_and_scaled_pigeon(self):
        for p,h in ((3,3),(4,3),(5,4),(5,5),(6,5),(7,6),(9,8),(12,11),(12,12)):
            f = pigeon(p,h)
            b = budget()
            r = hall.propose(p*h,f,b)
            self.assertEqual(r["decision"], "sat" if p<=h else "unsat")
            hall.verify(p*h,f,r,b)
            hall.verify(p*h,f,json.loads(json.dumps(r)),budget())
        with self.assertRaises(Exhausted):
            hall.propose(30,pigeon(6,5),budget(1))

    def test_deficient_subset(self):
        c = next(c for c in manifest() if c["id"] == "local_deficiency")
        r = hall.propose(c["n"],c["clauses"],budget())
        self.assertEqual(r["decision"],"unsat")
        self.assertEqual(len(r["certificate"]["groups"]),3)
        self.assertEqual(len(r["certificate"]["resources"]),2)
        self.assertFalse(reference(c))
        hall.verify(c["n"],c["clauses"],r,budget())

    def test_forged_certificates(self):
        f = pigeon(4,3)
        p = hall.propose(12,f,budget())
        for bad in ("missing_variable","duplicate_group","missing_edge","wrong_label"):
            q = copy.deepcopy(p)
            g = list(f)
            if bad == "missing_variable":
                q["certificate"]["resources"][0].pop()
            elif bad == "duplicate_group":
                q["certificate"]["groups"][1] = q["certificate"]["groups"][0]
            elif bad == "wrong_label":
                q["certificate"]["resources"][0][0] = True
            else:
                g.pop(len(q["certificate"]["groups"]))
            with self.assertRaises(ValueError):
                hall.verify(12,g,q,budget())
        with self.assertRaises(ValueError):
            hall.verify(1,[[1]],{"decision":"sat","certificate":[False]},budget())

    def test_matching_not_sufficient(self):
        f = [[1,2],[3,4],[-1,-3],[-2,-4],[-1],[-4]]
        self.assertTrue(hall.eligible(f))
        self.assertTrue(bitset_reference(4,f))
        self.assertIsNone(hall.propose(4,f,budget()))
        # A non-clique conflict path cannot be treated as one resource.
        g = [[1],[2],[3],[-1,-2],[-2,-3]]
        self.assertIsNone(hall.propose(3,g,budget()))

    def test_random_reference(self):
        rng = random.Random(181901)
        credited = 0
        for n in range(1,9):
            for _ in range(300):
                f = [[rng.choice((-1,1))*rng.randint(1,n) for _ in range(rng.randrange(1,5))]
                     for _ in range(rng.randrange(20))]
                r = hall.propose(n,f,budget())
                if r is not None:
                    credited += 1
                    hall.verify(n,f,json.loads(json.dumps(r)),budget())
                    self.assertEqual(r["decision"]=="sat",bitset_reference(n,f))
        self.assertGreater(credited,0)

    def test_integrated_fallback_and_binding(self):
        policy = {"order":[{"plan":list(p),"suggested_cap":50000} for p in DEFAULT_PLANS]}
        plan = ["min_product",8]
        for n,f,expected in ((30,pigeon(6,5),"unsat"),(2,[[1,2]],"sat"),
                (4,[[1,2],[3,4],[-1,-3],[-2,-4],[-1],[-4]],"sat")):
            r = portfolio.solve(n,f,policy,plan)
            self.assertEqual(r["decision"],expected)
            self.assertTrue(portfolio.verify(n,f,policy,plan,json.loads(json.dumps(r))))
            if n == 30:
                self.assertIsNone(r["fallback"])
            else:
                self.assertIsNotNone(r["fallback"])
            bad = copy.deepcopy(r)
            bad["work_steps"] += 1
            with self.assertRaises(ValueError):
                portfolio.verify(n,f,policy,plan,bad)

    def test_manifest(self):
        cases = manifest()
        self.assertEqual(len(cases),73)
        self.assertEqual(len({c["id"] for c in cases}),73)
        for c in cases:
            self.assertIs(type(reference(c)),bool)


if __name__ == "__main__":
    unittest.main()
