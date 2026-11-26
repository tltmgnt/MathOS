"""REX-022B1: physical raw address cursor; retain prior formal claim gates."""
import json
from mathos.research.tga_f038_rex_021 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-022B1",
        "scope": "TERNARY_RAW_POOL_ADDRESS_CURSOR_AND_CHECKPOINT",
        "decision": "PRESERVE_PHYSICAL_ADDRESS_CURSOR_NORMALIZATION_OPEN",
        "partial_evidence": {
            "raw_address_descriptor": "TESTED",
            "selector_checkpoint_descriptor": "TESTED",
            "normalized_clause_validation_descriptor": "OPEN",
            "physical_bag_producer": "OPEN",
            "single_machine_worker_handoff": "OPEN",
            "physical_boolean_witness_translation": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Pool shape implies normalization or satisfiability",
            "A physical selector checkpoint constitutes a completed bag producer",
            "An address-only descriptor gives original-selector stage admission",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
