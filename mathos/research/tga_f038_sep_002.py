"""SEP-002 local and global status routes, without theorem promotion."""
import json
from mathos.proof_analysis.gap_analysis import Claim, analyze
from mathos.research.tga_f038_sep_001 import report as sep_report
from mathos.research.tga_pnp_resolution_gap import graph as global_graph


def summary(g, key):
    r = analyze(g, key)
    return {k: r[k] for k in ("status", "minimal_completion_sets",
                              "common_to_all_modeled_routes")}


def report():
    prior = sep_report()["restricted_evidence"]["claims"]
    g = {k: Claim(v["label"], v["state"],
                  tuple(tuple(r) for r in v["routes"]), v["note"])
         for k, v in prior.items()}
    g["SLC-01"] = Claim("Exact sliced separator theorem and reduced planner",
                        "open", note="Derived and semantic checks; review open")
    g["SLC-02"] = Claim("Slice lifecycle, static cache and total physical cost",
                        "open", note="Analytical ledger, host tests; not compiled")
    g["SLC-03"] = Claim("Uniform admission or alternative recovery",
                        "open", note="Complete graph rejects this structural certificate")
    g["sliced_restricted"] = Claim("Sliced restricted route evidence readiness",
        "derived", (("restricted_evidence", "SLC-01", "SLC-02"),))
    g["sliced_uniform"] = Claim("Sliced uniform eventual-stage evidence readiness",
        "derived", (("sliced_restricted", "SLC-03", "SEP-06"),))
    local = {k: summary(g, k) for k in ("restricted_evidence", "uniform_recovery",
                                       "sliced_restricted", "sliced_uniform")}
    glob = global_graph()
    routes = {k: summary(glob, k) for k in (
        "certificate_route", "direct_sat", "selector_route", "negative",
        "mathematical_resolution", "resolution_evidence_gate")}
    assert all(v["status"] == "BLOCKED" for v in (*local.values(), *routes.values()))
    assert local["sliced_restricted"]["minimal_completion_sets"] == [
        ["SEP-01", "SEP-02", "SEP-03", "SEP-04", "SLC-01", "SLC-02"]]
    assert local["sliced_uniform"]["minimal_completion_sets"] == [
        ["SEP-01", "SEP-02", "SEP-03", "SEP-04", "SEP-06",
         "SLC-01", "SLC-02", "SLC-03"]]
    assert routes["mathematical_resolution"]["minimal_completion_sets"] == [
        ["direct_sat"], ["universal_lower_bound"],
        ["selector_algorithm", "selector_bit_cost", "selector_preservation"],
        ["decision_bridge", "discovery", "machine_cost", "ordinary_complete",
         "selected_bounds", "short_proofs", "unbounded_codec"]]
    assert routes["resolution_evidence_gate"]["common_to_all_modeled_routes"] == [
        "independent_review"]
    return {
        "system": "MRA-X-TGA-2.0",
        "mission": "F038-TGA-SEP-002",
        "scope": "AUTHORED_SUFFICIENT_ROUTES_NOT_MATHEMATICAL_PROOF",
        "decision": "PRESERVE_SLICED_ROUTE_REVIEW_BEFORE_EXTENSION",
        "PNP_RESOLUTION_STATUS": "OPEN",
        "PROMOTION": "NONE",
        "local_routes": local,
        "global_routes": routes,
        "rejected_claims": {
            "four_key_message_must_be_materialized": "REFUTED_ON_ADMITTED_CLASS",
            "slicing_admits_every_scope_graph": "REFUTED",
            "restricted_fixed_dimension_coverage_implies_general_SAT": "INVALID_INFERENCE",
        },
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
