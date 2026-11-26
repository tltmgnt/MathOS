"""RE-X-003 status: fixed physical sorted membership, not full factor elimination."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph
from mathos.research.tga_f038_rex_002 import report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    notes = {
        "REX-02": "Fixed two-track and extended tagged block preparation tested; full solver layout open",
        "REX-03": "Prepared sorted variable-length membership and grouped OR physically implemented; sorting, query generation, factor preservation, reordering, full bit routine open",
        "REX-04": "Sparse physical projection tested; actual SAT witness assembly open",
        "REX-05": "Fixed physical descriptors for individual workers tested; no integrated separator descriptor",
    }
    for k, note in notes.items():
        c = g[k]
        g[k] = Claim(c.label, c.state, c.routes, note)
    local = {k: inspect_routes(g, k) for k in old["local_routes"]}
    assert all(v["status"] == "BLOCKED" for v in local.values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    assert local["restricted_evidence"]["minimal_completion_sets"] == [
        ["REX-%02d" % i for i in range(1, 8)]]
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN" and old["PROMOTION"] == "NONE"
    return {
        "system": "MRA-X-TGA-2.0 + RE-X",
        "mission": "F038-REX-003",
        "scope": "PHYSICAL_SORTED_MEMBERSHIP_NOT_INTEGRATED_ELIMINATION",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_SORTED_MEMBERSHIP_INTEGRATION_OPEN",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "Syntactically valid token stream implies sorted keys",
            "Physical membership on prepared sorted records implies physical sorting",
            "Destructive membership output implies retained-factor join integration",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
