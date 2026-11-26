"""RE-X-011: variable-domain rectangular path lifecycle evidence."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph
from mathos.research.tga_f038_rex_010 import report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    notes = {
        "REX-02": "Compact variable-domain rectangular path masks parsed and dimension-validated physically; original normalized raw producer open",
        "REX-03": "Fixed variable-domain path message vectors and predecessor edge marks tested; general branching lifecycle open",
        "REX-04": "Same-tape variable-domain path backtracking and contiguous one-hot output tested; original normalized Boolean witness assembly open",
        "REX-05": "Fixed descriptor executes arbitrary finite positive rank-domain path without host transfers; complete normalized F038 solver absent",
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
        "mission": "F038-REX-011",
        "scope": "FIXED_PHYSICAL_VARIABLE_DOMAIN_PATH_LIFECYCLE",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_VARIABLE_DOMAIN_PATH_BRANCHING_OPEN",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "Variable-domain path execution implies branching or arbitrary bounded-width execution",
            "One-hot rank witness is automatically original selector witness",
            "Quadratic explicit path mask runtime implies unrestricted polynomial SAT",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
