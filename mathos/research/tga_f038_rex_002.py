"""RE-X-002: physical product-track compiler evidence, not integrated SAT."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph, report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    for k, note in {
        "REX-02": "Raw-to-fixed two-track product blocks implemented and tested; full solver-specific layout and review open",
        "REX-03": "Physical grouped OR on prepared membership bits implemented; factor joins, sorting, counters and full fixed sequential solver open",
        "REX-04": "Sparse contiguous witness-track projection tested under explicit output-region contract; actual SAT witness assembly and review open",
        "REX-05": "Generic fixed logical rule compiler with same-tape preparation, computation and projection tested; full integrated separator machine absent",
    }.items():
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
        "mission": "F038-REX-002",
        "scope": "FIXED_TWO_TRACK_COMPILER_AND_PREPARED_EXISTENTIAL_OR",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_PRODUCT_COMPILER_FULL_SOLVER_OPEN",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "Two tracks imply independent multitape head simulation",
            "Prepared membership flags imply physical factor membership discovery",
            "Generic compilation proves an arbitrary worker's output contract",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
