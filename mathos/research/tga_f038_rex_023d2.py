"""REX-023D2: physical consistent selection and latent rank recovery; original witness open."""
import json
from mathos.research.tga_f038_rex_023d1 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-023D2",
        "scope": "PHYSICAL_GENERAL_WIDTH_TWO_CONSISTENT_ROWS_AND_LATENT_RANKS",
        "decision": "PRESERVE_SELECTED_RANKS_ORIGINAL_BOOLEAN_TRANSLATION_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "general_elimination_native_codec": "CI_PASSED",
            "general_physical_top_down_row_selection": "TESTED",
            "general_physical_original_order_latent_ranks": "TESTED",
            "general_physical_width_two_witness": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Physical latent rank output is the original Boolean witness format",
            "Host verification of translated ranks is physical witness translation",
        ],
    }


if __name__ == '__main__':
    print(json.dumps(report(), indent=2))
