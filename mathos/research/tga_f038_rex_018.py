"""RE-X-018: fixed variable-label pair alignment edge kernel."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph
from mathos.research.tga_f038_rex_017 import report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    notes = {
        "REX-02": "Explicit sparse triple row grammar and all three pair codes checked physically; dense tensor producer and original normalized input open",
        "REX-03": "Variable-length joint label equality and per-parent-row semijoin tested on one edge; full nested variable-domain lifecycle and required cost open",
        "REX-04": "First supported parent row and first compatible child row recoverable from output flags; all-parent provenance and original witness assembly open",
        "REX-05": "Fixed edge descriptor complements the Boolean nested worker but does not compose them on one tape; complete normalized F038 solver absent",
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
        "mission": "F038-REX-018",
        "scope": "FIXED_PHYSICAL_VARIABLE_LABEL_EDGE_ALIGNMENT",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_VARIABLE_LABEL_ALIGNMENT_NESTED_COST_OPEN",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "Separate unary marginals preserve a two-coordinate separator",
            "One variable-label edge plus Boolean nested execution implies variable-domain nested execution",
            "Cubic edge-kernel upper bound establishes original cubic selector-stage admission",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
