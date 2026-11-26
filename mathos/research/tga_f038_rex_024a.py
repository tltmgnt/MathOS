"""REX-024A: exact general witness quotient and restricted-stage admission ledger."""
import json
from mathos.research.tga_f038_rex_023d3 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-024A",
        "scope": "CLOCK_PRESERVING_GENERAL_WIDTH_TWO_WITNESS_QUOTIENT",
        "decision": "PRESERVE_RESTRICTED_QUOTIENT_FINITE_CUBIC_COVERAGE_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "general_exact_transition_quotient": "TESTED",
            "general_parent_packed_table_equality": "TESTED",
            "general_eventual_cubic_stage_admission": "DERIVED_CONDITIONAL_RESOURCE_BOUND",
            "general_original_native_witness_codec": "UNCONFIRMED",
            "general_quotient_native_witness_codec": "UNCONFIRMED",
            "general_finite_selector_stage_admission": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Reduced descriptor length implies fewer physical transitions",
            "A missing individual descriptor slot implies universal stage failure",
            "Eventual restricted cubic admission proves unrestricted SAT admission",
            "A quotient class identifies a unique original program phase",
        ],
    }


if __name__ == '__main__':
    print(json.dumps(report(), indent=2))
