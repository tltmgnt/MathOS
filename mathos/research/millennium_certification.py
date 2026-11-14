"""CMI-recognized Millennium CERTIFIED use case (external result only).

Mirrors the already-awarded Poincare Millennium Prize as an explicitly
EXTERNAL-recognition-only status. This tool does NOT award a Clay prize,
prove a new theorem, verify Perelman's original proof, or change MathOS's
canonical NOT_CERTIFIED / BLOCKED mathematical research states.

The historical official-source URLs are pinned and reviewed outside CI.
CI rechecks pinning and MathOS status *locally*, NOT CMI live website content.

python -m mathos.research.millennium_certification \
    --output-dir artifacts/millennium-certification
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from mathos.research.clay_alignment import TARGETS_PATH, audit_clay_alignment
from mathos.research.hypothesis_pipeline import HYPOTHESES, OBLIGATIONS, ROOT

EVIDENCE_PATH = ROOT / "docs/research/MILLENNIUM_EXTERNAL_CERTIFIED.v1.json"
OTHER_MODELS = (
    "Birch-Swinnerton-Dyer", "Hodge", "Navier-Stokes",
    "P-versus-NP", "Riemann", "Yang-Mills",
)
CERTIFIED_SCOPE = "EXTERNALLY_RECOGNIZED_MILLENNIUM_RESOLUTION"

EXPECTED_POLICY = {
    "certificate_label": "CERTIFIED",
    "certificate_scope": CERTIFIED_SCOPE,
    "certificate_issuer": "MathOS evidence mirror, NOT the Clay Mathematics Institute",
    "source_of_mathematical_recognition": "Clay Mathematics Institute",
    "basis": "OFFICIAL_SOLVED_LISTING_AND_2010_AWARD_ANNOUNCEMENT",
    "source_verification_mode": "PINNED_OFFICIAL_RECORDS_NOT_LIVE_FETCH",
    "auto_certify_new_solutions": False,
    "auto_certify_mathos_reconstruction": False,
    "enable_automatic_proof_promotion": False,
    "claim_real_time_external_reverification": False,
    "require_human_review_for_new_external_records": True,
    "canonical_mathos_certification": "NOT_CERTIFIED",
    "existing_mathos_tracks": "BLOCKED",
    "external_poincare_result": "established_external",
}
EXPECTED_EXTERNAL_RECORD = {
    "model_key": "Poincare",
    "canonical_claim_id": "POINCARE.published",
    "assertion": (
        "Every closed simply connected three-manifold is homeomorphic "
        "to the three-sphere."
    ),
    "existing_resolution_attribution": "Grigori Perelman",
    "solved_on_official_listing": True,
    "official_listing_url": "https://www.claymath.org/Millennium%20Problems/",
    "official_problem_url": "https://www.claymath.org/millennium/poincare-conjecture/",
    "clay_award_announcement_url": (
        "https://www.claymath.org/wp-content/uploads/2022/06/"
        "Poincare-press-release.pdf"
    ),
    "award_announcement_date": "2010-03-18",
    "award_year": 2010,
    "award_recipient": "Grigori Perelman",
    "formal_mathos_reconstruction_status": "NOT_CERTIFIED",
    "independent_mathos_proof_replayed": False,
    "external_recognition_status": "CERTIFIED",
    "evidence_type": "EXTERNAL_CMI_AWARD_AND_SOLVED_LISTING",
    "evidence_review_note": (
        "CMI officially lists Poincare as solved and announced the Millennium "
        "Prize award to Perelman on March 18, 2010; MathOS only mirrors "
        "these reviewed public records."
    ),
}
EXPECTED_TOP_LEVEL_KEYS = {
    "schema_version", "system", "purpose", "policy",
    "allowed_external_record", "other_models_expected_not_certified",
}


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def verify_external_millennium_case(
    *,
    evidence_path: Path = EVIDENCE_PATH,
    obligations_path: Path = OBLIGATIONS,
    targets_path: Path = TARGETS_PATH,
    hypotheses_path: Path = HYPOTHESES,
) -> dict:
    """Produce a read-only status mirror after verifying all pinned conditions."""
    sources = {
        "cmi_source_manifest": evidence_path.read_bytes(),
        "canonical_obligations": obligations_path.read_bytes(),
        "clay_target_register": targets_path.read_bytes(),
        "hypothesis_register": hypotheses_path.read_bytes(),
        "checker_source": Path(__file__).read_bytes(),
    }
    manifest = json.loads(sources["cmi_source_manifest"])
    canonical = json.loads(sources["canonical_obligations"])
    targets = json.loads(sources["clay_target_register"])
    if not isinstance(manifest, dict) or set(manifest) != EXPECTED_TOP_LEVEL_KEYS:
        raise ValueError("unexpected external certification manifest fields")
    if manifest["schema_version"] != "1.0.0":
        raise ValueError("unrecognized external certification schema")
    if manifest["policy"] != EXPECTED_POLICY:
        raise ValueError("forged external-certification promotion policy")
    if manifest["allowed_external_record"] != EXPECTED_EXTERNAL_RECORD:
        raise ValueError("external recognition must match the pinned CMI historical case")
    if manifest["other_models_expected_not_certified"] != list(OTHER_MODELS):
        raise ValueError("unauthorized external recognition of additional problem")
    if not isinstance(manifest["purpose"], str) or (
        "does not issue a CMI certificate" not in manifest["purpose"]
    ):
        raise ValueError("misleading certification purpose")
    if not isinstance(manifest["system"], str) or (
        manifest["system"] != "MathOS Millennium external-recognition certification mirror"
    ):
        raise ValueError("unexpected certification issuer")

    audit = audit_clay_alignment(
        targets_path=targets_path,
        register_path=obligations_path,
        hypotheses_path=hypotheses_path,
    )
    if (audit["certification"] != "NOT_CERTIFIED"
        or audit["open_work_packages"] != 14):
        raise ValueError("canonical mathematical gate must stay NOT_CERTIFIED")
    external = canonical["external_result"]
    if (external.get("claim_id") != "POINCARE.published"
        or external.get("graph_state") != "established_external"
        or external.get("verification") != "accepted_external_not_replayed"):
        raise ValueError("externally established Poincare not separately recorded")
    if canonical.get("certification") != "NOT_CERTIFIED":
        raise ValueError("MathOS is not independently certified")
    if any(
        t["modeled_target_status"] != "BLOCKED" or any(
            p["graph_state"] != "open"
            or p["formal_check"] != "not_performed"
            or p["review_verdict"] != "not_reviewed"
            for p in t["work_packages"]
        ) for t in canonical["tracks"]
    ):
        raise ValueError("open MathOS proof obligation was promoted")
    clay_statuses = {t["model_key"]: t["clay_status"] for t in targets["targets"]}
    if (len(clay_statuses) != 7
        or clay_statuses.get("Poincare") != "SOLVED_EXTERNALLY"
        or any(clay_statuses.get(key) not in ("UNSOLVED", "ACTIVE")
               for key in OTHER_MODELS)):
        raise ValueError("registered external Clay status disagrees with CMI award")

    # No general-purpose CERTIFIED path: this is a reviewed historical
    # case only. Any new recognized Millennium award requires code review,
    # new official sources and human checking of the updated public record.
    entries = []
    for key in sorted(clay_statuses):
        recognized = key == "Poincare"
        entries.append({
            "model_key": key,
            "status": "CERTIFIED" if recognized else "NOT_CERTIFIED",
            "certification_scope": CERTIFIED_SCOPE if recognized else "NONE",
            "certification_basis": (
                "PINNED_EXTERNAL_CMI_POINCARE_AWARD" if recognized else "NONE"
            ),
            "independently_proved_by_mathos": False,
            "official_source_live_checked_by_this_run": False,
            "mathos_proof_status": "NOT_CERTIFIED",
            "mathos_research_route": "BLOCKED",
        })

    report = {
        "schema_version": "1.0.0",
        "use_case": "MILLENNIUM_EXTERNAL_CERTIFIED_POINCARE",
        "status": "CERTIFIED",
        "status_scope": CERTIFIED_SCOPE,
        "meaning": (
            "MathOS MIRRORS the preexisting CMI-solved/awarded Poincare "
            "result. CERTIFIED is a MathOS evidence classification, NOT "
            "a CMI-issued digital credential or a new mathematical proof."
        ),
        "recognized_by": "Clay Mathematics Institute",
        "reported_by": "MathOS external-recognition mirror",
        "award_recipient": EXPECTED_EXTERNAL_RECORD["award_recipient"],
        "award_announcement_date": EXPECTED_EXTERNAL_RECORD["award_announcement_date"],
        "official_cmi_sources": {
            "solved_listing": EXPECTED_EXTERNAL_RECORD["official_listing_url"],
            "poincare_problem": EXPECTED_EXTERNAL_RECORD["official_problem_url"],
            "award_announcement": EXPECTED_EXTERNAL_RECORD[
                "clay_award_announcement_url"
            ],
        },
        "source_verification_mode": "PINNED_OFFICIAL_RECORDS_NOT_LIVE_FETCH",
        "human_review_needed_for_new_external_awards": True,
        "original_cmi_source_live_checked": False,
        "external_recognized_problems": 1,
        "unrecognized_problems_not_certified": 6,
        "certified_new_mathos_millennium_proofs": 0,
        "mathos_canonical_certification": "NOT_CERTIFIED",
        "mathos_open_work_packages": 14,
        "canonical_proof_promotion": "NONE",
        "external_award_mirror_is_independent_mathos_proof": False,
        "all_tracks": entries,
        "source_sha256": {
            key: _sha256(contents) for key, contents in sources.items()
        },
    }
    for key, path in (
        ("cmi_source_manifest", evidence_path),
        ("canonical_obligations", obligations_path),
        ("clay_target_register", targets_path),
        ("hypothesis_register", hypotheses_path),
        ("checker_source", Path(__file__)),
    ):
        if sources[key] != path.read_bytes():
            raise RuntimeError("read-only certification source changed during run")
    report["report_sha256"] = _sha256(_canonical(report))
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("artifacts/millennium-certification"),
    )
    args = parser.parse_args(argv)
    report = verify_external_millennium_case()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / "millennium_certification.json"
    output.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "external_case": "Poincare",
        "external_case_status": report["status"],
        "external_certification_scope": report["status_scope"],
        "mathos_certification": report["mathos_canonical_certification"],
        "new_mathos_millennium_proofs_certified": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
