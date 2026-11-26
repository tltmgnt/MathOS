"""RE-X-008: finite relational reference solver and prepared-worker equivalence tests."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph
from mathos.research.tga_f038_rex_007 import report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    notes = {
        "REX-02": "General finite integer-domain reference solver and rank-encoded prepared bags tested; original physical producer open",
        "REX-03": "Reference stage invariant, complete-candidate batching, reordering and multistage composition tested; full fixed tape lifecycle open",
        "REX-04": "Reference and generated prepared-worker local witness provenance agree on designated bags; original physical witness assembly open",
        "REX-05": "Cross-language reference/physical prepared-bag tests passed; no complete normalized same-machine solver",
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
        "mission": "F038-REX-008",
        "scope": "FINITE_RELATIONAL_REFERENCE_AND_PREPARED_WORKER_BRIDGE",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_RELATIONAL_REFERENCE_PHYSICAL_LIFECYCLE_OPEN",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "Universal finite relational correctness implies unrestricted polynomial complexity",
            "Finite prepared-worker agreement proves complete original physical equivalence",
            "Candidate batch cap bounds the outgoing relation cardinality",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
