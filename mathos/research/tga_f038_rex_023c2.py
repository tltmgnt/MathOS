"""REX-023C2: physically emitted general width-two relations; general worker open."""
import json
from mathos.research.tga_f038_rex_023c1 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-023C2",
        "scope": "PHYSICAL_VARIABLE_ARITY_OWNED_FACTOR_RELATIONS",
        "decision": "PRESERVE_GENERAL_PHYSICAL_RELATIONS_WORKER_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "general_factor_forest_native_codec": "CI_PASSED",
            "general_physical_bag_grammar": "TESTED",
            "general_physical_mask_restoration": "TESTED",
            "general_physical_separator_worker": "OPEN",
            "general_physical_width_two_witness": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Emitted local relations are a globally consistent row choice",
            "Variable-arity forest grammar is already supported by REX-020",
            "The physical relation producer is an unrestricted SAT solver",
        ],
    }


if __name__ == '__main__':
    print(json.dumps(report(), indent=2))
