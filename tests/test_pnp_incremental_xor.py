import copy
import json
import random
import unittest
from mathos.research import pnp_native_xor_conflict as native
from mathos.research import pnp_incremental_xor_state as inc
from mathos.research.pnp_native_xor_frontier import control
from mathos.research.pnp_xor_subsystem import extract
from mathos.research.pnp_xor_frontier import encode
from mathos.research.pnp_conflict_frontier import bitset20
from mathos.research.pnp_structural_kernel import Budget, Exhausted


def budget(steps=4_000_000):
    return Budget(seconds=15,max_steps=steps,max_cells=200_000)


def label(events):
    return None if any(lit is None for _,lit in events) else {lit for _,lit in events}


def reference(n,rows,trail):
    models=[a for a in range(1<<n)
            if all(bool(a>>(abs(x)-1)&1)==(x>0) for x in trail)
            and all((m&a).bit_count()%2==r for m,r in rows)]
    if not models:
        return None
    return {v if models[0]>>(v-1)&1 else -v for v in range(1,n+1)
            if v not in {abs(x) for x in trail}
            and all((a>>(v-1)&1)==(models[0]>>(v-1)&1) for a in models)}


class IncrementalTests(unittest.TestCase):
    def test_rollback_exhaustive(self):
        rng=random.Random(192309)
        for n in range(3,9):
            for _ in range(100):
                rows=[(rng.randrange(1<<n),rng.randrange(2)) for _ in range(rng.randrange(1,n+3))]
                witnesses=[{"scope":list(inc.indices(m)),"rhs":r} for m,r in rows]
                b=budget()
                s=inc.Incremental(rows,b)
                trail=[]
                for _ in range(30):
                    if trail and rng.random()<.35:
                        trail=trail[:rng.randrange(len(trail))]
                    elif len(trail)<n:
                        v=rng.choice([v for v in range(1,n+1) if v not in {abs(x) for x in trail}])
                        trail.append(v if rng.randrange(2) else -v)
                    events=s.sync(trail,b)
                    self.assertEqual(label(events),reference(n,rows,trail))
                    self.assertEqual(label(events),label(native.scan(rows,trail,b)))
                    for event,_ in events:
                        native.verify_explanation(n,witnesses,json.loads(json.dumps(event)),b)

    def test_root_conflict_and_recovery(self):
        b=budget()
        s=inc.Incremental([(3,0)],b)
        self.assertEqual(label(s.sync([1,-2],b)),None)
        self.assertEqual(label(s.sync([1],b)),{2})
        self.assertEqual(label(s.sync([-1],b)),{-2})
        self.assertEqual(label(s.sync([],b)),set())
        s=inc.Incremental([(3,0),(3,1)],b)
        for trail in ([],[1],[1,-2],[]):
            self.assertIsNone(label(s.sync(trail,b)))

    def test_sparse_steps(self):
        for k in (16,32,64,96):
            rows=[(7<<(3*i),i%2) for i in range(k)]
            b,other=budget(),budget()
            state=inc.Incremental(rows,b)
            trail=[]
            def check():
                self.assertEqual(label(state.sync(trail,b)),label(native.scan(rows,trail,other)))
            check()
            for i in range(k):
                trail.append(3*i+1)
                check()
            for i in range(k):
                trail.append(-(3*i+2))
                check()
            trail=trail[:k]
            check()
            for i in range(k):
                trail.append(3*i+2)
                check()
            self.assertLess(b.steps,other.steps)

    def test_compressed_proof(self):
        f=control(5,True)
        raw=inc.attempt(22,f,100000,5,prune=False)
        pruned=inc.attempt(22,f,100000,5)
        for r in (raw,pruned):
            self.assertEqual(r["decision"],"unsat")
            native.replay(22,f,json.loads(json.dumps(r)),100000)
        a,c=(r["proof"]["certificate"] for r in (raw,pruned))
        self.assertLess(len(c["rows"]),len(a["rows"]))
        self.assertEqual([e["clause"] for e in a["events"]],[e["clause"] for e in c["events"]])
        self.assertLess(len(json.dumps(c)),len(json.dumps(a)))
        bad=copy.deepcopy(pruned)
        event=next(e for e in bad["proof"]["certificate"]["events"] if e["kind"]=="xor")
        event["rows"]=[len(c["rows"])]
        with self.assertRaises(ValueError):
            native.replay(22,f,bad,100000)

    def test_random_integrated_and_budget(self):
        rng=random.Random(192310)
        for n in range(3,9):
            for _ in range(50):
                f=[]
                for _ in range(rng.randrange(1,6)):
                    f.extend(encode(sorted(rng.sample(range(1,n+1),3)),rng.randrange(2)))
                f += [[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3)]
                      for _ in range(rng.randrange(14))]
                r=inc.attempt(n,f,100000,5)
                self.assertNotEqual(r["decision"],"unknown")
                self.assertEqual(r["decision"]=="sat",bitset20(n,f))
                native.replay(n,f,json.loads(json.dumps(r)),100000)
        r=inc.attempt(22,control(5,True),1,5)
        self.assertEqual(r["decision"],"unknown")
        native.replay(22,control(5,True),r,1)


if __name__=="__main__":
    unittest.main()
