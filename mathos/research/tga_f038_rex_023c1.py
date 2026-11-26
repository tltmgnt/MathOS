"""REX-023C1: physical factor-forest checkpoint, general solver remains open."""
import json
from mathos.research.tga_f038_rex_023b import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-023C1",
        "scope": "PHYSICAL_ALL_SCOPE_MASKS_AND_FOREST_PARENTS",
        "decision": "PRESERVE_FACTOR_FOREST_PHYSICAL_RELATION_SERIALIZATION_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "general_planner_native_codec": "CI_PASSED",
            "general_physical_factor_masks": "TESTED",
            "general_physical_forest_parents": "TESTED",
            "general_owned_factor_relation_host_oracle": "TESTED",
            "general_physical_bag_grammar": "OPEN",
            "general_physical_width_two_witness": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Physical masks and forest headers constitute physical bag-row serialization",
            "Host-owned-factor relation enumeration constitutes physical worker execution",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
