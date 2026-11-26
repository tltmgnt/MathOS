"""RE-X-013: persistent variable-domain ordered-tree lifecycle."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph
from mathos.research.tga_f038_rex_012 import report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    notes = {
        "REX-02": "Nested variable-rank tree masks parsed and rectangle dimensions checked physically; original normalized raw producer open",
        "REX-03": "Fixed variable-rank tree topology stack and aligned child-message conjunction tested; general bounded-width bag lifecycle open",
        "REX-04": "Persistent variable-rank tree predecessor marks and one-hot witness tested; original normalized Boolean witness assembly open",
        "REX-05": "Fixed descriptor executes arbitrary finite rooted ordered tree with positive rank domains; complete normalized F038 solver absent",
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
        "mission": "F038-REX-013",
        "scope": "FIXED_PHYSICAL_VARIABLE_DOMAIN_TREE_LIFECYCLE",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_VARIABLE_DOMAIN_TREE_GENERAL_WIDTH_OPEN",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "Variable-domain tree execution implies arbitrary bounded-width execution",
            "One-hot tree preorder witness is automatically original selector witness",
            "Quadratic explicit tree mask runtime implies unrestricted polynomial SAT",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
