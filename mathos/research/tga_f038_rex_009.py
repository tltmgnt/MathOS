"""RE-X-009: bounded exact structural planning and prepared-worker lifecycle evidence."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph
from mathos.research.tga_f038_rex_008 import report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    notes = {
        "REX-02": "Bounded structural planner uses validated finite domains and scopes; original physical producer open",
        "REX-03": "Exact host subset planning, width admission and stage certificate replay tested; full fixed tape lifecycle and charged producer open",
        "REX-04": "Planner-guided generated message tables support host backtracking of a valid original relational witness; original physical witness assembly open",
        "REX-05": "Three-stage prepared-worker chain tested with host transfers and mixed physical/logical execution; no complete normalized same-machine solver",
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
        "mission": "F038-REX-009",
        "scope": "BOUNDED_EXACT_WIDTH_PLANNING_AND_PREPARED_WORKER_CHAIN",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_WIDTH_PLANNER_PHYSICAL_LIFECYCLE_OPEN",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "Greedy minimum candidate count decides structural admission",
            "No admitted structural order implies unsatisfiability",
            "Exact bounded subset planning implies unrestricted polynomial planning",
            "Host-transferred prepared-worker stages prove fixed physical lifecycle",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
