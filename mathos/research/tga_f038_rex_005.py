"""RE-X-005: same-machine sort and membership attachment, not complete SAT."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph
from mathos.research.tga_f038_rex_004 import report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    notes = {
        "REX-02": "Shared tagged record layout and raw preparation tested; normalized solver layout open",
        "REX-03": "Stable sort and retained-factor membership attached in one physical machine; actual tuple generation, multifactor conjunction, ID reorder and elimination lifecycle open",
        "REX-04": "Contiguous retained-record serialization tested; actual SAT witness assembly open",
        "REX-05": "One fixed descriptor composes stable sort and membership with no reset; full separator descriptor absent",
    }
    for k, note in notes.items():
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
        "mission": "F038-REX-005",
        "scope": "SAME_MACHINE_RETAINED_JOIN_NOT_COMPLETE_ELIMINATION",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_RETAINED_JOIN_ELIMINATION_OPEN",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "Retained one-factor membership implies multifactor conjunction",
            "Stable composite-key order restores original candidate-ID order",
            "Prepared record join implies normalized SAT discovery",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
