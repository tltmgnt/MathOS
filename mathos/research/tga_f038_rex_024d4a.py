"""024D4A: physically composed raw-selector-to-encoded witness; halt interface open."""
import json
from mathos.research.tga_f038_rex_024d3b2 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024D4A",
        "scope": "COMPOSED_RAW_SELECTOR_TO_ENCODED_WIDTH_THREE_WITNESS",
        "decision": "PRESERVE_PHYSICAL_BRIDGE_ORIGINAL_HALT_INTERFACE_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_constructive_worker_ci": "CI_PASSED",
            "width_three_direct_mask_stream_to_worker": "TESTED_PHYSICAL",
            "width_three_raw_selector_encoded_witness": "TESTED",
            "width_three_ternary_worker": "COMPOSED_ENCODED_WITNESS_TESTED",
            "width_three_physical_witness": "OPEN_ORIGINAL_HALT_INTERFACE",
            "width_three_cubic_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "A physical raw-selector to encoded witness computation implies original halt-head admission",
            "An empty virtual witness implies a blank physical halt head",
            "A calculated original descriptor length proves serialized native codec verification",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
