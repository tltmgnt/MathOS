"""RE-X-016: fixed variable-domain common-pair branching lifecycle."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph
from mathos.research.tga_f038_rex_015 import report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    notes = {
        "REX-02": "Common-pair root grid, private unary masks and all child tensor dimensions checked physically; original raw producer open",
        "REX-03": "Fixed common-pair star worker conjoins private child messages at identical joint ranks; general changing-overlap bags open",
        "REX-04": "Persistent private predecessor history and joint root plus private one-hot witness recovery tested; original witness assembly open",
        "REX-05": "Fixed descriptor executes common-pair variable-domain branching bags; complete normalized F038 solver absent",
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
        "mission": "F038-REX-016",
        "scope": "FIXED_PHYSICAL_COMMON_PAIR_BRANCHING_LIFECYCLE",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_COMMON_PAIR_BRANCHING_CHANGING_OVERLAP_OPEN",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "Separate unary marginals preserve a two-coordinate separator",
            "Common-pair branching plus sliding chains separately prove arbitrary branching with changing separators",
            "Quadratic explicit common-pair tensor runtime implies unrestricted polynomial SAT",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
