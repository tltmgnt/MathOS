"""REX-023D3: restricted-family original Boolean witness; no global promotion."""
import json
from mathos.research.tga_f038_rex_023d2 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-023D3",
        "scope": "GENERAL_NINE_GROUP_NORMALIZED_WIDTH_TWO_PHYSICAL_BOOLEAN_WITNESS",
        "decision": "PRESERVE_RESTRICTED_WITNESS_GLOBAL_ADMISSION_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "general_selection_native_codec": "CI_PASSED",
            "general_physical_width_two_witness": "TESTED",
            "general_original_integer_witness_js_replay": "TESTED",
            "general_original_native_witness_codec": "UNCONFIRMED",
            "general_finite_selector_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "General nine-group width-two witness computation covers unrestricted SAT",
            "A structural refusal is an UNSAT decision",
            "A sufficient individual program slot establishes the earliest universal stage",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
