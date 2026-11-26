"""FAR-001 evidence gate, separate from the global P vs NP graph."""
import json
from mathos.proof_analysis.gap_analysis import Claim, analyze

NOTES = {
    "FAR-01": ("Sound compatibility filtering", "Restricted derivation and finite checks; review open"),
    "FAR-02": ("Specific obstruction bypass, including multiple feasible sources", "Derived on designated field family; review open"),
    "FAR-03": ("Noncircular safe predicate discovery", "Bounded joint construction; physical implementation open"),
    "FAR-04": ("Surviving exception resource bound", "Conditional score/volume derivation; review open"),
    "FAR-05": ("Physical transition implementation and cost", "Analytic ledger only; not compiled"),
    "FAR-06": ("Uniform recovery without extra structural promise", "No proof of uniform filtered overflow tightness or alternative recovery"),
    "FAR-07": ("Exact eventual universal-stage integration", "Requires the same implemented program and actual clock proof"),
    "FAR-08": ("Independent mathematical review", "Not executed"),
}

def graph():
    g = {k: Claim(label, "open", note=note) for k, (label, note) in NOTES.items()}
    g["restricted_evidence"] = Claim(
        "Restricted FAR theorem evidence readiness", "derived",
        (("FAR-01", "FAR-02", "FAR-03", "FAR-04", "FAR-05", "FAR-08"),),
        "Editorial gate, not a mathematical premise for a restricted lemma.")
    g["uniform_recovery"] = Claim(
        "Uniform low-loss eventual exact-stage FAR route evidence readiness", "derived",
        (("FAR-01", "FAR-03", "FAR-04", "FAR-05", "FAR-06", "FAR-07", "FAR-08"),),
        "All obligations must refer to the same uniform machine. Not a P vs NP resolution route by itself.")
    return g

def report():
    g = graph()
    return {
        "mission": "F038-FAR-001",
        "scope": "AUTHORED_EVIDENCE_DEPENDENCIES_NOT_PROOF",
        "PNP_RESOLUTION_STATUS": "OPEN",
        "PROMOTION": "NONE",
        "decision": "CONTINUE_CONSTRAINED_AUDIT_OR_REDIRECT",
        "rejected_claims": {
            "low_loss_implies_unfiltered_certificate_tightness": "REFUTED_ON_DESIGNATED_MAPS",
            "bounded_joint_filter_is_complete_for_all_rectangles": "REFUTED",
        },
        "restricted_evidence": analyze(g, "restricted_evidence"),
        "uniform_recovery": analyze(g, "uniform_recovery"),
    }

if __name__ == "__main__":
    r = report()
    assert r["restricted_evidence"]["status"] == "BLOCKED"
    assert r["restricted_evidence"]["minimal_completion_sets"] == [
        ["FAR-01", "FAR-02", "FAR-03", "FAR-04", "FAR-05", "FAR-08"]]
    assert r["uniform_recovery"]["status"] == "BLOCKED"
    assert r["uniform_recovery"]["minimal_completion_sets"] == [
        ["FAR-01", "FAR-03", "FAR-04", "FAR-05", "FAR-06", "FAR-07", "FAR-08"]]
    print(json.dumps(r, indent=2))
