"""RE-X-022B6: original Boolean witness for the fixed normalized path; gates remain open."""
import json
from mathos.research.tga_f038_rex_022b5 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-022B6",
        "scope": "FIXED_TERNARY_RAW_TO_ORIGINAL_BOOLEAN_WITNESS",
        "decision": "PRESERVE_FIXED_PATH_WITNESS_FINITE_STAGE_ADMISSION_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "physical_boolean_witness_translation": "TESTED",
            "raw_to_original_boolean_witness": "TESTED",
            "original_integer_witness_contract_js_replay": "TESTED",
            "native_original_python_codec_gate": "UNCONFIRMED",
            "finite_original_selector_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "A correct fixed-path Boolean witness machine decides unrestricted SAT",
            "An eventual per-description budget proves the prescribed finite stage deadline",
            "A native interpreter regression file constitutes an executed native replay",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
