"""RE-X-015: fixed variable-domain sliding triple lifecycle."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph
from mathos.research.tga_f038_rex_014 import report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    notes = {
        "REX-02": "Nested variable-domain pair grids and tensor dimensions physically validated; original normalized raw producer open",
        "REX-03": "Fixed variable-domain sliding triple worker preserves exact pair identity and conjunction on full candidates; general bag lifecycle open",
        "REX-04": "Same-tape variable-domain pair predecessor recovery tested; original normalized Boolean witness assembly open",
        "REX-05": "Fixed descriptor executes variable-domain sliding triple chains; complete normalized F038 solver absent",
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
        "mission": "F038-REX-015",
        "scope": "FIXED_PHYSICAL_VARIABLE_PAIR_SEPARATOR_LIFECYCLE",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_VARIABLE_PAIR_SEPARATOR_GENERAL_BAGS_OPEN",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "Separate unary marginals preserve a two-coordinate separator",
            "Variable-domain sliding bags cover arbitrary bounded-width CSP",
            "Quadratic explicit tensor runtime implies unrestricted polynomial SAT",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
