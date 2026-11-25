import copy
import unittest
from unittest.mock import patch

from mathos.research import tga_all_problems as allp


class AllProblemsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.topo = allp.topology()

    def test_seven_tracks_joint_and_external(self):
        t = self.topo
        self.assertEqual(set(t["registered_tracks"]), set(allp.TRACKS))
        project = t["registered_project_joint"]
        external = t["registered_external_poincare_joint"]
        self.assertEqual(project["status"], "BLOCKED")
        self.assertEqual(external["status"], "BLOCKED")
        self.assertEqual(len(project["minimal_completion_sets"]), 8)
        self.assertTrue(all("POINCARE.reconstruction" in s for s in project["minimal_completion_sets"]))
        self.assertTrue(all("POINCARE.reconstruction" not in s for s in external["minimal_completion_sets"]))
        self.assertEqual(t["joint_factorization"]["project"]["status"], "PASS")
        self.assertEqual(t["joint_factorization"]["external_poincare"]["status"], "PASS")
        self.assertEqual(t["mathematical_certification"], "NOT_CERTIFIED")

    def test_bridges_remain_explicit(self):
        p = self.topo["registered_project_joint"]
        for completion in p["minimal_completion_sets"]:
            self.assertTrue(any(c.startswith("BRIDGE.RH.") for c in completion))
            self.assertTrue(any(c.startswith("BRIDGE.BSD.") for c in completion))
        self.assertFalse(p["level_6_certified"])

    def test_factorization_rejects_tampering(self):
        p = copy.deepcopy(self.topo["registered_project_joint"])
        p["minimal_blocking_sets"] = []
        with self.assertRaises(ValueError):
            allp.check_factorization(p, list(self.topo["registered_tracks"].values()))

    def test_failure_does_not_skip_other_rounds(self):
        with patch.object(allp.round1, "rh", side_effect=ValueError("fixture failure")), \
             patch.object(allp.round2, "rh", return_value={"fixture": 2}), \
             patch.object(allp.round3, "rh", return_value={"fixture": 3}), \
             patch.object(allp.round4, "rh", return_value={"fixture": 4}):
            r = allp.run_track("Riemann")
        self.assertEqual(r["status"], "FAILED")
        self.assertEqual(r["failed_rounds"], ["round1"])
        self.assertEqual(r["controls"]["round3"]["status"], "PASS")
        self.assertEqual(r["controls"]["round4"]["status"], "PASS")
        self.assertFalse(r["new_proof_generated"])


if __name__ == "__main__":
    unittest.main()
