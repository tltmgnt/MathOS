import json
import random
import tempfile
from pathlib import Path
import unittest

from mathos.research.pnp_recursive_separators import search,verify_certificate,scope_obstruction,verify_obstruction
from mathos.research.pnp_recursive_frontier import family,probe,run
from mathos.research.pnp_structural_kernel import Budget,brute,Exhausted


class TestRecursive(unittest.TestCase):
    def test_connected_family(self):
        for m in (2,4,16,64):
            r=probe(m,Budget(seconds=30,max_steps=10_000_000))
            self.assertEqual(r["recursive_verified_leaves"],4*m)
            self.assertEqual(r["global_backdoor_lower"],m)
            self.assertEqual(r["artifact"]["metrics"]["max_split_depth"],2)
            self.assertTrue(verify_certificate(1+3*m,family(m),json.loads(json.dumps(r["artifact"])),Budget()))
            self.assertTrue(verify_obstruction(1+3*m,family(m),r["obstruction"],Budget()))

    def test_random_soundness(self):
        rng=random.Random(901)
        for _ in range(180):
            n=rng.randrange(9)
            lits=[v for v in range(-n,n+1) if v]
            f=[rng.choices(lits,k=rng.randrange(6)) if lits else []
               for _ in range(rng.randrange(14))]
            a=search(n,f,Budget(),depth=3)
            self.assertTrue(verify_certificate(n,f,json.loads(json.dumps(a)),Budget()))
            if a["decision"]!="unknown":
                self.assertEqual(a["decision"]=="sat",brute(n,f,Budget()))

    def test_three_valued(self):
        self.assertEqual(search(7,family(2),Budget(),depth=1)["decision"],"unknown")
        self.assertEqual(search(7,family(2),Budget(),depth=2)["decision"],"sat")
        self.assertEqual(search(7,family(2)+[(1,),(-1,)],Budget(),depth=2)["decision"],"unsat")
        a=search(4,[(1,),(-1,),(2,3,4)],Budget(),depth=0)
        self.assertEqual(a["decision"],"unsat")
        self.assertEqual(a["metrics"]["unknown_leaves"],1)
        # One satisfied assignment to x1 and one unrecognized residual.
        a=search(4,[(1,2,3,4)],Budget(),depth=1)
        self.assertEqual(a["decision"],"sat")
        self.assertEqual(a["metrics"]["unknown_leaves"],1)
        self.assertEqual(search(0,[],Budget())["decision"],"sat")
        self.assertEqual(search(0,[()],Budget())["decision"],"unsat")

    def test_tampering(self):
        f=family(2)
        a=search(7,f,Budget(),depth=2)
        t=a["tree"]
        for forged in (
            {**a,"decision":"unsat"},
            {**a,"tree":{**t,"branches":t["branches"][:1]}},
            {**a,"tree":{**t,"separator_parts":0}},
            {**a,"tree":{**t,"variable":2}},
            {**a,"metrics":{**a["metrics"],"leaves":0}},
            {**a,"depth_limit":0},
        ):
            with self.assertRaises(ValueError):
                verify_certificate(7,f,forged,Budget())
        c=scope_obstruction(7,f,Budget())
        with self.assertRaises(ValueError):
            verify_obstruction(7,f,{**c,"global_backdoor_lower":3},Budget())
        # A second clause on exactly the same support invalidates exclusivity.
        f=[(1,2,3),(1,2,-3)]
        c=scope_obstruction(3,f,Budget())
        self.assertEqual(c["global_backdoor_lower"],0)
        with self.assertRaises(ValueError):
            verify_obstruction(3,f,{**c,"clause_indices":[0],"global_backdoor_lower":1},Budget())

    def test_limits_and_checkpoint(self):
        with self.assertRaises(Exhausted):
            search(7,family(2),Budget(),nodes=1)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"checkpoint.json"
            r=run(Budget(),sizes=(2,4),checkpoint_path=p)
            self.assertEqual(r["completion"],"scoped_recursive_research_completed")
            self.assertTrue(all(o["status"]=="unresolved" for o in r["obligations"]))
            self.assertFalse(r["p_equals_np_established"])
            self.assertFalse(r["p_not_equals_np_established"])
            self.assertEqual(json.loads(p.read_text())["universal_obligation"],"unresolved")
            r=run(Budget(max_steps=1),sizes=(2,),checkpoint_path=p)
            self.assertEqual(r["completion"],"resource_exhausted")


if __name__=="__main__":
    unittest.main()
