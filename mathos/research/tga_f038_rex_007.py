"""RE-X-007: candidate-complete host producer and physical prepared-worker bridge."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph
from mathos.research.tga_f038_rex_006 import report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    notes = {
        "REX-02": "Namespaced complete-request producer integrated with normalized host decoder; fixed physical producer open",
        "REX-03": "Whole-candidate generation, positive message union and witness provenance implemented at host level; physical prepared worker exercised on generated records; fixed tape lifecycle open",
        "REX-04": "Candidate witness extracted from AND representative, not arbitrary OR representative; full original physical witness assembly open",
        "REX-05": "Actual prepared worker receives host-generated factor records; normalized host adapter verified, no complete same-machine solver",
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
        "mission": "F038-REX-007",
        "scope": "HOST_PRODUCER_PHYSICAL_PREPARED_WORKER_BRIDGE",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_CANDIDATE_COMPLETE_BRIDGE_PHYSICAL_LIFECYCLE_OPEN",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "An outgoing OR representative is necessarily a feasible witness",
            "Identical projected tuple digits in different factors share membership",
            "Host generation and separate physical batch calls prove one-tape lifecycle",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
