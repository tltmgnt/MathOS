"""FAR-003 authored evidence topology; not mathematical certification."""
import json
from mathos.research.tga_f038_far_001 import graph as far_graph
from mathos.proof_analysis.gap_analysis import Claim, analyze


def graph():
    g = far_graph()
    for key, label, note in (
        ("PHYS-01", "Fixed-alphabet compiler and mobile mask review", "FAR-002 primitive executed; review outstanding"),
        ("PHYS-02A", "Prepared nested equality semijoin review", "Fixed table, exact clock and exhaustive finite executions; review outstanding"),
        ("PHYS-02B", "Support-aware local mask and pair-union composition", "Exact projected union algorithm and conditional ledger; not compiled"),
        ("PHYS-03", "Raw normalized-input preparation and output reconstruction", "Not implemented for integrated solver"),
        ("PHYS-04", "Complete root/descendant physical cost on the same machine", "Not implemented"),
        ("FAR-03", "Noncircular safe predicate discovery", "Exact pair-major projected feasibility derived; physical composition open"),
        ("FAR-06", "Uniform recovery without extra promise", "Key-deletion sufficiency refuted on designated distributed-escape maps; alternative route open"),
    ):
        g[key] = Claim(label, "open", note=note)
    g["PHYS-02"] = Claim("Nested physical composition", "derived",
                         (("PHYS-02A", "PHYS-02B"),),
                         "Prepared equality is not the complete support-aware filter.")
    g["FAR-05"] = Claim("Integrated physical implementation and cost", "derived",
                        (("PHYS-01", "PHYS-02", "PHYS-03", "PHYS-04"),))
    return g


def report():
    g = graph()
    result = {key: analyze(g, key) for key in
              ("PHYS-02", "FAR-05", "restricted_evidence", "uniform_recovery")}
    assert all(r["status"] == "BLOCKED" for r in result.values())
    assert result["PHYS-02"]["minimal_completion_sets"] == [["PHYS-02A", "PHYS-02B"]]
    assert result["FAR-05"]["minimal_completion_sets"] == [
        ["PHYS-01", "PHYS-02A", "PHYS-02B", "PHYS-03", "PHYS-04"]]
    assert len(result["restricted_evidence"]["minimal_completion_sets"][0]) == 10
    assert len(result["uniform_recovery"]["minimal_completion_sets"][0]) == 11
    return {
        "mission": "F038-FAR-003",
        "scope": "AUTHORED_EVIDENCE_DEPENDENCIES_NOT_PROOF",
        "bounded_cycles_completed": 3,
        "decision": "COMPLETE_BOUNDED_MISSION_REVIEW_OR_REDIRECT",
        "PNP_RESOLUTION_STATUS": "OPEN",
        "PROMOTION": "NONE",
        "rejected_claims": {
            "low_loss_implies_unfiltered_certificate_tightness": "REFUTED_ON_DESIGNATED_MAPS",
            "bounded_joint_filter_complete_for_all_rectangles": "REFUTED",
            "exact_key_feasibility_implies_tight_key_filtered_certificates": "REFUTED_ON_DESIGNATED_MAPS",
            "prepared_equality_machine_is_integrated_FAR_worker": "INVALID_SCOPE_INFERENCE",
        },
        **result,
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
