"""Pinned source-chain audit of an external Lean RH claim; NOT theorem verification.

Focus: UpperTheory.FinalTheorems.everyCharacter -> RH. Only a few small
fixed Git blobs are inspected. The enormous transitive theorem proof, the
true mathematical assumptions, and a trusted kernel replay are NOT checked.

Run: python -m mathos.research.rh_external_bridge_audit --fetch-pinned
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

from mathos.research.rh_external_claim_audit import (
    AuditError, MIRROR_COMMIT, ROOT, git_blob_sha1,
)

MANIFEST = ROOT / "docs/research/RH_EXTERNAL_BRIDGE_2026.v1.json"
EXTERNAL_AUDIT = ROOT / "docs/research/RH_EXTERNAL_CLAIM_2026.v1.json"
SCHEMA = "mathos.rh.external_bridge_audit/1"
SOURCE_REPO = "CocoSgt/riemann-hypothesis-lean"
MAX_BYTES = 65_536
# Exact source pins verified against immutable upstream GitHub blobs.
PINS = {
    "src/Development/AutomorphicArithmetic/CharacterBoxes/MainConclusion.lean":
        "ee340012ab19713a8acfecf8adc6a331cbc2f1a4",
    "src/Development/AutomorphicArithmetic/CharacterBoxes/EveryCharacter.lean":
        "6ac769568b67f85f33565ba3e1eef7b91f53c55f",
    "src/Development/AutomorphicArithmetic/CharacterBoxes/RiemannHypothesisOfEveryCharacter.lean":
        "c6dfef5bfa62aa0ef1cd1481833e1cd2475cbbbc",
    "src/Formalism/GammaFactorNonvanishing/CritLine.lean":
        "95fa4da5c50119db164aa93944d106f22fdb576d",
    "src/Formalism/GammaFactorNonvanishing/RhOfRight.lean":
        "3604637147a33e72248faddd775ea750e7846ead",
    "src/Development/AutomorphicArithmetic/Foundations/GaloisRepresentations/IntegralStructures/RowSrc.lean":
        "f769999ac5e49241993e5efbf81e4d2cded18acd",
    "src/Development/AutomorphicArithmetic/Foundations/LocalLanglands/LocalCentralUnits/RecTExists.lean":
        "268786576f96cb5a2cea5fab2da4cf4f291c1116",
    "src/Development/AutomorphicArithmetic/AutomorphicVarieties/ModularityArgument/ThresholdArguments/DenseThresholdCases/VwinOfRow.lean":
        "4cba179acd45ac08d3cad21f51c9b9d62715a9a4",
}
BASE = "src/Development/AutomorphicArithmetic/"
MAIN = BASE + "CharacterBoxes/MainConclusion.lean"
EVERY = BASE + "CharacterBoxes/EveryCharacter.lean"
DIRECT = BASE + "CharacterBoxes/RiemannHypothesisOfEveryCharacter.lean"
CRIT = "src/Formalism/GammaFactorNonvanishing/CritLine.lean"
RIGHT = "src/Formalism/GammaFactorNonvanishing/RhOfRight.lean"
ROW = BASE + "Foundations/GaloisRepresentations/IntegralStructures/RowSrc.lean"
RECT = BASE + "Foundations/LocalLanglands/LocalCentralUnits/RecTExists.lean"
VWIN = BASE + "AutomorphicVarieties/ModularityArgument/ThresholdArguments/DenseThresholdCases/VwinOfRow.lean"

# Inspect declarative source text, not proof soundness. SHA pins make these
# checks about the *specific bytes*, not regexes against arbitrary files.
MARKERS = {
    MAIN: (
        "theorem UpperTheory.FinalTheorems.everyCharacter_of_row",
        "UpperTheory.LiteratureTheorems.every_character_of_literature_of_vWin",
        "UpperTheory.Zero.LLC.recTExists",
        "UpperTheory.One.vwin_of_row h",
        "theorem UpperTheory.FinalTheorems.everyCharacter : UpperTheory.EveryCharacter :=",
        "UpperTheory.FinalTheorems.everyCharacter_of_row UpperTheory.Gal.Int.galoisLocalGlobalStrong_recParameter",
        "theorem UpperTheory.FinalTheorems.riemannHypothesis : RiemannHypothesis :=",
        "UpperTheory.riemannHypothesis_of_everyCharacter UpperTheory.FinalTheorems.everyCharacter",
    ),
    EVERY: (
        "def UpperTheory.EveryCharacter : Prop :=",
        "1 / 2 < s.re",
        "DirichletCharacter.LFunction χ s ≠ 0",
        "theorem UpperTheory.Top.plugAll",
    ),
    DIRECT: (
        "theorem UpperTheory.zeta_ne_zero_of_everyCharacter",
        "DirichletCharacter.LFunction_modOne_eq",
        "theorem UpperTheory.riemannHypothesis_of_everyCharacter (h : UpperTheory.EveryCharacter) : RiemannHypothesis",
        "completedRiemannZeta_one_sub",
    ),
    CRIT: (
        "theorem Formalism.VW.rh_of_every (h : UpperTheory.EveryCharacter) : RiemannHypothesis :=",
        "Formalism.VW.rh_of_right",
        "LFunction_modOne_eq",
    ),
    RIGHT: (
        "theorem Formalism.VW.rh_of_right (hz : ∀ s : ℂ, 1 / 2 < s.re → s ≠ 1 → riemannZeta s ≠ 0) : RiemannHypothesis := by",
        "riemannZeta_one_sub hnat h1",
        "htriv",
    ),
    ROW: (
        "theorem galoisLocalGlobalStrong_recParameter : UpperTheory.GalStar.Row0b recT :=",
        "galoisRepresentations_of_thetaLift UpperTheory.TP.K.tLiftK",
    ),
    RECT: (
        "theorem UpperTheory.Zero.LLC.recTExists :",
        "UpperTheory.Zero.LLC.RecTExists := by",
        "UpperTheory.Zero.LLC.artEx",
        "UpperTheory.Zero.LLC.cuspEx",
    ),
    VWIN: (
        "theorem UpperTheory.One.vwin_of_row",
        "UpperTheory.Top.VWin :=",
        "UpperTheory.One.Join.automorphic_window_of_inputs",
    ),
}
EDGES = [
    ["UpperTheory.FinalTheorems.everyCharacter",
     "UpperTheory.FinalTheorems.everyCharacter_of_row"],
    ["UpperTheory.FinalTheorems.everyCharacter_of_row",
     "UpperTheory.Gal.Int.galoisLocalGlobalStrong_recParameter"],
    ["UpperTheory.Gal.Int.galoisLocalGlobalStrong_recParameter",
     "UpperTheory.TP.K.tLiftK"],
    ["UpperTheory.FinalTheorems.everyCharacter_of_row",
     "UpperTheory.Zero.LLC.recTExists"],
    ["UpperTheory.FinalTheorems.everyCharacter_of_row",
     "UpperTheory.One.vwin_of_row"],
    ["UpperTheory.FinalTheorems.everyCharacter_of_row",
     "UpperTheory.LiteratureTheorems.every_character_of_literature_of_vWin"],
    ["Formalism.VW.rh_of_every",
     "Formalism.VW.rh_of_right"],
    ["UpperTheory.riemannHypothesis_of_everyCharacter",
     "UpperTheory.EveryCharacter"],
]
REVIEW_GAPS = [
    "No independent mathematical review of the deep automorphic and Galois arguments.",
    "No full transitive import/dependency trace or audit of all intermediate definitions.",
    "No replay of the upstream complete Lean kernel proof in this MathOS job.",
    "The literature/automorphic input theorem is referenced, not proved by the audited small files.",
    "External CMI recognition and mathematical community acceptance are separate from this code.",
]
POLICY = {
    "review_level": "SOURCE_LINK_TRACE_ONLY",
    "canonical_rh_status": "OPEN",
    "mathos_certification": "NOT_CERTIFIED",
    "transitive_kernel_replayed_here": False,
    "deep_automorphic_proof_independently_reviewed": False,
    "independent_mathematical_acceptance": False,
    "automatically_update_canonical_register": False,
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AuditError(message)


def validate_manifest(manifest: object) -> None:
    require(type(manifest) is dict and set(manifest) == {
        "schema", "source_repository", "source_commit", "target",
        "pinned_git_blobs", "policy",
    }, "bridge manifest schema mismatch")
    require(
        manifest["schema"] == SCHEMA
        and manifest["source_repository"] == SOURCE_REPO
        and manifest["source_commit"] == MIRROR_COMMIT
        and manifest["target"] == (
            "UpperTheory.FinalTheorems.everyCharacter → "
            "Formalism.VW.rh_of_every → Mathlib RiemannHypothesis"
        ) and manifest["pinned_git_blobs"] == PINS
        and manifest["policy"] == POLICY,
        "bridge manifest source pins or proof-state boundary changed",
    )


def inspect_source_texts(contents: dict[str, str]) -> dict:
    require(type(contents) is dict and set(contents) == set(PINS),
            "expected precisely eight pinned bridge files")
    for path, markers in MARKERS.items():
        source = contents[path]
        require(type(source) is str, "invalid bridge source")
        for marker in markers:
            require(marker in source, f"{path}: missing theorem reference {marker}")
    # Cross-reference the actual direct proof's imports; imports alone
    # are not kernel evidence but guard against disconnected fragments.
    require("import Development.AutomorphicArithmetic.CharacterBoxes.EveryCharacter"
            in contents[DIRECT], "RH implication file missing source definition import")
    require("import Formalism.GammaFactorNonvanishing.RhOfRight"
            in contents[CRIT], "conditional RH bridge not imported")
    require("import Development.AutomorphicArithmetic.CharacterBoxes.RiemannHypothesisOfEveryCharacter"
            in contents[MAIN], "main conclusion does not import direct RH bridge")
    return {
        "files_matched": len(PINS),
        "explicit_source_edges": EDGES,
        "necessary_nonvanishing_statement": (
            "For every Dirichlet character (except the trivial pole case), "
            "L(s, χ) ≠ 0 whenever Re(s) > 1/2"
        ),
        "route_to_RH": (
            "Nonvanishing to the right plus the classical functional "
            "equation excludes nontrivial zeros left of the critical line"
        ),
        "deep_automorphic_input_reviewed": False,
        "transitive_kernel_proof_verified_by_this_audit": False,
        "status": "SOURCE_LINKS_PRESENT_NOT_THEOREM_VERIFIED",
    }


def url_for(path: str) -> str:
    require(path in PINS, "only explicitly pinned bridge files may be fetched")
    return "https://raw.githubusercontent.com/" + SOURCE_REPO + "/" + MIRROR_COMMIT + "/" + path


def fetch_pinned_files(*, opener=None) -> dict[str, str]:
    opener = opener or urlopen
    result = {}
    for path, expected in PINS.items():
        req = Request(url_for(path),
                      headers={"User-Agent": "MathOS-RH-Critical-Bridge-Audit/1"})
        with opener(req, timeout=25) as response:
            data = response.read(MAX_BYTES + 1)
        require(len(data) <= MAX_BYTES, f"{path}: file too large")
        require(git_blob_sha1(data) == expected,
                f"{path}: exact Git blob fingerprint changed")
        result[path] = data.decode("utf-8")
    return result


def make_report(*, manifest_path: Path = MANIFEST,
                fetch_pinned: bool = False, opener=None) -> dict:
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    validate_manifest(manifest)
    parent = json.loads(EXTERNAL_AUDIT.read_text(encoding="utf-8"))
    require(parent["source"]["mirror_commit"] == MIRROR_COMMIT
            and parent["policy"]["mathos_global_claim_status"] == "OPEN"
            and parent["policy"]["full_proof_replayed_by_this_tool"] is False,
            "external-claim parent audit changed")
    source_inspection = None
    if fetch_pinned:
        source_inspection = inspect_source_texts(
            fetch_pinned_files(opener=opener)
        )
    return {
        "schema": SCHEMA,
        "source_commit": MIRROR_COMMIT,
        "source_file_count": len(PINS),
        "source_fetch_performed": fetch_pinned,
        "source_inspection": source_inspection,
        "review_gaps": REVIEW_GAPS,
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "global_rh_status": "OPEN",
        "mathos_certification": "NOT_CERTIFIED",
        "acceptance": "SOURCE_TRACE_ONLY",
        "full_formal_proof_replayed_by_mathos": False,
        "mathematical_truth_established_by_this_audit": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch-pinned", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = make_report(fetch_pinned=args.fetch_pinned)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(1, f"RH CRITICAL BRIDGE AUDIT FAILED: {exc}\n")
    output = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
