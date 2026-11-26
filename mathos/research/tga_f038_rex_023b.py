"""REX-023B: structural planner evidence without unrestricted promotion."""
import json
from mathos.research.tga_f038_rex_023a import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-023B",
        "scope": "PHYSICAL_NINE_GROUP_PRIMAL_GRAPH_WIDTH_TWO_PLAN",
        "decision": "PRESERVE_GENERAL_WIDTH_TWO_PLANNER_GENERAL_SOLVER_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "native_large_quotient_replay": "CI_PASSED",
            "general_physical_primal_graph": "TESTED",
            "general_physical_width_two_plan": "TESTED",
            "general_physical_bag_grammar": "OPEN",
            "general_physical_width_two_witness": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Width-two plan is a satisfying assignment",
            "Structural refusal implies unsatisfiability",
            "Arbitrary width-two bags already match the fixed three-field worker grammar",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
