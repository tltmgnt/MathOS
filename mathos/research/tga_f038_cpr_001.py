"""MRA-X-TGA-2.0: CPR-001 editorial evidence gate, not a proof checker."""
import json
from mathos.proof_analysis.gap_analysis import Claim, analyze


def graph():
    g = {}
    for key, label, note in (
        ("CPR-01", "Projection hierarchy and oracle scope", "Exact set identities; review open"),
        ("CPR-02", "Feasible-source multiplicity conditions", "Generalized count and finite tests; review open"),
        ("CPR-03", "Conditioned parity certificate and separation", "Soundness, cycle example and clique obstruction derived; review open"),
        ("CPR-04", "Same-machine physical implementation and normalized integration", "Analytical ledger only; not compiled"),
        ("CPR-05", "Independent mathematical review", "Outstanding"),
        ("CPR-06", "Uniform alternative structural recovery", "Per-edge binary parity sufficiency refuted; distinct recovery required"),
        ("CPR-07", "Exact eventual universal-stage integration", "No integrated description or clock proof"),
    ):
        g[key] = Claim(label, "open", note=note)
    g["restricted_evidence"] = Claim(
        "Restricted conditioned parity evidence readiness", "derived",
        (("CPR-01", "CPR-02", "CPR-03", "CPR-04", "CPR-05"),),
        "Authored evidence dependencies, not mathematical necessities.")
    g["uniform_recovery"] = Claim(
        "Alternative uniform structural recovery evidence readiness", "derived",
        (("restricted_evidence", "CPR-06", "CPR-07"),),
        "An editorial gate only; no claim that the refuted parity implication can be repaired.")
    return g


def report():
    g = graph()
    r = {k: analyze(g, k) for k in ("restricted_evidence", "uniform_recovery")}
    assert all(v["status"] == "BLOCKED" for v in r.values())
    assert r["restricted_evidence"]["minimal_completion_sets"] == [
        ["CPR-01", "CPR-02", "CPR-03", "CPR-04", "CPR-05"]]
    assert r["uniform_recovery"]["minimal_completion_sets"] == [
        ["CPR-01", "CPR-02", "CPR-03", "CPR-04", "CPR-05", "CPR-06", "CPR-07"]]
    return {
        "system": "MRA-X-TGA-2.0",
        "mission": "F038-TGA-CPR-001",
        "scope": "AUTHORED_EVIDENCE_DEPENDENCIES_NOT_PROOF",
        "decision": "PRESERVE_RESTRICTED_PARITY_RETIRE_UNIFORM_REVIEW",
        "PNP_RESOLUTION_STATUS": "OPEN",
        "PROMOTION": "NONE",
        "rejected_claims": {
            "low_structural_order_implies_free_global_projections": "INVALID_COST_INFERENCE",
            "singleton_map_count_always_subtracts_one": "REFUTED_WITHOUT_TARGET_FEASIBILITY",
            "small_feasible_source_set_implies_sparse_binary_parity_envelope": "REFUTED",
            "arbitrary_binary_coloring_repairs_per_edge_parity_obstruction": "REFUTED",
        },
        **r,
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
