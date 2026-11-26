"""PCF-001 authored evidence gate. No proof certification or promotion."""
import json
from mathos.research.tga_f038_far_003 import graph as far_graph
from mathos.proof_analysis.gap_analysis import Claim, analyze


def graph():
    g = far_graph()
    for key, label, note in (
        ("PCF-01", "Sound pointwise-compatible cylinder recovery", "Restricted containment theorem and semantic model-set checks; review open"),
        ("PCF-02", "Noncircular interval flag construction", "Exact coarse projection with bounded scratch; not compiled"),
        ("PCF-03", "Physical stationary-tree construction and traversal ledger", "Conditional analytical bound; complete physical implementation absent"),
        ("PCF-04", "Uniform tight cylinder score or alternative recovery", "Vanishing loss alone is insufficient on designated private-escape maps"),
        ("PCF-05", "Independent mathematical and complexity review", "Not executed"),
        ("PCF-06", "Inherited actual map and narrow/envelope recovery audit", "Inherited conditional routines; integration and review open"),
    ):
        g[key] = Claim(label, "open", note=note)
    g["pcf_restricted_evidence"] = Claim(
        "Restricted PCF route evidence readiness", "derived",
        (("PCF-01", "PCF-02", "PCF-03", "PCF-05", "PCF-06", "PHYS-03"),),
        "Authored work packages; no claim that every package is mathematically necessary.")
    g["pcf_uniform_recovery"] = Claim(
        "Uniform low-loss eventual exact-stage PCF route evidence readiness", "derived",
        (("pcf_restricted_evidence", "PCF-04", "FAR-07"),),
        "Same integrated machine required; not a general P versus NP resolution route.")
    return g


def report():
    g = graph()
    r = {k: analyze(g, k) for k in (
        "restricted_evidence", "uniform_recovery", "pcf_restricted_evidence",
        "pcf_uniform_recovery")}
    assert all(v["status"] == "BLOCKED" for v in r.values())
    assert r["pcf_restricted_evidence"]["minimal_completion_sets"] == [
        ["PCF-01", "PCF-02", "PCF-03", "PCF-05", "PCF-06", "PHYS-03"]]
    assert r["pcf_uniform_recovery"]["minimal_completion_sets"] == [
        ["FAR-07", "PCF-01", "PCF-02", "PCF-03", "PCF-04", "PCF-05", "PCF-06", "PHYS-03"]]
    return {
        "mission": "F038-PCF-001",
        "scope": "AUTHORED_EVIDENCE_DEPENDENCIES_NOT_PROOF",
        "far_mission": "COMPLETE_BOUNDED_MISSION_REVIEW_OR_REDIRECT",
        "decision": "RETAIN_RESTRICTED_PCF_REVIEW_BEFORE_EXTENSION",
        "PNP_RESOLUTION_STATUS": "OPEN",
        "PROMOTION": "NONE",
        "rejected_claims": {
            "low_loss_implies_unfiltered_certificate_tightness": "REFUTED_ON_DESIGNATED_MAPS",
            "exact_key_feasibility_implies_tight_key_filtered_certificates": "REFUTED_ON_DESIGNATED_MAPS",
            "vanishing_pointwise_projected_density_implies_tight_interval_cylinders": "REFUTED_ON_DESIGNATED_MAPS",
            "host_projection_audit_is_compiled_solver": "INVALID_SCOPE_INFERENCE",
        },
        **r,
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
