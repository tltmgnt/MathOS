"""RE-X-019: quadratic pivot-synchronous variable-label edge alignment."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph
from mathos.research.tga_f038_rex_018 import report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    notes = {
        "REX-02": "Same explicit sparse triple row grammar, field selection tags generated physically; original normalized input producer open",
        "REX-03": "One-edge pivot-synchronous joint alignment has quadratic explicit-input bound and tested flags; nested lifecycle and global cost remain open",
        "REX-04": "First supported parent and child recovered on same tape; all-parent provenance and original witness assembly open",
        "REX-05": "Fixed quadratic variable-label edge descriptor tested; full nested machine and normalized F038 integration absent",
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
        "mission": "F038-REX-019",
        "scope": "FIXED_PHYSICAL_QUADRATIC_EDGE_ALIGNMENT",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_QUADRATIC_EDGE_NESTED_LIFECYCLE_OPEN",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "Separate unary marginals preserve a two-coordinate separator",
            "Quadratic single-edge worker implies full nested variable-domain physical lifecycle",
            "Quadratic explicit-row kernel alone establishes original selector-stage admission",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
