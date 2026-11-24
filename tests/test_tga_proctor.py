import copy
import json
from pathlib import Path
import tempfile
import unittest
from mathos.research import tga_agent as agent
from mathos.research import tga_proctor as p

class ProctorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)
            agent.run(agent.Offline(),out,attempts=2,max_calls=8)
            agent.run(agent.Offline(),out,attempts=1,max_calls=4,resume=True)
            cls.state=json.loads((out/"state.json").read_text())
    def test_curriculum(self):
        r=p.curriculum()
        self.assertEqual((r["weeks"],r["modules"],r["tracks"],r["assessment_points"]),(12,6,7,100))
        self.assertFalse(r["completion_awarded"])
    def test_replay(self):
        r=p.audit(self.state)
        self.assertEqual(r["recorded_packets_replayed"],3)
        self.assertEqual(r["reserved_calls"],12)
        self.assertFalse(r["formal_proof_verified"])
        self.assertFalse(r["learner_completion_awarded"])
    def test_mutations(self):
        for change in (
            lambda s:s["source_sha256"].clear(),
            lambda s:s.update(calls_reserved=0),
            lambda s:s["attempts"][0].update(candidate_status="PROOF_CANDIDATE"),
            lambda s:s["attempts"][0]["probe"]["directed_check"].update(executed=True),
            lambda s:s["attempts"][0].update(claim_id="HODGE.primitive"),
            lambda s:s.update(global_promotion="SOLVED"),
        ):
            with self.subTest(change=change):
                s=copy.deepcopy(self.state);change(s)
                with self.assertRaises(ValueError):p.audit(s)
    def test_failed_attempt_is_not_a_grade(self):
        s=copy.deepcopy(self.state)
        s["attempts"][-1]["status"]="FAILED"
        r=p.audit(s)
        self.assertEqual(r["recorded_packets_replayed"],2)
        self.assertFalse(r["learner_completion_awarded"])
