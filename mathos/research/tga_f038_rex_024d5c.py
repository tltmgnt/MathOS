"""024D5C: native m3 confirmed; explicit segmented storage and m4 phase evidence."""
import json
from mathos.research.tga_f038_rex_024d5b import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN" and old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024D5C",
        "scope": "NATIVE_DOMAIN_THREE_AND_EXPLICIT_WORKER_SPACE",
        "decision": "PRESERVE_NATIVE_M3_M4_PHASE_EVIDENCE_UNIFORM_TIME_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_clock_audit_ci": "CI_PASSED",
            "width_three_native_compatible_interpreter": "NATIVE_M2_M3_PASSED",
            "width_three_native_m3_corrected_replay": "CI_PASSED",
            "width_three_worker_exact_clock_model": "TESTED_M2_M3_NATIVE",
            "width_three_fast_clock_model": "TESTED_DIFFERENTIAL",
            "width_three_worker_space_envelope": "DERIVED_TESTED_M2_M3_M4",
            "width_three_domain_four_worker": "PHASE_ACCOUNTED_HOST_FORMATTED_C1",
            "width_three_native_m4_replay": "OPEN",
            "width_three_uniform_explicit_clock_constant": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "An observed domain-four checkpoint and isolated output prove a complete original native run",
            "A faster observation algorithm accelerates the physical machine",
            "An explicit worker storage envelope establishes uniform numerical cubic-stage coverage",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
