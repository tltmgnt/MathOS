"""024D5B: native m2 confirmation, exact worker clock audit, corrected m3 budget."""
import json
from mathos.research.tga_f038_rex_024d5a import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN" and old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024D5B",
        "scope": "NATIVE_DOMAIN_TWO_AND_EXACT_SEGMENTED_CLOCK_AUDIT",
        "decision": "PRESERVE_NATIVE_M2_CORRECT_M3_BUDGET_FULL_UNIFORM_CONSTANT_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_native_compatible_interpreter": "NATIVE_M2_PASSED",
            "width_three_native_original_interpreter": "SMALL_CONTROL_ONLY",
            "width_three_native_quotient_descriptor": "TESTED",
            "width_three_worker_exact_clock_model": "TESTED_M2_DERIVED_M3",
            "width_three_native_m3_prior_budget": "FAILED_INSUFFICIENT_BUDGET",
            "width_three_native_m3_corrected_replay": "UNCONFIRMED",
            "width_three_uniform_explicit_clock_constant": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "An insufficient native replay budget refutes the restricted algorithm",
            "Exact phase-accounted clock is a completed full physical replay",
            "A simulator coefficient in terms of virtual steps and cells gives the entire uniform resource constant",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
