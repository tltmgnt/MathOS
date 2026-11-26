"""RE-X-022B5: same-tape row certificate; retain all formal P vs NP gates."""
import json
from mathos.research.tga_f038_rex_022b4 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-022B5",
        "scope": "FIXED_TERNARY_RAW_TO_ROW_CERTIFICATE",
        "decision": "PRESERVE_SAME_TAPE_WORKER_HANDOFF_WITNESS_TRANSLATION_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "same_machine_worker_handoff": "TESTED",
            "physical_worker_isolation": "TESTED",
            "raw_to_row_certificate": "TESTED",
            "physical_boolean_witness_translation": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Row-index certificate is the original n-bit Boolean witness",
            "Subcubic restricted-family decision establishes original selector admission",
            "Fixed seven-bag path covers unrestricted SAT",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
