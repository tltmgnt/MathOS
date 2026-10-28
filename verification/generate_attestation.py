"""Generate TOPO-406 test-result attestations from JUnit XML."""

import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "verification" / "registry.json"
REPORT = ROOT / "verification" / "test-results.xml"
OUTPUT = ROOT / "verification" / "attestation.json"


def read_results(path):
    """Parse actual unittest JUnit XML results."""
    if not path.is_file():
        raise FileNotFoundError(f"Missing test report: {path}")

    tree = ET.parse(path)
    results = {}

    for case in tree.iter("testcase"):
        classname = case.get("classname", "")
        name = case.get("name", "")

        if case.find("failure") is not None:
            status = "failed"
        elif case.find("error") is not None:
            status = "error"
        elif case.find("skipped") is not None:
            status = "skipped"
        else:
            status = "passed"

        key = (classname.split(".")[-1], name)
        results.setdefault(key, []).append(status)

    return results


def main():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    results = read_results(REPORT)

    records = []

    for claim in registry["claims"]:
        verification = claim["verification"]

        key = (
            verification["test_class"],
            verification["test_method"],
        )

        matches = results.get(key, [])

        status = (
            matches[0]
            if len(matches) == 1
            else "not_attested"
        )

        records.append({
            "claim_id": claim["claim_id"],
            "evidence_record": claim["evidence_record"],
            "test_file": verification["test_file"],
            "test_class": key[0],
            "test_method": key[1],
            "execution_status": status,
        })

    attestation = {
        "standard": "TOPO-406",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "github_run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "github_run_attempt": os.getenv(
            "GITHUB_RUN_ATTEMPT", "unknown"
        ),
        "github_commit": os.getenv("GITHUB_SHA", "unknown"),
        "records": records,
    }

    OUTPUT.write_text(
        json.dumps(attestation, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Generated {OUTPUT}")

    if any(
        record["execution_status"] != "passed"
        for record in records
    ):
        print("One or more registered tests were not attested as passed.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
