"""REX-023A: exact clock-preserving quotient and scheduler audit; no promotion."""
import json
from mathos.research.tga_f038_rex_022b6 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-023A",
        "scope": "FIXED_PATH_CLOCK_PRESERVING_DESCRIPTOR_QUOTIENT_AND_STAGE_LEDGER",
        "decision": "PRESERVE_QUOTIENT_EVENTUAL_RESTRICTED_ADMISSION_FINITE_GLOBAL_GATE_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "exact_reachable_transition_quotient": "TESTED",
            "native_original_small_scheduler_core": "TESTED_SOURCE_COPY",
            "native_large_quotient_replay": "UNCONFIRMED",
            "fixed_path_eventual_cubic_stage_slot": "DERIVED",
            "finite_original_selector_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "A quotient's missing slot implies the universal stage fails",
            "A halt slot with blank output is a witness admission",
            "An abstract transition quotient is minimum among all tape algorithms",
            "Eventual fixed-family cubic admission implies a uniform global cutoff",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
