import copy
import random
import unittest

from mathos.research.pnp_adaptive_separators import adaptive, dense_control, experiment, rank, separator_family
from mathos.research.pnp_generalized_escape import propose, verify
from mathos.research.pnp_structural_kernel import Budget, Exhausted, brute, normalize


def budget():
    return Budget(seconds=30, max_steps=20_000_000)


class TestAdaptiveSeparators(unittest.TestCase):
    def test_paired_separator_controls(self):
        for contradictory in (False, True):
            n,f = separator_family(contradictory=contradictory)
            self.assertIsNone(propose(n,f,budget(),depth=1))
            a = adaptive(n,f,budget(),depth=1)
            self.assertEqual(a["choices"][0]["variable"], 1)
            self.assertEqual(a["choices"][0]["score"][0], 6)
            cert = a["certificate"]
            self.assertEqual(cert["kind"], "unsat_tree" if contradictory else "sat_witness")
            self.assertTrue(verify(n,f,cert,budget()))
            if contradictory:
                self.assertEqual(cert["proof"]["variable"], 1)
                bad = copy.deepcopy(cert)
                bad["proof"]["variable"] = n+1
                with self.assertRaises(ValueError):
                    verify(n,f,bad,budget())

    def test_dense_unknown(self):
        n,f = dense_control()
        a = adaptive(n,f,budget(),depth=1)
        self.assertIsNone(a["certificate"])
        self.assertFalse(a["certificate_replayed"])
        self.assertEqual(a["choices"][0]["score"][0],9)

    def test_rank_independent_reference(self):
        # Reference computes connected components by pairwise primal adjacency,
        # independently of the incidence traversal used by the ranking.
        rng = random.Random(603)
        for _ in range(30):
            n = rng.randrange(2,10)
            literals = [x for x in range(-n,n+1) if x]
            _,f,_ = normalize(n,[rng.choices(literals,k=rng.randrange(1,5))
                                  for _ in range(20)])
            def profile(v, value):
                graph = {}
                for c in f:
                    if any(abs(x)==v and (x>0)==value for x in c):
                        continue
                    vs = {abs(x) for x in c if abs(x)!=v}
                    if not vs:
                        return (0,0,0)
                    for x in vs:
                        graph.setdefault(x,set()).update(vs-{x})
                widths = []
                while graph:
                    seen, stack = set(), [next(iter(graph))]
                    while stack:
                        x = stack.pop()
                        if x not in seen:
                            seen.add(x)
                            stack.extend(graph.pop(x,set())-seen)
                    widths.append(len(seen))
                return max(widths,default=0),sum(w for w in widths if w>8),sum(widths)
            rows = rank(f,budget())
            self.assertEqual({r["variable"] for r in rows},{abs(x) for c in f for x in c})
            for row in rows:
                v = row["variable"]
                self.assertEqual(row["negative"],profile(v,False))
                self.assertEqual(row["positive"],profile(v,True))
            self.assertEqual(rows, sorted(rows,key=lambda r:r["score"]))

    def test_permuted_separator_and_budget(self):
        n,f = separator_family()
        p = list(range(1,n+1))
        random.Random(604).shuffle(p)
        g = [[p[abs(x)-1]*(1 if x>0 else -1) for x in c] for c in f]
        a = adaptive(n,g,budget(),depth=1)
        self.assertEqual(a["choices"][0]["variable"],p[0])
        self.assertTrue(a["certificate_replayed"])
        with self.assertRaises(Exhausted):
            adaptive(n,g,Budget(max_steps=1),depth=1)

    def test_small_reference(self):
        rng = random.Random(605)
        for _ in range(60):
            n = rng.randrange(1,9)
            lits = [x for x in range(-n,n+1) if x]
            f = [rng.choices(lits,k=rng.randrange(1,5)) for _ in range(12)]
            a = adaptive(n,f,budget())
            self.assertTrue(a["certificate_replayed"])
            self.assertEqual(a["certificate"]["kind"]=="sat_witness",brute(n,f,budget()))

    def test_report(self):
        r = experiment()
        self.assertEqual(r["universal_obligation"],"unresolved")
        self.assertEqual([x["frequency"]["status"] for x in r["controls"]],["unknown"]*3)
        self.assertEqual([x["adaptive"]["status"] for x in r["controls"]],
                         ["sat_witness","unsat_tree","unknown"])


if __name__ == "__main__":
    unittest.main()
