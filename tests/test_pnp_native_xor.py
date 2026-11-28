import copy
import json
import random
import unittest
from itertools import product
from mathos.research import pnp_native_xor_conflict as native
from mathos.research import pnp_native_xor_portfolio as portfolio
from mathos.research.pnp_native_xor_frontier import manifest,reference,control,hidden
from mathos.research.pnp_xor_frontier import encode
from mathos.research.pnp_xor_subsystem import extract
from mathos.research.pnp_conflict_frontier import bitset20
from mathos.research.pnp_structural_kernel import Budget
from mathos.research.pnp_unified_portfolio import DEFAULT_PLANS


def budget():
    return Budget(seconds=5,max_steps=100000,max_cells=200000)


class NativeTests(unittest.TestCase):
    def test_native_unit_and_conflict(self):
        f=encode([1,2,3],0)+encode([1,2,4],0)
        rows=extract(f,budget())
        masks=native.row_masks(rows)
        inferred=native.scan(masks,[3],budget())
        self.assertIn(4,[lit for _,lit in inferred])
        for event,lit in inferred:
            native.verify_explanation(4,rows,event,budget())
        [(event,lit)]=native.scan(masks,[3,-4],budget())
        self.assertIsNone(lit)
        self.assertEqual(set(event["clause"]),{-3,4})
        native.verify_explanation(4,rows,event,budget())
        bad=copy.deepcopy(event)
        bad["clause"]=[3,4]
        with self.assertRaises(ValueError):
            native.verify_explanation(4,rows,bad,budget())

    def test_manual_mixed_proof_and_forgery(self):
        f=encode([1,2,3],0)+encode([1,2,4],0)+[[3,4],[-3,-4]]
        rows=[r for r in extract(f,budget()) if len(r["scope"])==3]
        proof={"decision":"unsat","certificate":{"rows":rows,"events":[
            {"kind":"xor","clause":[-3,4],"rows":[0,1]},
            {"kind":"xor","clause":[-4,3],"rows":[0,1]},
            {"kind":"rup","clause":[-3]},
            {"kind":"rup","clause":[]}]}}
        self.assertFalse(bitset20(4,f))
        native.verify(4,f,json.loads(json.dumps(proof)),budget())
        for mutation in ("source","sign","rows","order","final"):
            q=copy.deepcopy(proof)
            p=q["certificate"]
            if mutation=="source": p["rows"][0]["sources"].pop()
            elif mutation=="sign": p["events"][0]["clause"]=[3,4]
            elif mutation=="rows": p["events"][0]["rows"]=[0,0]
            elif mutation=="order": p["events"].insert(0,p["events"].pop(2))
            else: p["events"].pop()
            with self.assertRaises(ValueError):
                native.verify(4,f,q,budget())

    def test_random_scan_semantics(self):
        rng=random.Random(192209)
        for n in range(3,8):
            for _ in range(60):
                f=[]
                for _ in range(rng.randrange(1,8)):
                    f.extend(encode(sorted(rng.sample(range(1,n+1),3)),rng.randrange(2)))
                rows=extract(f,budget())
                trail=[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),rng.randrange(n+1))]
                models=[a for a in product((False,True),repeat=n)
                        if all(a[abs(x)-1]==(x>0) for x in trail)
                        and all(any(a[abs(x)-1]==(x>0) for x in c) for c in f)]
                events=native.scan(native.row_masks(rows),trail,budget())
                for event,lit in events:
                    native.verify_explanation(n,rows,event,budget())
                    if lit is None: self.assertFalse(models)
                    else: self.assertTrue(all(a[abs(lit)-1]==(lit>0) for a in models))
                if not models:
                    self.assertTrue(any(lit is None for _,lit in events))
                elif events:
                    self.assertTrue(all(lit is not None for _,lit in events))

    def test_small_mixed_exhaustive_reference(self):
        rng=random.Random(192210)
        for n in range(3,9):
            for _ in range(100):
                f=[]
                for _ in range(rng.randrange(1,6)):
                    f.extend(encode(sorted(rng.sample(range(1,n+1),3)),rng.randrange(2)))
                f += [[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3)]
                      for _ in range(rng.randrange(14))]
                r=native.attempt(n,f,100000,5)
                self.assertNotEqual(r["decision"],"unknown")
                native.replay(n,f,json.loads(json.dumps(r)),100000)
                self.assertEqual(r["decision"]=="sat",bitset20(n,f))

    def test_native_proof_and_portfolio(self):
        f=control(5,True)
        r=native.attempt(21,f,100000,5)
        self.assertEqual(r["decision"],"unsat")
        self.assertGreater(r["proof"]["xor_events"],0)
        native.replay(21,f,json.loads(json.dumps(r)),100000)
        policy={"order":[{"plan":list(p),"suggested_cap":50000} for p in DEFAULT_PLANS]}
        plan=["min_product",8]
        for n,f,want in ((21,f,"unsat"),(21,control(5,False),"sat"),(2,[[1,2]],"sat")):
            p=portfolio.solve(n,f,policy,plan)
            self.assertEqual(p["decision"],want)
            portfolio.verify(n,f,policy,plan,json.loads(json.dumps(p)))
            q=copy.deepcopy(p)
            q["work_steps"]+=1
            with self.assertRaises(ValueError):
                portfolio.verify(n,f,policy,plan,q)
        u=native.attempt(21,control(5,True),1,5)
        self.assertEqual(u["decision"],"unknown")
        native.replay(21,control(5,True),u,1)

    def test_manifest_and_hidden(self):
        cases=manifest()
        self.assertEqual(len(cases),191)
        self.assertEqual(len({c["id"] for c in cases}),191)
        for c in cases:
            self.assertIs(type(reference(c)),bool)
        for f in ([[1,2]],[[1],[-1]]):
            self.assertEqual(bitset20(8,hidden(2,f,1)),bitset20(2,f))


if __name__=="__main__":
    unittest.main()
