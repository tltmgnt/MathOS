"""Meter and certificate regression tests (no promotion of candidate)."""
import copy
import random
import unittest
from itertools import combinations, product

from mathos.research.pnp_bounded_matching import Meter, Limit, propose, check, solve, replay


def encode(ns, holes):
    groups, buckets, v = [], [[] for _ in range(holes)], 0
    for row in ns:
        g = []
        for j in row:
            v += 1
            g.append(v)
            buckets[j].append(v)
        groups.append(g)
    return v, groups + [[-x,-y] for b in buckets for x,y in combinations(b,2)]


def oracle(ns):
    return "sat" if any(len(set(a))==len(a) for a in product(*ns)) else "unsat"


def scramble(n,f,rng):
    p=list(range(1,n+1));rng.shuffle(p)
    p=[x if rng.randrange(2) else -x for x in p]
    g=[[p[abs(x)-1]*(1 if x>0 else -1) for x in c] for c in f]
    for c in g:rng.shuffle(c)
    rng.shuffle(g)
    return g


class BoundedMatching(unittest.TestCase):
    def checked(self,n,f,d):
        r=solve(n,f,steps=100_000,seconds=2)
        self.assertEqual(r["decision"],d)
        self.assertLessEqual(r["work_steps"],100_000)
        self.assertTrue(replay(n,f,r,steps=100_000))

    def test_exhaustive_and_signed_permutations(self):
        rng=random.Random(183511)
        opts=[list(x) for k in (3,4) for x in combinations(range(4),k)]
        for k in range(1,5):
            for ns in product(opts,repeat=k):
                n,f=encode(ns,4);d=oracle(ns)
                self.checked(n,f,d)
                self.checked(n,scramble(n,f,rng),d)
        for _ in range(400):
            h=rng.randint(3,7)
            ns=[rng.sample(range(h),rng.randint(3,h)) for _ in range(rng.randint(1,8))]
            n,f=encode(ns,h)
            self.checked(n,scramble(n,f,rng),oracle(ns))

    def test_budget_edges(self):
        n,f=encode([list(range(5))]*6,5)
        b=Meter(100_000,2)
        cert=propose(n,f,b);p=b.used
        check(n,f,cert,b);full=b.used
        for q in (1,p-1,p,full-1,full):
            r=solve(n,f,steps=q,seconds=2)
            self.assertEqual(r["decision"],"unsat" if q==full else "unknown")
            self.assertEqual(r["work_steps"],q)
            self.assertTrue(replay(n,f,r,steps=q))
        self.assertIsNone(solve(n,f,steps=p,seconds=2)["certificate"])
        self.assertEqual(solve(513,[],steps=100_000,seconds=2)["status"],"resource_exhausted")

    def test_invalid_certificates(self):
        n,f=encode([list(range(5))]*6,5)
        r=solve(n,f,steps=100_000,seconds=2)
        cases=[dict(r,work_steps=1),dict(r,decision="sat"),
               dict(r,certificate=dict(r["certificate"],buckets=r["certificate"]["buckets"][:-1]))]
        for bad in cases:
            with self.assertRaises((ValueError,Limit)):
                replay(n,f,bad,steps=100_000)
        with self.assertRaises(ValueError):
            replay(n,f[:-1],r,steps=100_000)
        with self.assertRaises(ValueError):
            solve(3,[[0]],steps=100_000,seconds=2)
        self.assertEqual(solve(3,[[1,2,3],[1,2]],steps=100_000,seconds=2)["status"],"unrecognized")


if __name__=="__main__":unittest.main()
