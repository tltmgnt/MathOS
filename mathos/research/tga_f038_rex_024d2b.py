"""024D2B: exact header quotient and tested mask-loader IR, not full ternary witness."""
import json
from mathos.research.tga_f038_rex_024d2a import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024D2B",
        "scope": "EXACT_HEADER_PHYSICAL_QUOTIENT_AND_MASK_LOADER_IR",
        "decision": "PRESERVE_QUOTIENT_ADVANCE_MASK_LOADING_IR_PHYSICAL_COMPLETION_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_headers_ci": "CI_PASSED",
            "width_three_header_physical_quotient": "TESTED",
            "width_three_header_quotient_smoke": "TESTED",
            "width_three_header_quotient_full_replay": "OPEN",
            "width_three_mask_loader_ir": "TESTED",
            "width_three_mask_loader_ternary_table": "COMPILED",
            "width_three_mask_loader_ternary_completion": "OPEN",
            "width_three_compiled_checkpoint_reader": "OPEN",
            "width_three_ternary_worker": "OPEN",
            "width_three_physical_witness": "OPEN",
            "width_three_cubic_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Exact descriptor quotient reduces physical execution clock",
            "Equal quotient state counts alone prove rooted isomorphism",
            "Compiled mask-loader table plus IR tests establish complete ternary mask loading",
        ],
    }


if __name__ == '__main__':
    print(json.dumps(report(), indent=2))
