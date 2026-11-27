"""024D4B: physical original halt-head witness and safe blank refusal."""
import json
from mathos.research.tga_f038_rex_024d4a import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024D4B",
        "scope": "RESTRICTED_RAW_SELECTOR_TO_ORIGINAL_HALT_HEAD_WITNESS",
        "decision": "PRESERVE_PHYSICAL_WITNESS_NATIVE_REPLAY_AND_CUBIC_ADMISSION_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_physical_bridge_ci": "CI_PASSED",
            "width_three_ternary_worker": "COMPOSED_ORIGINAL_HALT_HEAD_TESTED",
            "width_three_physical_witness": "TESTED_DOMAIN_TWO",
            "width_three_blank_refusal_and_unsat": "TESTED",
            "width_three_original_descriptor_stream_js": "TESTED",
            "width_three_native_original_interpreter": "OPEN",
            "width_three_cubic_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Restricted width-three witness construction implies unrestricted SAT in P",
            "Original-format streamed JS codec checks imply native Python interpreter replay",
            "An asymptotic subcubic bound gives an explicit numerical finite-stage admission threshold",
            "Structural refusal establishes UNSAT",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
