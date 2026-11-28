import json
import random
import tempfile
from pathlib import Path
import unittest

from mathos.research.pnp_compositional import search, verify_certificate, isolated_obstruction, verify_obstruction
from mathos.research.pnp_compositional_frontier import family, probe, run
from mathos.research.pnp_structural_kernel import Budget, brute


class TestComposition(unittest.TestCase):
    def test_family_scaling(self):
        for m in (1,4,16,64):
            r=probe(m,Budget(seconds=20,max_steps=5_000_000))
            self.assertEqual(r["global_backdoor_lower"],m)
            self.assertEqual(r["componentwise_verified_leaf_count"],2*m)
            self.assertEqual(r["global_full_assignment_count"],2**m)
            self.assertTrue(verify_certificate(3*m,family(m),json.loads(json.dumps(r["artifact"])),Budget()))
            self.assertTrue(verify_obstruction(3*m,family(m),r["obstruction"],Budget()))

    def test_connected_backdoor(self):
        f=[(1,2,3),(4,5,6),(3,4)]
        a=search(6,f,Budget(),k=1)
        self.assertEqual(a["decision"],"unknown")
        self.assertEqual(a["unresolved_components"][0]["reason"],"no_backdoor_within_k")
        b=search(6,f,Budget(),k=2)
        self.assertEqual(b["decision"],"sat")
        self.assertEqual(len(b["certified_components"][0]["backdoor"]),2)
        self.assertEqual(b["leaf_count"],4)
        a=search(6,f+[(3,),(-3,)],Budget(),k=2)
        self.assertEqual(a["decision"],"unsat")
        self.assertTrue(a["complete_strong_backdoor_cover"])

    def test_random_soundness(self):
        rng=random.Random(811)
        for _ in range(160):
            n=rng.randrange(8)
            lits=[v for v in range(-n,n+1) if v]
            f=[rng.choices(lits,k=rng.randrange(5)) if lits else []
               for _ in range(rng.randrange(12))]
            a=search(n,f,Budget(),k=2)
            self.assertTrue(verify_certificate(n,f,json.loads(json.dumps(a)),Budget()))
            if a["decision"]!="unknown":
                self.assertEqual(a["decision"]=="sat",brute(n,f,Budget()))

    def test_tampering(self):
        f=family(2)
        a=search(6,f,Budget(),k=1)
        p=a["certified_components"][0]
        for forged in (
                {**a,"decision":"unsat"},
                {**a,"certified_components":[p]},
                {**a,"leaf_count":0},
                {**a,"certified_components":[{**p,"branches":p["branches"][:1]},a["certified_components"][1]]},
                {**a,"certified_components":[{**p,"branches":[p["branches"][0]]*2},a["certified_components"][1]]},
                {**a,"certified_components":[{**p,"sat":False},a["certified_components"][1]]}):
            with self.assertRaises(ValueError):
                verify_certificate(6,f,forged,Budget())
        ob=isolated_obstruction(6,f,Budget())
        with self.assertRaises(ValueError):
            verify_obstruction(6,f,{**ob,"lower_bound":3},Budget())
        with self.assertRaises(ValueError):
            verify_obstruction(6,f+[(3,4)],ob,Budget())

    def test_unknown_and_partition(self):
        f=[(1,2,3),()]
        a=search(3,f,Budget(),k=0)
        self.assertEqual(a["decision"],"unsat")
        self.assertFalse(a["complete_strong_backdoor_cover"])
        self.assertEqual(len(a["unresolved_components"]),1)
        b=search(3,[(1,2,3)],Budget(),k=2,candidate_limit=1)
        self.assertEqual(b["decision"],"unknown")
        self.assertEqual(b["unresolved_components"][0]["reason"],"candidate_limit")
        self.assertEqual(search(0,[],Budget())["decision"],"sat")
        # Reassign two overlapping clauses to separate uncertified groups.
        f=[(1,2,3),(3,4,5)]
        a=search(5,f,Budget(),k=0)
        a["unresolved_components"]=[{"clause_indices":[0]},{"clause_indices":[1]}]
        with self.assertRaises(ValueError):
            verify_certificate(5,f,a,Budget())

    def test_checkpoint_and_governance(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"checkpoint.json"
            r=run(Budget(seconds=20,max_steps=5_000_000),sizes=(1,4),checkpoint_path=p)
            self.assertEqual(r["completion"],"scoped_compositional_research_completed")
            self.assertEqual(len(r["controls"]),4)
            self.assertTrue(all(o["status"]=="unresolved" for o in r["obligations"]))
            self.assertFalse(r["p_equals_np_established"])
            self.assertFalse(r["p_not_equals_np_established"])
            self.assertEqual(json.loads(p.read_text())["universal_obligation"],"unresolved")
            self.assertEqual(run(Budget(max_steps=1),sizes=(1,))["completion"],"resource_exhausted")


if __name__=="__main__":
    unittest.main()
