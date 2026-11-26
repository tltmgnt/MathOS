"""RE-X-006: prepared multifactor elimination in one fixed physical machine."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph
from mathos.research.tga_f038_rex_005 import report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    notes = {
        "REX-02": "Shared three-key prepared record layout tested; original normalized physical record producer open",
        "REX-03": "Membership, candidate conjunction and outgoing OR integrated in one physical worker; complete request generation, candidate-complete chunks, cross-chunk merge and message lifecycle open",
        "REX-04": "Retained record output with sparse representative flags tested; actual SAT witness assembly open",
        "REX-05": "Three sorts, join, two rekeys and two reductions on one tape tested; complete normalized separator descriptor absent",
    }
    for k, note in notes.items():
        c = g[k]
        g[k] = Claim(c.label, c.state, c.routes, note)
    local = {k: inspect_routes(g, k) for k in old["local_routes"]}
    assert all(v["status"] == "BLOCKED" for v in local.values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN" and old["PROMOTION"] == "NONE"
    return {
        "system": "MRA-X-TGA-2.0 + RE-X",
        "mission": "F038-REX-006",
        "scope": "PREPARED_COMPLETE_CANDIDATE_BATCH_ELIMINATION",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_BATCH_ELIMINATION_REQUIRE_CANDIDATE_COMPLETENESS",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "OR of partial candidate conjunctions preserves existential elimination",
            "Prepared request grammar validates complete required-factor coverage",
            "Prepared batch elimination implies normalized SAT discovery",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
