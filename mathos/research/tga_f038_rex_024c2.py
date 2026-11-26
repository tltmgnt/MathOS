"""024C2: charged multitape separator kernel, not a composed wider witness."""
import json
from mathos.research.tga_f038_rex_024c1 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024C2",
        "scope": "CHARGED_FIXED_MULTITAPE_JOINT_SEPARATOR_MERGE_KERNEL",
        "decision": "PRESERVE_KERNEL_PHYSICAL_COMPOSITION_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_factor_native_codec": "CI_PASSED",
            "width_three_multitape_projection_merge_kernel": "TESTED",
            "width_three_kernel_checkpoint_host_integration": "TESTED",
            "width_three_physical_full_tuple_expansion": "OPEN",
            "width_three_physical_forest_controller": "OPEN",
            "width_three_ternary_worker": "OPEN",
            "width_three_physical_witness": "OPEN",
            "width_three_cubic_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Host-mediated checkpoint integration is a composed physical solver",
            "Multitape microprogram primitive counts are single-tape transition counts",
            "Standalone kernel resource bound establishes full witness resource bound",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
