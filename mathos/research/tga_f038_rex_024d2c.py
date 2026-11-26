"""024D2C: direct raw-selector physical mask stream, not a wider witness."""
import json
from mathos.research.tga_f038_rex_024d2b import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024D2C",
        "scope": "DIRECT_RAW_SELECTOR_TERNARY_MASK_STREAM",
        "decision": "PRESERVE_DIRECT_LOADER_FULL_WORKER_AND_TRANSFER_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_compact_compiler_ci": "CI_PASSED",
            "width_three_direct_mask_loader": "TESTED",
            "width_three_direct_mask_loader_original_codec_js": "TESTED",
            "width_three_direct_mask_loader_checkpoint_preservation": "TESTED",
            "width_three_generic_mask_loader_ternary_completion": "OPEN",
            "width_three_direct_mask_stream_to_worker": "OPEN",
            "width_three_ternary_worker": "OPEN",
            "width_three_physical_witness": "OPEN",
            "width_three_cubic_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Direct physical mask serialization establishes a complete compiled forest controller",
            "A mask stream is an original Boolean satisfying assignment",
            "A different direct loader proves a numerical speedup against an unmeasured generic loader",
        ],
    }


if __name__ == '__main__':
    print(json.dumps(report(), indent=2))
