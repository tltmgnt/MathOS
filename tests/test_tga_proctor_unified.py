import copy
import tempfile
import unittest
from pathlib import Path
from mathos.research import tga_agent as a
from mathos.research import tga_proctor_unified as u

class Unified(unittest.TestCase):
    def test_identity(self):
        r=u.analyze_candidate(u.DEMO)
        self.assertTrue(r["equivalent"])
        self.assertEqual(r["assignments_checked"],8)
        self.assertIn("cases v0 <;> cases v1 <;> cases v2 <;> rfl",u.source(u.DEMO))
    def test_counterexample(self):
        c=copy.deepcopy(u.DEMO);c["right"]=False
        r=u.analyze_candidate(c)
        self.assertFalse(r["equivalent"])
        self.assertTrue(r["counterexample"]["left"])
    def test_reject_bad_grammar(self):
        for value in ("arbitrary Lean",["import","Mathlib"],4,["or",0]):
            c=copy.deepcopy(u.DEMO);c["left"]=value
            with self.assertRaises(ValueError):u.source(c)
    def test_checkpoint_integration(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t)
            a.run(a.Offline(),d/"agent",attempts=1,max_calls=4)
            r=u.run(d/"agent/state.json",u.DEMO,d/"proof")
            self.assertEqual(r["status"],"FINITE_CHECK_ONLY")
            self.assertIsNone(r["formal"])
            self.assertEqual(r["proctor_audit"]["recorded_packets_replayed"],1)
            self.assertEqual(r["global_promotion"],"NONE")
            c=copy.deepcopy(u.DEMO);c["attempt_id"]=2
            with self.assertRaises(ValueError):u.run(d/"agent/state.json",c,d/"proof")
