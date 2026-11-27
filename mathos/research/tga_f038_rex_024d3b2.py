"""024D3B2: standalone compiled constructive witness, physical raw-selector bridge open."""
import json
from mathos.research.tga_f038_rex_024d3b1 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024D3B2",
        "scope": "STANDALONE_COMPILED_RETAINED_FOREST_ORIGINAL_LAYOUT_WITNESS",
        "decision": "PRESERVE_COMPILED_CONSTRUCTIVE_WORKER_PHYSICAL_BRIDGE_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_forest_ci": "CI_PASSED",
            "width_three_compiled_top_down_selection": "TESTED",
            "width_three_compiled_original_layout_witness": "TESTED",
            "width_three_compiled_domain_three_witness_ir": "TESTED",
            "width_three_ternary_worker": "STANDALONE_WITNESS_TESTED",
            "width_three_direct_mask_stream_to_worker": "OPEN_LITERAL_TRANSFER_ONLY",
            "width_three_physical_witness": "OPEN_ORIGINAL_HALT_INTERFACE",
            "width_three_cubic_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "A standalone compiled original-layout witness on a virtual tape establishes raw-selector witness admission",
            "A complete domain-three IR witness establishes a domain-three ternary witness replay",
            "Calculated descriptor size implies serialized native decoder verification",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
