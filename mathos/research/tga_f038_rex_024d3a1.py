"""024D3A1: compiled one-bag cursor, with host-mediated initial mask routing."""
import json
from mathos.research.tga_f038_rex_024d2c import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024D3A1",
        "scope": "STANDALONE_TERNARY_ONE_BAG_MASK_CURSOR",
        "decision": "PRESERVE_COMPILED_LOCAL_RELATIONS_PHYSICAL_ROUTING_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_direct_loader_ci": "CI_PASSED",
            "width_three_tuple_cursor_ir": "TESTED",
            "width_three_tuple_cursor_ternary": "TESTED",
            "width_three_tuple_cursor_original_codec_js": "TESTED",
            "width_three_tuple_cursor_domain_three": "TESTED",
            "width_three_mask_cursor_initial_routing": "TESTED_HOST_MEDIATED",
            "width_three_direct_mask_stream_to_worker": "OPEN",
            "width_three_ternary_worker": "OPEN",
            "width_three_physical_witness": "OPEN",
            "width_three_cubic_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "A standalone compiled one-bag relation generator is a composed raw-selector solver",
            "Host routing of mask streams from a physical checkpoint is a physical transfer",
            "Local allowed rows are finalized subtree-feasible rows or original witnesses",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
