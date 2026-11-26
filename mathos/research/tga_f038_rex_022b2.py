"""RE-X-022B2: exact physical normalized fixed-path recognition, producer still open."""
import json
from mathos.research.tga_f038_rex_022b1 import report as previous_report


def report():
    old = previous_report()
    assert old["PNP_RESOLUTION_STATUS"] == "OPEN"
    assert old["PROMOTION"] == "NONE"
    assert all(v["status"] == "BLOCKED" for v in old["local_routes"].values())
    assert all(v["status"] == "BLOCKED" for v in old["global_routes"].values())
    return {
        **old,
        "mission": "F038-REX-022B2",
        "scope": "TERNARY_NORMALIZED_FIXED_PATH_CLASSIFIER_AND_CHECKPOINT",
        "decision": "PRESERVE_PHYSICAL_NORMALIZATION_MASK_DEPOSITION_OPEN",
        "partial_evidence": {
            **old["partial_evidence"],
            "normalized_clause_validation_descriptor": "TESTED",
            "fixed_path_structural_validation": "TESTED",
            "validated_selector_checkpoint": "TESTED",
            "physical_mask_deposition": "OPEN",
        },
        "rejected_inferences": old["rejected_inferences"] + [
            "Normalized fixed-path acceptance implies SAT",
            "Fixed-path refusal implies UNSAT or treewidth above two",
            "Validated selector checkpoint constitutes emitted local predicate tables",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
