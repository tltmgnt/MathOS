"""024C4: charged multitape original-layout witness; original single-tape admission open."""
import json
from mathos.research.tga_f038_rex_024c3 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024C4",
        "scope": "CHARGED_FIXED_MULTITAPE_WIDTH_THREE_ORIGINAL_LAYOUT_WITNESS",
        "decision": "PRESERVE_MULTITAPE_WITNESS_TERNARY_COMPILATION_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_controller_ci": "CI_PASSED",
            "width_three_multitape_top_down_selection": "TESTED",
            "width_three_multitape_original_boolean_layout": "TESTED",
            "width_three_domain_four_snapshot_witness": "TESTED",
            "width_three_ternary_worker": "OPEN",
            "width_three_physical_witness": "OPEN",
            "width_three_cubic_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Original-layout bits on a multitape output imply original single-tape interpreter admission",
            "Separate producer and worker clocks sum to an original single-tape clock",
        ],
    }


if __name__ == '__main__':
    print(json.dumps(report(), indent=2))
