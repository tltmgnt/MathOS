"""024D5D: direct domain-four preparation confirmed, explicit virtual worker budget."""
import json
from mathos.research.tga_f038_rex_024d5c import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN" and old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024D5D",
        "scope": "EXPLICIT_WORKER_TIME_ENVELOPE_AND_DOMAIN_FOUR_NATIVE_FIXTURE",
        "decision": "PRESERVE_RESTRICTED_WORKER_BOUNDS_NATIVE_M4_AND_PRODUCER_CONSTANTS_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_resource_audit_ci": "CI_PASSED",
            "width_three_domain_four_direct_loader": "CI_PASSED",
            "width_three_domain_four_worker": "CI_PHASE_ACCOUNTED_DIRECT_PREPARATION",
            "width_three_worker_uniform_virtual_time": "DERIVED_SOURCE_LEVEL_TESTED_FIXTURES",
            "width_three_worker_uniform_physical_time": "DERIVED_SOURCE_LEVEL",
            "width_three_native_m4_replay": "UNCONFIRMED",
            "width_three_uniform_explicit_clock_constant": "OPEN_PRODUCER_BRIDGE_OUTPUT",
            "width_three_cubic_stage_admission": "OPEN_FINITE_COVERAGE",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Phase-accounted domain-four clock establishes a full native replay",
            "A conservative source-level worker bound is a mechanically certified entire-machine bound",
            "A uniform worker coefficient alone establishes explicit whole-machine cubic admission",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
