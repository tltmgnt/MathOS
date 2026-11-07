"""Standard-library tests for MathOS EFO evidence and falsification."""
import copy
from dataclasses import replace
import unittest

from mathos.efo import (record, register_test, evaluate_test, export_chain,
                        verify_export, verify_chain, digest, FalsificationTest)

T0 = "2026-11-01T00:00:00Z"
T1 = "2026-11-02T00:00:00Z"
T2 = "2026-11-03T00:00:00Z"
T3 = "2026-11-04T00:00:00Z"
T4 = "2026-11-05T00:00:00Z"

def fixture():
    observation = record("observation", T0, T1, "fixture:measurement", "value was 100", {"value": 100})
    fact = record("fact", T1, T1, "analyst", "measured value was 100", {"value": 100}, (observation.digest,))
    hypothesis = record("hypothesis", T1, T2, "analyst", "value will exceed 101", {"threshold": 101}, (fact.digest,))
    test = register_test(hypothesis, criterion="value", operator="gt", threshold=101, registered_at=T2, horizon_end=T3)
    outcome = evaluate_test(test, criterion="value", observed_at=T3, recorded_at=T4, source_id="fixture:outcome", value=102)
    return (observation, fact, hypothesis), (test,), (outcome,)

class EFOTests(unittest.TestCase):
    def test_roundtrip(self):
        items = fixture()
        self.assertTrue(verify_chain(*items))
        self.assertTrue(verify_export(export_chain(*items)))
        self.assertEqual(export_chain(*items), export_chain(*fixture()))

    def test_deep_immutable_snapshot(self):
        values = {"nested": {"items": [1]}}
        obs = record("observation", T0, T1, "fixture", "claim", values)
        before = obs.digest
        values["nested"]["items"].append(2)
        obs.measurements["nested"]["items"].append(3)
        self.assertEqual(obs.measurements, {"nested": {"items": [1]}})
        self.assertEqual(obs.digest, before)

    def test_falsification(self):
        records, tests, _ = fixture()
        outcome = evaluate_test(tests[0], criterion="value", observed_at=T3, recorded_at=T4, source_id="fixture", value=99)
        self.assertEqual(outcome.verdict, "falsified")
        self.assertTrue(verify_chain(records, tests, (outcome,)))

    def test_inconclusive(self):
        records, tests, _ = fixture()
        outcome = evaluate_test(tests[0], criterion="value", observed_at=T3, recorded_at=T4, source_id="fixture", value=None)
        self.assertEqual(outcome.verdict, "inconclusive")
        self.assertTrue(verify_chain(records, tests, (outcome,)))

    def test_wrong_metric_rejected(self):
        _, tests, _ = fixture()
        with self.assertRaises(ValueError):
            evaluate_test(tests[0], criterion="unrelated", observed_at=T3, recorded_at=T4, source_id="fixture", value=102)

    def test_early_outcome_rejected(self):
        _, tests, _ = fixture()
        with self.assertRaises(ValueError):
            evaluate_test(tests[0], criterion="value", observed_at=T2, recorded_at=T4, source_id="fixture", value=102)

    def test_missing_parent(self):
        records, tests, outcomes = fixture()
        self.assertFalse(verify_chain(records[1:], tests, outcomes))

    def test_tampered_verdict(self):
        records, tests, outcomes = fixture()
        self.assertFalse(verify_chain(records, tests, (replace(outcomes[0], verdict="falsified"),)))

    def test_tampered_export(self):
        document = export_chain(*fixture())
        modified = copy.deepcopy(document)
        modified["payload"]["records"][0]["claim"] = "modified"
        self.assertFalse(verify_export(modified))
        modified["digest"] = digest(modified["payload"])
        self.assertFalse(verify_export(modified))

    def test_fact_requires_evidence(self):
        with self.assertRaises(ValueError):
            record("fact", T0, T1, "analyst", "unsupported", {})

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            record("observation", "2026-11-01", T1, "fixture", "claim", {})

    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):
            record("observation", T0, T1, "fixture", "claim", {"value": float("nan")})

    def test_registration_after_horizon(self):
        records, _, _ = fixture()
        with self.assertRaises(ValueError):
            register_test(records[-1], criterion="value", operator="gt", threshold=101, registered_at=T3, horizon_end=T3)

    def test_research_only_enforced(self):
        obs = record("observation", T0, T1, "fixture", "claim", {})
        with self.assertRaises(ValueError):
            replace(obs, research_only=False)

    def test_duplicate_links_rejected(self):
        records, _, _ = fixture()
        with self.assertRaises(ValueError):
            record("hypothesis", T1, T2, "analyst", "claim", {}, (records[0].digest, records[0].digest))

if __name__ == "__main__":
    unittest.main()
