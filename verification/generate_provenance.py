"""Generate provenance for the current MathOS CI run."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "verification" / "registry.json"
OUTPUT = ROOT / "verification" / "provenance.json"


def main():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    commit = os.environ.get("GITHUB_SHA", "unknown")

    records = []

    for claim in registry["claims"]:
        verification = claim["verification"]

        records.append({
            "claim_id": claim["claim_id"],
            "test_file": verification["test_file"],
            "test_class": verification["test_class"],
            "test_method": verification["test_method"],
            "execution_status": "not_individually_attested"
        })

    provenance = {
        "standard": "TOPO-406",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "github_run_id": run_id,
        "github_run_attempt": os.environ.get(
            "GITHUB_RUN_ATTEMPT", "unknown"
        ),
        "github_commit": commit,
        "github_ref": os.environ.get(
            "GITHUB_REF", "unknown"
        ),
        "records": records
    }

    OUTPUT.write_text(
        json.dumps(provenance, indent=2) + "\n",
        encoding="utf-8"
    )

    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
