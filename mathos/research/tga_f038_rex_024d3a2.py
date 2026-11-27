"""024D3A2: compiled one-bag canonical mask routing plus local tuple generation."""
import json
from mathos.research.tga_f038_rex_024d3a1 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024D3A2",
        "scope": "COMPILED_LITERAL_CHECKPOINT_ONE_BAG_MASK_ROUTING_AND_CURSOR",
        "decision": "PRESERVE_PHYSICAL_MASK_ROUTER_FOREST_AND_RAW_TRANSFER_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_tuple_cursor_ci": "CI_PASSED",
            "width_three_mask_router_ir": "TESTED",
            "width_three_mask_router_ternary": "TESTED",
            "width_three_mask_router_domain_three": "TESTED",
            "width_three_mask_cursor_initial_routing": "TESTED_COMPILED",
            "width_three_direct_mask_stream_to_worker": "OPEN_LITERAL_TRANSFER_ONLY",
            "width_three_retained_forest_compilation": "OPEN",
            "width_three_ternary_worker": "OPEN",
            "width_three_physical_witness": "OPEN",
            "width_three_cubic_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Literal host tape initialization is a physical raw-selector bridge",
            "A compiled one-bag router and cursor is a complete forest solver",
            "Range-checked packed transitions imply serialized native codec verification",
        ],
    }


if __name__ == '__main__':
    print(json.dumps(report(), indent=2))
