"""EFO reasoning integration regression tests."""
import unittest
from mathos.core import MathOS
from mathos.efo import record, register_test, evaluate_test, export_chain, digest

A="2026-11-01T00:00:00Z"
B="2026-11-02T00:00:00Z"
C="2026-11-03T00:00:00Z"
D="2026-11-04T00:00:00Z"
E="2026-11-05T00:00:00Z"

def bundle(value=102):
    obs=record("observation",A,B,"fixture","observed value",{"value":100})
    hyp=record("hypothesis",B,C,"analyst","will exceed 101",{"target":101},(obs.digest,))
    test=register_test(hyp,criterion="value",operator="gt",threshold=101,registered_at=C,horizon_end=D)
    outcome=evaluate_test(test,criterion="value",observed_at=D,recorded_at=E,source_id="fixture",value=value)
    return export_chain((obs,hyp),(test,),(outcome,))

class StubAI:
    def __init__(self):
        self.calls=0
    def solve(self,problem,domain="general"):
        self.calls+=1
        return {"answer":"model response","model":"fixture"}

class IntegrationTests(unittest.TestCase):
    def test_math_verification_is_independent(self):
        system=MathOS(ai_engine=StubAI())
        before=system.solve("2x + 5 = 13",domain="mathematics")
        after=system.solve("2x + 5 = 13",domain="mathematics",evidence_bundle=bundle())
        self.assertEqual(before.verification_status,after.verification_status)
        self.assertEqual(after.empirical_evidence["claim_alignment"],"not_assessed")
        self.assertEqual(after.empirical_evidence["verdict_counts"]["supported"],1)

    def test_ai_remains_unverified(self):
        result=MathOS(ai_engine=StubAI()).solve("Explain gravity",domain="science",evidence_bundle=bundle())
        self.assertEqual(result.verification_status,"unverified")
        self.assertEqual(result.empirical_evidence["source_authenticity"],"not_verified")

    def test_falsified_and_inconclusive(self):
        for value,name in [(99,"falsified"),(None,"inconclusive")]:
            result=MathOS(ai_engine=StubAI()).solve("Explain",domain="general",evidence_bundle=bundle(value))
            self.assertEqual(result.empirical_evidence["verdict_counts"][name],1)
            self.assertEqual(result.verification_status,"unverified")

    def test_invalid_bundle_rejected_before_ai_call(self):
        ai=StubAI()
        data=bundle()
        data["payload"]["records"][0]["claim"]="tampered"
        with self.assertRaises(ValueError):
            MathOS(ai_engine=ai).solve("Explain",domain="general",evidence_bundle=data)
        self.assertEqual(ai.calls,0)
        data["digest"]=digest(data["payload"])
        with self.assertRaises(ValueError):
            MathOS(ai_engine=ai).solve("Explain",domain="general",evidence_bundle=data)
        self.assertEqual(ai.calls,0)

    def test_default_compatibility(self):
        result=MathOS(ai_engine=StubAI()).solve("Explain",domain="general")
        self.assertEqual(result.empirical_evidence,{})
        self.assertEqual(result.verification_status,"unverified")

    def test_summary_detached_from_input(self):
        data=bundle()
        result=MathOS(ai_engine=StubAI()).solve("Explain",domain="general",evidence_bundle=data)
        before=result.empirical_evidence["bundle_digest"]
        data["payload"]["records"][0]["claim"]="changed"
        self.assertEqual(result.empirical_evidence["bundle_digest"],before)

if __name__=="__main__":
    unittest.main()
