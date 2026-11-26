"""REX-023D1: physical forest decision; original witness and global gates remain open."""
import json
from mathos.research.tga_f038_rex_023c2 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-023D1",
        "scope": "PHYSICAL_GENERAL_WIDTH_TWO_BOTTOM_UP_DECISION",
        "decision": "PRESERVE_PHYSICAL_FOREST_DECISION_WITNESS_RECOVERY_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "general_relations_native_codec": "CI_PASSED",
            "general_physical_separator_worker": "TESTED",
            "general_physical_width_two_decision": "TESTED",
            "general_physical_width_two_witness": "OPEN",
            "general_physical_top_down_row_selection": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Subtree-feasible row flags are a globally selected assignment",
            "A forest decision bit at a separate tape location is an original Boolean witness",
            "A restricted treewidth-two solver decides unrestricted SAT",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
