"""024D5F: machine-checked partial producer macro ceilings, resource gates retained."""
import json
from mathos.research.tga_f038_rex_024d5e import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN" and old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024D5F",
        "scope": "PARTIAL_STATIC_PRODUCER_MACRO_RESOURCE_CERTIFICATE",
        "decision": "PRESERVE_PARTIAL_STATIC_CERTIFICATE_FULL_RESOURCE_PROOF_AND_FINITE_COVERAGE_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "width_three_cubic_bound_ci": "CI_PASSED",
            "width_three_producer_macro_drift_certificate": "TESTED_439429_STATES",
            "width_three_scanner_macro_control_bound": "TESTED_STATIC_31_VISITS",
            "width_three_uniform_explicit_clock_constant": "PARTIALLY_STATIC_CERTIFIED_LAYOUT_AND_OTHER_PHASES_OPEN",
            "width_three_native_m4_replay": "UNCONFIRMED",
            "width_three_cubic_stage_admission": "OPEN_FINITE_COVERAGE",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "A signed displacement certificate conditional on bounded span proves the span bound itself",
            "Static scanner macro counts prove the semantic correspondence of every cut to a distinct input bit",
            "Partial macro certification mechanically proves the complete restricted whole-machine clock bound",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
