"""SEP-001 evidence dependency gate; not a mathematical proof checker."""
import json
from mathos.proof_analysis.gap_analysis import Claim, analyze


def report():
    g = {}
    for key, label, note in (
        ("SEP-01", "Exact component factorization and admission theorem", "Derived and finite semantic tests; review open"),
        ("SEP-02", "Streamed bit implementation and resource bound", "Analytical batch ledger; not implemented"),
        ("SEP-03", "Normalized physical input/output integration", "Not compiled"),
        ("SEP-04", "Independent mathematical review", "Outstanding"),
        ("SEP-05", "Wider structural admission or distinct recovery", "Four-key arity obstruction; uniform route open"),
        ("SEP-06", "Same-machine exact eventual universal-stage proof", "No integrated description or clock proof"),
    ):
        g[key] = Claim(label, "open", note=note)
    g["restricted_evidence"] = Claim(
        "Restricted exact separator evidence readiness", "derived",
        (("SEP-01", "SEP-02", "SEP-03", "SEP-04"),))
    g["uniform_recovery"] = Claim(
        "Uniform alternative recovery evidence readiness", "derived",
        (("restricted_evidence", "SEP-05", "SEP-06"),))
    r = {key: analyze(g, key) for key in ("restricted_evidence", "uniform_recovery")}
    assert all(v["status"] == "BLOCKED" for v in r.values())
    assert r["restricted_evidence"]["minimal_completion_sets"] == [
        ["SEP-01", "SEP-02", "SEP-03", "SEP-04"]]
    assert r["uniform_recovery"]["minimal_completion_sets"] == [
        ["SEP-01", "SEP-02", "SEP-03", "SEP-04", "SEP-05", "SEP-06"]]
    return {
        "system": "MRA-X-TGA-2.0",
        "mission": "F038-TGA-SEP-001",
        "scope": "AUTHORED_EVIDENCE_DEPENDENCIES_NOT_PROOF",
        "decision": "PRESERVE_EXACT_SEPARATOR_ROUTE_REVIEW_BEFORE_EXTENSION",
        "PNP_RESOLUTION_STATUS": "OPEN",
        "PROMOTION": "NONE",
        "rejected_claims": {
            "tractable_private_component_implies_width_three_exact_key_messages": "REFUTED",
            "ineligible_scope_plan_implies_unsatisfiable_or_hard": "INVALID_INFERENCE",
            "host_elimination_regression_is_compiled_physical_solver": "INVALID_SCOPE_INFERENCE",
        },
        **r,
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
