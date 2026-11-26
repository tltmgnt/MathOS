"""RE-X-022B4: fixed physical raw-to-nested-bag producer; retain open gates."""
import json
from mathos.research.tga_f038_rex_022b3 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-022B4",
        "scope": "FIXED_TERNARY_RAW_TO_NESTED_BAG_PRODUCER",
        "decision": "PRESERVE_PHYSICAL_SERIALIZATION_HANDOFF_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "physical_bag_producer": "TESTED",
            "physical_bag_serialization": "TESTED",
            "physical_mask_restoration": "TESTED",
            "host_extracted_physical_grammar_worker_bridge": "TESTED",
            "same_machine_worker_handoff": "OPEN",
            "physical_boolean_witness_translation": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "BAGS_PREPARED constitutes a SAT witness",
            "Host extraction of physically emitted grammar is same-machine composition",
            "A subcubic producer alone establishes original-selector admission",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
