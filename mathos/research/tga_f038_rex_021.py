"""RE-X-021: normalized width-two host producer and physical worker bridge."""
import json
from mathos.proof_analysis.rex import inspect_routes, authorize_one
from mathos.proof_analysis.gap_analysis import Claim
from mathos.research.tga_f038_rex_001 import graph as previous_graph
from mathos.research.tga_f038_rex_020 import report as previous_report


def report():
    old = previous_report()
    g = previous_graph()
    notes = {
        "REX-02": "Original normalized raw recognizer and exact width-two host table producer bridged; fixed physical producer and its resource ledger open",
        "REX-03": "Width-two structural coverage derived and host-produced bags physically tested; wider plans and end-to-end physical cost open",
        "REX-04": "Original n-bit witness reconstructed and validated by host from physical row certificate; same-machine translation open",
        "REX-05": "Host raw producer and physical nested worker bridged; no fixed original-input descriptor or original selector admission yet",
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
        "mission": "F038-REX-021",
        "scope": "NORMALIZED_WIDTH_TWO_HOST_PRODUCER_PHYSICAL_WORKER",
        "PNP_RESOLUTION_STATUS": "OPEN", "PROMOTION": "NONE",
        "decision": "PRESERVE_WIDTH_TWO_HOST_BRIDGE_PHYSICAL_PRODUCER_OPEN",
        "local_routes": local, "global_routes": old["global_routes"],
        "inherited_local_routes": old["inherited_local_routes"],
        "governance": authorize_one(local["restricted_evidence"], {}, 0),
        "rejected_inferences": old["rejected_inferences"] + [
            "Separate unary marginals preserve a two-coordinate separator",
            "Width-two primal-graph recognition covers all normalized instances or all previously admitted plans",
            "Host producer plus prepared-input descriptor constitutes an original-input fixed machine",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
