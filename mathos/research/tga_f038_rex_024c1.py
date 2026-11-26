"""REX-024C1: physical width-three headers and factors, not a wider solver."""
import json
from mathos.research.tga_f038_rex_024b import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024C1",
        "scope": "PHYSICAL_WIDTH_THREE_ALL_SCOPE_MASKS_AND_BAG_HEADERS",
        "decision": "PRESERVE_PHYSICAL_HEADERS_WIDER_SERIALIZER_AND_WORKER_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_plan_native_codec": "CI_PASSED",
            "width_three_physical_factor_masks": "TESTED",
            "width_three_physical_bag_headers": "TESTED",
            "width_three_physical_ownership_slots": "TESTED",
            "width_three_owned_relation_host_oracle": "TESTED",
            "width_three_physical_bag_relations": "OPEN",
            "width_three_multitape_merge_blueprint": "DESIGN_ONLY",
            "width_three_physical_witness": "OPEN",
            "width_three_cubic_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Physical scope slots constitute physically serialized bag tuples",
            "A multitape merge blueprint establishes a completed ternary machine",
        ],
    }


if __name__ == '__main__':
    print(json.dumps(report(), indent=2))
