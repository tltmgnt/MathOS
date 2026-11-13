"""Read-only EFO bridge. Valid integrity does not establish answer correctness."""
from mathos.efo import verify_export

def summarize_evidence_bundle(bundle):
    if not verify_export(bundle):
        raise ValueError("Invalid or tampered EFO evidence bundle")
    payload = bundle["payload"]
    counts = {"supported": 0, "falsified": 0, "inconclusive": 0}
    for outcome in payload["outcomes"]:
        counts[outcome["verdict"]] += 1
    return {
        "schema_version": payload["schema_version"],
        "bundle_digest": bundle["digest"],
        "integrity": "internally_consistent",
        "claim_alignment": "not_assessed",
        "source_authenticity": "not_verified",
        "formal_proof": "not_assessed",
        "records": len(payload["records"]),
        "tests": len(payload["tests"]),
        "outcomes": len(payload["outcomes"]),
        "verdict_counts": counts,
        "limitations": [
            "Evidence integrity does not verify the answer.",
            "Source labels and timestamps are not independently authenticated.",
            "Threshold tests do not establish causality or statistical significance."
        ],
    }
