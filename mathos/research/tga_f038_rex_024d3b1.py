"""024D3B1: standalone compiled retained forest decision, no raw-selector witness promotion."""
import json
from mathos.research.tga_f038_rex_024d3a2 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024D3B1",
        "scope": "STANDALONE_COMPILED_RETAINED_FOREST_DECISION",
        "decision": "PRESERVE_COMPILED_FOREST_WITNESS_AND_BRIDGE_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_mask_router_ci": "CI_PASSED",
            "width_three_row_interned_compiler_projection_homomorphism": "TESTED",
            "width_three_retained_forest_compilation": "TESTED",
            "width_three_standalone_ternary_forest_decision": "TESTED",
            "width_three_joint_three_full_forest_ir": "TESTED",
            "width_three_joint_three_full_forest_ternary": "OPEN",
            "width_three_ternary_worker": "DECISION_ONLY_TESTED",
            "width_three_physical_witness": "OPEN",
            "width_three_cubic_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "A standalone compiled forest decision implies raw-selector physical composition",
            "A decision bit at a virtual tape is an original satisfying assignment",
            "A completed IR parity test proves a completed physical parity replay",
        ],
    }


if __name__ == '__main__':
    print(json.dumps(report(), indent=2))
