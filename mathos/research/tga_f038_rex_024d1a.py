"""024D1A: standalone ternary keyed merge subkernel, not original width-three witness."""
import json
from mathos.research.tga_f038_rex_024c4 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024D1A",
        "scope": "STANDALONE_TERNARY_KEYED_MERGE_SUBKERNEL",
        "decision": "PRESERVE_COMPILED_SUBKERNEL_FULL_WORKER_AND_BRIDGE_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_multitape_witness_ci": "CI_PASSED",
            "width_three_finite_keyed_merge_ir": "TESTED",
            "width_three_standalone_ternary_keyed_merge": "TESTED",
            "width_three_keyed_merge_original_codec_js": "TESTED",
            "width_three_ternary_worker": "OPEN",
            "width_three_physical_witness": "OPEN",
            "width_three_cubic_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "A compiled keyed semijoin is a compiled full forest controller",
            "A preencoded virtual tape configuration constitutes a physical raw-selector bridge",
            "Original descriptor syntax alone establishes original Boolean witness admission",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
