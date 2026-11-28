import copy
import json
import random
import tempfile
from pathlib import Path
import unittest

from mathos.research.pnp_unified_portfolio import run,verify_report,DEFAULT_PLANS
from mathos.research.pnp_general_frontier import run as frontier,controls
from mathos.research.pnp_structural_kernel import Budget,brute


def budget():
    return Budget(seconds=30,max_steps=20_000_000,max_cells=200_000)


class TestUnified(unittest.TestCase):
    def test_control_portfolio(self):
        for name,n,f,expected in controls():
            r=run(n,f,budget())
            self.assertEqual(r["decision"],"sat" if expected else "unsat")
            self.assertEqual(len(r["entries"]),len(DEFAULT_PLANS))
            self.assertTrue(verify_report(n,f,json.loads(json.dumps(r)),budget()))
            self.assertEqual({e["decision"] for e in r["entries"]}-{ "unknown" },{r["decision"]})

    def test_reduction_chain(self):
        f=[(1,),(-1,2),(-2,3),(-3,)]
        r=run(3,f,budget(),plans=(("unit","recursive"),))
        self.assertEqual(r["decision"],"unsat")
        self.assertTrue(verify_report(3,f,r,budget()))
        entry=r["entries"][0]
        self.assertTrue(entry["reduction"]["steps"])
        forged=copy.deepcopy(r)
        forged["entries"][0]["reduction"]["clauses"]=()
        with self.assertRaises(ValueError):
            verify_report(3,f,forged,budget())

    def test_unknown_exhaustion(self):
        f=[(1,2,3)]
        r=run(3,f,budget(),plans=(("none","recursive"),),depth=0)
        self.assertEqual(r["decision"],"unknown")
        self.assertTrue(verify_report(3,f,r,budget()))
        b=Budget(max_steps=1)
        r=run(3,f,b)
        self.assertEqual(r["decision"],"unknown")
        self.assertTrue(all(e["status"]=="resource_exhausted" for e in r["entries"]))
        self.assertLessEqual(b.steps,b.max_steps)
        self.assertTrue(verify_report(3,f,r,budget()))

    def test_tampered_report(self):
        f=[(1,2),(-1,2)]
        r=run(2,f,budget(),plans=(("none","two_sat"),("none","recursive")))
        for field,value in (("decision","unsat"),("p_equals_np_established",True),
                            ("input_sha256","0"*64),("entries",r["entries"][:1])):
            with self.assertRaises(ValueError):
                verify_report(2,f,{**r,field:value},budget())
        with self.assertRaises(ValueError):
            verify_report(2,f+[(-2,)],r,budget())
        forged=copy.deepcopy(r)
        forged["entries"][0]["proof"]["assignment"]=[False,False]
        with self.assertRaises(ValueError):
            verify_report(2,f,forged,budget())

    def test_random_soundness(self):
        rng=random.Random(1010)
        for _ in range(120):
            n=rng.randrange(8)
            lits=[x for x in range(-n,n+1) if x]
            f=[rng.choices(lits,k=rng.randrange(5)) if lits else []
               for _ in range(rng.randrange(12))]
            r=run(n,f,budget())
            self.assertTrue(verify_report(n,f,r,budget()))
            if r["decision"]!="unknown":
                self.assertEqual(r["decision"]=="sat",brute(n,f,budget()))

    def test_frontier_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"report.json"
            r=frontier(budget(),checkpoint_path=p)
            self.assertEqual(r["completion"],"scoped_portfolio_research_completed")
            self.assertEqual(len(r["controls"]),4)
            self.assertEqual(r["scoped_challenge"]["status"],"observed_unrecognized")
            self.assertTrue(all(x["status"]=="unresolved" for x in r["next_obligations"]))
            self.assertFalse(json.loads(p.read_text())["p_not_equals_np_established"])


if __name__=="__main__":
    unittest.main()
