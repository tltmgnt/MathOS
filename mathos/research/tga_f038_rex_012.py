"""RE-X-012: persistent physical Boolean branching-tree lifecycle."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph
from mathos.research.tga_f038_rex_011 import report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    notes = {
        "REX-02": "Nested Boolean ordered-tree grammar parsed physically; original normalized raw producer open",
        "REX-03": "Arbitrary-depth Boolean tree active-ancestor stack and child-message conjunction tested; variable-domain branching and general width open",
        "REX-04": "Same-tape Boolean tree preorder witness recovery tested; original normalized Boolean witness assembly open",
        "REX-05": "Fixed descriptor executes arbitrary finite Boolean ordered rooted tree without host transfers; complete normalized F038 solver absent",
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
        "mission": "F038-REX-012",
        "scope": "FIXED_PHYSICAL_BOOLEAN_TREE_LIFECYCLE",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_BOOLEAN_TREE_VARIABLE_DOMAIN_BRANCHING_OPEN",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "Boolean branching and variable-domain path separately imply variable-domain branching",
            "Tree preorder witness is automatically original selector witness",
            "Quadratic explicit tree mask runtime implies unrestricted polynomial SAT",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
