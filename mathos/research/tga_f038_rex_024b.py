"""REX-024B: exact width-three structural planning; wider witness and global gates open."""
import json
from mathos.research.tga_f038_rex_024a import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024B",
        "scope": "EXACT_PHYSICAL_NINE_GROUP_WIDTH_THREE_ELIMINATION_SEARCH",
        "decision": "PRESERVE_WIDTH_TWO_WITNESS_ADVANCE_WIDTH_THREE_STRUCTURAL_PLAN",
        "partial_evidence": {
            **old["partial_evidence"],
            "general_original_native_witness_codec": "CI_PASSED",
            "general_quotient_native_witness_codec": "CI_PASSED",
            "general_physical_width_three_plan": "TESTED",
            "width_three_greedy_counterexample": "TESTED",
            "width_three_physical_bag_relations": "OPEN",
            "width_three_physical_witness": "OPEN",
            "width_three_cubic_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Arbitrary degree-three greedy elimination is complete for width three",
            "Width-three structural eligibility establishes SAT",
            "Width-three structural refusal establishes UNSAT",
            "The width-two physical resource exponent automatically extends to width three",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
