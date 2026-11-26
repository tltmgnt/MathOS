"""024D1B: compiled projected semijoin subkernel; full ternary witness remains open."""
import json
from mathos.research.tga_f038_rex_024d1a import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024D1B",
        "scope": "STANDALONE_TERNARY_PROJECTED_SEMIJOIN_AND_RETAINED_TUPLES",
        "decision": "PRESERVE_COMPILED_PROJECTION_HEADER_ROUTING_AND_BRIDGE_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_keyed_merge_ci": "CI_PASSED",
            "width_three_finite_projection_ir": "TESTED",
            "width_three_projection_ir_compaction": "TESTED",
            "width_three_ternary_tuple_projection": "TESTED",
            "width_three_ternary_retained_tuple_output": "TESTED",
            "width_three_projection_original_codec_js": "TESTED",
            "width_three_compiled_checkpoint_reader": "OPEN",
            "width_three_ternary_worker": "OPEN",
            "width_three_physical_witness": "OPEN",
            "width_three_cubic_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "On-tape coordinate masks imply physical derivation from original headers",
            "Retained tuple output is an original Boolean satisfying assignment",
            "Descriptor size comparison between different programs proves clock equivalence",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
