"""024C3: charged width-three decision worker from a physical checkpoint snapshot."""
import json
from mathos.research.tga_f038_rex_024c2 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024C3",
        "scope": "CHARGED_FIXED_MULTITAPE_WIDTH_THREE_CHECKPOINT_DECISION",
        "decision": "PRESERVE_CHARGED_CONTROLLER_PHYSICAL_BRIDGE_AND_WITNESS_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_merge_ci": "CI_PASSED",
            "width_three_physical_full_tuple_expansion": "TESTED_MULTITAPE",
            "width_three_physical_forest_controller": "TESTED_MULTITAPE",
            "width_three_snapshot_handoff": "TESTED_HOST_OBSERVER",
            "width_three_multitape_decision": "TESTED",
            "width_three_ternary_worker": "OPEN",
            "width_three_physical_witness": "OPEN",
            "width_three_cubic_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "A charged multitape decision worker is a compiled original-format ternary program",
            "An observed checkpoint snapshot is a physical handoff",
            "A root decision bit is an original satisfying assignment",
        ],
    }


if __name__ == '__main__':
    print(json.dumps(report(), indent=2))
