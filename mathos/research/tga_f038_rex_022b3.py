"""RE-X-022B3: physical local forbidden masks; retain formal claim gates."""
import json
from mathos.research.tga_f038_rex_022b2 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-022B3",
        "scope": "TERNARY_NORMALIZATION_AND_49_PHYSICAL_FORBIDDEN_MASKS",
        "decision": "PRESERVE_PHYSICAL_MASK_DEPOSITION_SERIALIZATION_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "physical_mask_deposition": "TESTED",
            "physical_pin_deposition": "TESTED",
            "physical_bag_serialization": "OPEN",
            "host_serialized_worker_bridge": "TESTED",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Physical mask checkpoint constitutes a SAT witness",
            "Host serialization plus worker execution constitutes same-machine handoff",
            "Quadratic physical mask deposition alone establishes original-selector admission",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
