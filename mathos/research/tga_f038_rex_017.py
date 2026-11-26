"""RE-X-017: fixed Boolean changing-overlap nested bags."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph
from mathos.research.tga_f038_rex_016 import report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    notes = {
        "REX-02": "Nested Boolean triple grammar physically parsed; intrinsic overlap codes guarantee running intersection; original raw producer open",
        "REX-03": "Fixed nested triple worker aligns all three ordered parent-pair choices and conjoins complete tuple messages; variable-domain changing overlaps open",
        "REX-04": "Persistent Boolean bag feasibility and preorder new-variable witness recovery tested; original witness assembly open",
        "REX-05": "Fixed descriptor executes arbitrary finite ordered Boolean introduction trees with two-coordinate changing overlap; complete normalized F038 solver absent",
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
        "mission": "F038-REX-017",
        "scope": "FIXED_PHYSICAL_BOOLEAN_CHANGING_OVERLAP",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_BOOLEAN_CHANGING_OVERLAP_VARIABLE_DOMAIN_OPEN",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "Separate unary marginals preserve a two-coordinate separator",
            "Boolean introduction-tree execution implies variable-domain changing-overlap execution",
            "Quadratic explicit Boolean triple input runtime implies unrestricted polynomial SAT",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
