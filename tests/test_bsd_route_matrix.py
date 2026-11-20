"""Structural audit only: BSD route matrix records no theorem or certification.

This does NOT validate the mathematical completeness of the matrix, prove
any BSD theorem, or establish novelty.
"""
from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "research" / "BSD_ALL_APPROACHES_MATRIX.v1.json"
OPEN = {"BSD.analytic_selmer", "BSD.sha_finiteness", "BSD.leading_term"}
STATES = {
    "KNOWN_SPECIAL_CASE", "ACTIVE_PARTIAL", "EXPLORATORY",
    "INSUFFICIENT_ALONE", "SUPPORTING_TOOL", "LOGICAL_ALTERNATIVE",
    "TARGET_RESTATEMENT",
}


class BSDRouteMatrixAudit(unittest.TestCase):
    def test_taxonomy_is_non_certifying_and_complete_in_declared_fields(self):
        data = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], "1.0.0")
        self.assertEqual(data["certification"], "NOT_CERTIFIED")
        self.assertEqual(data["mathematical_novelty"], "NOT_ESTABLISHED")
        self.assertEqual(data["universal_proof"], "NOT_ESTABLISHED")
        self.assertIs(data["all_approaches_exhaustive"], False)
        self.assertEqual(data["existing_canonical_route"], "BSD.rank_refined")
        self.assertEqual(set(data["registered_claims"]), OPEN)

        routes = data["routes"]
        self.assertEqual(len(routes), 18)
        self.assertEqual(
            {r["id"] for r in routes},
            {"BSD.M%02d" % n for n in range(1, 19)},
        )
        self.assertTrue(all(r["state"] in STATES for r in routes))
        fields = {"id", "name", "state", "scope", "lever", "bridge",
                  "failure", "exper", "targets"}
        for route in routes:
            self.assertEqual(set(route), fields)
            for key in fields - {"targets"}:
                self.assertIsInstance(route[key], str)
                self.assertGreater(len(route[key].strip()), 5)
            self.assertTrue(route["targets"])
            self.assertTrue(set(route["targets"]) <= OPEN)

        # These must remain cautionary labels rather than proof-status promotion.
        self.assertEqual(
            next(r for r in routes if r["id"] == "BSD.M14")["state"],
            "INSUFFICIENT_ALONE",
        )
        self.assertEqual(
            next(r for r in routes if r["id"] == "BSD.M17")["state"],
            "TARGET_RESTATEMENT",
        )
        self.assertEqual(
            next(r for r in routes if r["id"] == "BSD.M18")["state"],
            "TARGET_RESTATEMENT",
        )


if __name__ == "__main__":
    unittest.main()
