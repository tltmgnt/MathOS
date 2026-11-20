"""No manuscript should be promoted by an unproved Selmer-infinitude claim."""
import copy
import json
import unittest

from mathos.research.tect_x_submission_gate import (
    DEFAULT_STATUS, REQUIRED, evaluate_status
)


class TestSelmerSubmissionGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.status = json.loads(DEFAULT_STATUS.read_text(encoding="utf-8"))

    def test_live_status_is_blocked_by_unproved_infinite_selmer_theorem(self):
        result = evaluate_status(self.status)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["journal_submission_authorized"])
        self.assertFalse(result["proof_verified_by_software"])
        self.assertTrue(any("theorem is open" in x for x in result["blockers"]))

    def test_open_claim_cannot_be_overridden_with_authorization(self):
        tampered = copy.deepcopy(self.status)
        tampered["publication"]["journal_submission_authorized"] = True
        with self.assertRaisesRegex(ValueError, "contradicts"):
            evaluate_status(tampered)

    def test_submitted_requires_authorization(self):
        tampered = copy.deepcopy(self.status)
        tampered["publication"]["submitted"] = True
        with self.assertRaisesRegex(ValueError, "submitted flag"):
            evaluate_status(tampered)

    def test_boolean_gates_need_evidence(self):
        tampered = copy.deepcopy(self.status)
        tampered["gates"]["main_theorem_proved"] = True
        result = evaluate_status(tampered)
        self.assertTrue(any("lacks evidence" in x for x in result["blockers"]))

    def test_false_gate_values_are_not_truthy_strings(self):
        tampered = copy.deepcopy(self.status)
        tampered["gates"]["independent_specialist_review"] = "yes"
        with self.assertRaisesRegex(ValueError, "exact boolean"):
            evaluate_status(tampered)

    def test_unknown_gate_rejected(self):
        tampered = copy.deepcopy(self.status)
        tampered["gates"]["simulated_pass"] = True
        with self.assertRaisesRegex(ValueError, "required gate"):
            evaluate_status(tampered)

    def test_full_gate_set_is_consistent_with_schema(self):
        self.assertEqual(set(REQUIRED), set(self.status["gates"]))
        self.assertEqual(set(REQUIRED), set(self.status["gate_evidence"]))


if __name__ == "__main__":
    unittest.main()
