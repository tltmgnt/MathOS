"""Keep the review register synchronized with the authored dependency models."""
import json
from pathlib import Path
import unittest

from mathos.proof_analysis.gap_analysis import models

REGISTER = Path(__file__).resolve().parents[1] / "docs/proof-analysis/OBLIGATIONS.v1.json"


class ProofObligationRegisterTests(unittest.TestCase):
    def test_register_tracks_model_leaves_without_status_promotion(self):
        record = json.loads(REGISTER.read_text(encoding="utf-8"))
        self.assertEqual(record["schema_version"], "1.0.0")
        self.assertEqual(record["certification"], "NOT_CERTIFIED")
        current = models()
        self.assertEqual({x["model_key"] for x in record["tracks"]}, set(current))
        for track in record["tracks"]:
            graph = current[track["model_key"]]
            self.assertEqual(track["target_statement"], graph["target"].label)
            self.assertEqual(track["target_graph_state"], graph["target"].state)
            self.assertEqual(track["modeled_target_status"], "BLOCKED")
            leaves = {key: node for key, node in graph.items() if node.state == "open"}
            supplied = {o["model_node_id"]: o for o in track["work_packages"]}
            self.assertEqual(set(supplied), set(leaves))
            for node_id, claim in supplied.items():
                self.assertEqual(claim["statement"], leaves[node_id].label)
                self.assertEqual(claim["graph_state"], "open")
                self.assertEqual(claim["review_verdict"], "not_reviewed")
                self.assertEqual(claim["formal_check"], "not_performed")

    def test_poincare_external_proof_distinct_from_reconstruction(self):
        record = json.loads(REGISTER.read_text(encoding="utf-8"))
        graph = models()["Poincare"]
        self.assertEqual(record["external_result"]["graph_state"], graph["published"].state)
        self.assertEqual(record["external_result"]["statement"], graph["published"].label)
        self.assertEqual(graph["reconstruction"].state, "open")


if __name__ == "__main__":
    unittest.main()
