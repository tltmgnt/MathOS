import json
from pathlib import Path
import tempfile
import unittest
from mathos.research import tga_agent as a

class TestTGAAgent(unittest.TestCase):
    def test_topology_and_rotation(self):
        gap,focus=a.targets()
        self.assertEqual(len(focus),13)
        self.assertEqual(len(gap["completion_sets"]),8)
        hist=[]
        for k in a.PRIORITY:
            self.assertEqual(a.select(hist),k);hist.append({"claim_id":k})
        self.assertEqual(a.select(hist),a.PRIORITY[0])
    def test_checkpoint_and_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            r=a.run(a.Offline(),out,attempts=2,max_calls=8)
            self.assertEqual(r["live_model_calls_this_run"],0)
            self.assertEqual(r["coverage"],2)
            self.assertEqual(len(list(out.glob("*.docx"))),2)
            self.assertFalse(r["mathematical_proof_verified"])
            r=a.run(a.Offline(),out,attempts=1,max_calls=4,resume=True)
            self.assertEqual(r["coverage"],3)
            self.assertEqual(r["total_attempts"],3)
            s=json.loads((out/"state.json").read_text())
            self.assertEqual(s["calls_reserved"],12)
            self.assertTrue(all(x["candidate_status"]=="UNRESOLVED" for x in s["attempts"]))
            s["source_sha256"]={}
            (out/"state.json").write_text(json.dumps(s))
            with self.assertRaises(ValueError):a.run(a.Offline(),out,attempts=1,max_calls=4,resume=True)
    def test_fail_closed(self):
        class Bad(a.Offline):
            def complete(self,role,context):return {"verdict":"PROVED"},{}
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            with self.assertRaises(RuntimeError):a.run(Bad(),out,attempts=1,max_calls=4)
            s=json.loads((out/"state.json").read_text())
            self.assertEqual(s["calls_reserved"],1)
            self.assertEqual(s["attempts"][0]["status"],"FAILED")
            self.assertEqual(s["global_promotion"],"NONE")
            self.assertFalse(list(out.glob("*.docx")))
        with self.assertRaises(ValueError):a.validate("adversary",{
            "verdict":"PROVED","first_gap":"x","counterexample_attempt":"x","next_check":"x"})
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):a.run(a.Offline(),Path(td),attempts=2,max_calls=7)
    def test_interruption_accounting(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"state.json";h=a.snapshot()
            s=a.new_state(a.Offline(),h)
            s["attempts"]=[{"id":1,"claim_id":a.PRIORITY[0],"status":"IN_PROGRESS",
                             "calls_reserved":1,"roles":{}}]
            s["calls_reserved"]=1;a.atomic(path,s)
            r=a.load_state(path,a.Offline(),h,True)
            self.assertEqual(r["attempts"][0]["status"],"INTERRUPTED")
            self.assertEqual(r["calls_reserved"],1)
            self.assertEqual(a.select(r["attempts"]),a.PRIORITY[1])
