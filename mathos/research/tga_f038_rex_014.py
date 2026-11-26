"""RE-X-014: fixed Boolean sliding triple bags with exact pair separators."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph
from mathos.research.tga_f038_rex_013 import report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    notes = {
        "REX-02": "Compact sliding triple mask grammar parsed physically; original normalized raw producer open",
        "REX-03": "Two-coordinate separator preservation and two-factor shared-candidate conjunction tested in fixed Boolean sliding bags; general bounded-width lifecycle open",
        "REX-04": "Persistent pair-key predecessor history and contiguous Boolean witness tested; original normalized witness assembly open",
        "REX-05": "Fixed descriptor executes arbitrary finite Boolean sliding triple chain; variable-domain pair separators and complete normalized solver absent",
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
        "mission": "F038-REX-014",
        "scope": "FIXED_PHYSICAL_BOOLEAN_PAIR_SEPARATOR_LIFECYCLE",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_BOOLEAN_PAIR_SEPARATOR_VARIABLE_DOMAIN_OPEN",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "Separate unary marginals preserve a two-coordinate separator",
            "Fixed Boolean sliding bags cover arbitrary bounded-width CSP",
            "Quadratic Boolean sliding-bag runtime implies unrestricted polynomial SAT",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
