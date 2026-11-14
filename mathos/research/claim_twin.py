"""Finite mathematical-claim digital twin with proof-carrying witnesses.

Automatically verifies *bounded* statements with exact arithmetic or a replayed
resolution certificate. It CANNOT certify open Millennium problems. Its seven
certificates are scoped to fixed finite objects; no AI-generated code is run.

python -m mathos.research.claim_twin --output-dir artifacts/claim-twin
python -m mathos.research.claim_twin --input untrusted-candidates.json --track all
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import re
from typing import Any

from mathos.research.clay_alignment import TARGETS_PATH, audit_clay_alignment
from mathos.research.hypothesis_pipeline import (
    HYPOTHESES, OBLIGATIONS, ROOT,
    k4_tseitin_clauses, resolution_certificate_k4, verify_resolution_certificate_k4,
)

MANIFEST = ROOT / "docs/research/CLAIM_TWIN.v1.json"
SCOPE = "FINITE_EXACT_MODEL_ONLY"
STATUS = "CERTIFIED_BOUNDED"
MAX_INPUT_BYTES = 250_000
MAX_STEPS = 1_000

# The exact claim statement, parameterization and evidence meaning are
# duplicated in trusted checker source, not taken solely from a modifiable
# agent-generated manifest. A new statement requires a reviewed code change.
PINNED = {
    "Riemann": (
        "BOUND.RH.H16", "harmonic_fraction",
        "Exact rational evaluation of the finite harmonic sum H_16 = sum(k=1..16, 1/k).",
        {"n": 16},
    ),
    "P-versus-NP": (
        "BOUND.PNP.K4", "k4_resolution",
        "The fixed odd-charge K4 Tseitin 3-CNF has no satisfying Boolean assignment.",
        {"graph": "K4", "odd_vertex": 0},
    ),
    "Navier-Stokes": (
        "BOUND.NS.EXPONENT", "abc_exponent_samples",
        "For nu=1, K=3 and q in {1,1/2,1/4,1/8}, the finite rational values 2K(1-q)/nu equal the supplied samples.",
        {"nu": "1", "K": "3", "q": ["1", "1/2", "1/4", "1/8"]},
    ),
    "Yang-Mills": (
        "BOUND.YM.MATRIX", "transfer_ratios",
        "For n=1..8, the positive rational transfer matrices [[1,q],[q,1]] with q=2^-n have the reported exact subleading-to-leading eigenvalue ratios.",
        {"n_first": 1, "n_last": 8},
    ),
    "Hodge": (
        "BOUND.HODGE.RING", "truncated_polynomial",
        "Within the explicitly presented rational quotient algebra Q[h]/(h^5), h^5=0 and the h^4 coefficients of h^k h^(4-k) are 1 for k=0..4.",
        {"dimension": 4, "relation": "h^5=0"},
    ),
    "Birch-Swinnerton-Dyer": (
        "BOUND.BSD.COUNTS", "elliptic_counts",
        "For the fixed elliptic curve y^2=x^3-x, the reported point counts over eight specified prime fields include one point at infinity.",
        {"curve": "y^2=x^3-x", "primes": [5, 7, 11, 13, 17, 19, 23, 29]},
    ),
    "Poincare": (
        "BOUND.POINCARE.BOUNDARY", "simplex_gf2",
        "The simplicial mod-2 chain complex of the boundary of the four-simplex on five vertices has boundary ranks (4,6,4) and Betti numbers (1,0,0,1).",
        {"vertices": 5, "coefficients": "F2"},
    ),
}

EXPECTED_POLICY = {
    "official_certification": "NOT_CERTIFIED",
    "canonical_tracks": "BLOCKED",
    "scope": SCOPE,
    "accepted_certificate_status": STATUS,
    "automatic_global_promotion": False,
    "formal_kernel_proof": False,
    "independent_expert_review": False,
    "cryptographic_signature": False,
}


def _json_canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _strict_keys(obj: Any, keys: set[str], context: str) -> dict:
    if type(obj) is not dict or set(obj) != keys:
        raise ValueError(f"{context}: invalid or extra keys")
    return obj


def _fraction(value: Any) -> Fraction:
    if (type(value) is not str or len(value) > 48 or
        re.fullmatch(r"-?[0-9]+(?:/[1-9][0-9]*)?", value) is None):
        raise ValueError("invalid canonical exact rational")
    result = Fraction(value)
    if str(result) != value:
        raise ValueError("noncanonical rational witness")
    return result


def _intlist(data: Any, size: int) -> list[int]:
    if type(data) is not list or len(data) != size or any(
        type(v) is not int for v in data
    ):
        raise ValueError("invalid bounded integer list")
    return data


def _is_prime(p: int) -> bool:
    return p > 1 and all(p % k for k in range(2, int(p ** 0.5) + 1))


def _finite_counts(primes: list[int]) -> list[int]:
    counts = []
    for p in primes:
        if not _is_prime(p) or p < 5 or 64 % p == 0:
            raise ValueError("invalid good prime in elliptic-curve model")
        # Independently verify by both quadratic characters and enumeration.
        brute = 1 + sum(
            (y * y - x**3 + x) % p == 0
            for x in range(p) for y in range(p)
        )
        character_sum = sum(
            0 if (a := (x**3-x) % p) == 0 else (
                1 if pow(a, (p-1)//2, p) == 1 else -1
            )
            for x in range(p)
        )
        via_legendre = p + 1 + character_sum
        if brute != via_legendre or (p + 1 - brute)**2 > 4 * p:
            raise RuntimeError("independent elliptic count or Hasse check failed")
        counts.append(brute)
    return counts


def _complex_ranks() -> tuple[list[int], list[int], bool]:
    """Independently derive boundary ranks and Betti numbers using GF(2) sets."""
    cells = {i: list(combinations(range(5), i + 1)) for i in range(4)}
    ranks = {0: 0, 4: 0}
    composition_zero = True
    for d in range(1, 4):
        pivots: dict[tuple[int, ...], set[tuple[int, ...]]] = {}
        for simplex in cells[d]:
            faces = set(combinations(simplex, d))
            while faces:
                lead = max(faces)
                if lead in pivots:
                    faces.symmetric_difference_update(pivots[lead])
                else:
                    pivots[lead] = set(faces)
                    break
            if d >= 2:
                twice: set[tuple[int, ...]] = set()
                for face in combinations(simplex, d):
                    twice.symmetric_difference_update(combinations(face, d - 1))
                composition_zero &= not twice
        ranks[d] = len(pivots)
    betti = [len(cells[d]) - ranks[d] - ranks[d + 1] for d in range(4)]
    return [ranks[d] for d in range(1, 4)], betti, composition_zero


def build_candidates(
    track: str = "all",
) -> list[dict[str, Any]]:
    """Produce witness payloads. These are untrusted until separately checked."""
    if track != "all" and track not in PINNED:
        raise ValueError("unknown digital-twin track")
    selected = list(PINNED) if track == "all" else [track]
    cases = []
    for key in selected:
        claim_id, kind, statement, parameters = PINNED[key]
        if kind == "harmonic_fraction":
            total = sum((Fraction(1, i) for i in range(1, 17)), Fraction(0))
            witness: dict[str, Any] = {"numerator": total.numerator,
                                       "denominator": total.denominator}
        elif kind == "k4_resolution":
            witness = {"resolution": resolution_certificate_k4()}
        elif kind == "abc_exponent_samples":
            q_values = [Fraction(q) for q in parameters["q"]]
            witness = {"exponents": [str(6 * (1-q)) for q in q_values]}
        elif kind == "transfer_ratios":
            witness = {"ratios": [
                str((1-Fraction(1, 2**n)) / (1+Fraction(1, 2**n)))
                for n in range(1, 9)
            ]}
        elif kind == "truncated_polynomial":
            witness = {"h5": 0, "top_pairings": [1] * 5}
        elif kind == "elliptic_counts":
            witness = {"point_counts": _finite_counts(parameters["primes"])}
        elif kind == "simplex_gf2":
            ranks, betti, _ = _complex_ranks()
            witness = {"boundary_ranks": ranks, "betti_mod2": betti}
        else:
            raise AssertionError("unreachable untrusted proof kind")
        cases.append({
            "model_key": key, "claim_id": claim_id,
            "kind": kind, "statement": statement,
            "parameters": parameters, "scope": SCOPE, "witness": witness,
        })
    return cases


def _check_witness(kind: str, parameters: dict, witness: Any) -> str:
    """The only trusted, bounded proof-checking dispatch. No eval/exec/import."""
    if kind == "harmonic_fraction":
        w = _strict_keys(witness, {"numerator", "denominator"}, kind)
        a, b = w["numerator"], w["denominator"]
        if any(type(x) is not int or abs(x) > 10**16 for x in (a, b)) or b <= 0:
            raise ValueError("invalid harmonic rational certificate")
        expected = sum((Fraction(1, k) for k in range(1, 17)), Fraction(0))
        if Fraction(a, b) != expected or b != expected.denominator:
            raise ValueError("incorrect harmonic rational certificate")
        return "EXACT_RATIONAL_SUM"

    if kind == "k4_resolution":
        w = _strict_keys(witness, {"resolution"}, kind)
        proof = w["resolution"]
        if (type(proof) is not dict or
            type(proof.get("steps")) is not list or
            not 0 < len(proof["steps"]) <= MAX_STEPS or
            not verify_resolution_certificate_k4(proof)):
            raise ValueError("resolution refutation rejected")
        clauses = k4_tseitin_clauses()
        if (len(clauses) != 16 or
            any(len(c) != 3 for c in clauses)):
            raise ValueError("wrong 3-CNF model")
        for assignment in product((False, True), repeat=6):
            if all(any(
                assignment[abs(lit)-1] == (lit > 0) for lit in clause
            ) for clause in clauses):
                raise ValueError("unsatisfiable formula had a model")
        return "RESOLUTION_REPLAY_AND_64_ASSIGNMENTS"

    if kind == "abc_exponent_samples":
        w = _strict_keys(witness, {"exponents"}, kind)
        raw = w["exponents"]
        if type(raw) is not list or len(raw) != 4:
            raise ValueError("invalid ABC finite sample sequence")
        nu, K = _fraction(parameters["nu"]), _fraction(parameters["K"])
        if nu != 1 or K != 3:
            raise ValueError("noncanonical conditional exponent inputs")
        expected = [(2*K*(1-_fraction(q))/nu) for q in parameters["q"]]
        if [_fraction(x) for x in raw] != expected:
            raise ValueError("conditional exponent arithmetic incorrect")
        return "EXACT_RATIONAL_EXPONENT_SAMPLES_NOT_PDE"

    if kind == "transfer_ratios":
        w = _strict_keys(witness, {"ratios"}, kind)
        raw = w["ratios"]
        if type(raw) is not list or len(raw) != 8:
            raise ValueError("wrong bounded transfer-model sequence")
        for n, result in enumerate(raw, 1):
            q = Fraction(1, 2**n)
            r = (1-q)/(1+q)
            # Trace and determinant of the fixed 2x2 matrix
            if (1+q)+(1-q) != 2 or (1+q)*(1-q) != 1-q*q:
                raise RuntimeError("transfer-matrix invariant failure")
            if _fraction(result) != r or not 0 < r < 1:
                raise ValueError("transfer ratio certificate incorrect")
        return "EXACT_RATIONAL_FINITE_TRANSFER_SPECTRA"

    if kind == "truncated_polynomial":
        w = _strict_keys(witness, {"h5", "top_pairings"}, kind)
        if type(w["h5"]) is not int or w["h5"] != 0:
            raise ValueError("h^5 is nonzero in the wrong model")
        pairings = _intlist(w["top_pairings"], 5)
        # Coefficient convolution in Z[h]/(h^5) realizes the rational
        # coefficient model on integer basis monomials.
        def mul(i: int, j: int) -> list[int]:
            a, b = [0]*5, [0]*5
            a[i] = b[j] = 1
            coeff = [0]*5
            for x, ax in enumerate(a):
                for y, by in enumerate(b):
                    if x+y < 5:
                        coeff[x+y] += ax*by
            return coeff
        expect = [mul(i, 4-i)[4] for i in range(5)]
        if pairings != expect or expect != [1]*5:
            raise ValueError("wrong finite quotient-algebra pairing")
        return "EXACT_TRUNCATED_QUOTIENT_ALGEBRA"

    if kind == "elliptic_counts":
        w = _strict_keys(witness, {"point_counts"}, kind)
        raw = _intlist(w["point_counts"], 8)
        if raw != _finite_counts(parameters["primes"]):
            raise ValueError("incorrect finite-field point count")
        return "EXACT_ENUMERATION_AND_LEGENDRE_CROSSCHECK"

    if kind == "simplex_gf2":
        w = _strict_keys(witness, {"boundary_ranks", "betti_mod2"}, kind)
        ranks = _intlist(w["boundary_ranks"], 3)
        betti = _intlist(w["betti_mod2"], 4)
        actual_ranks, actual_betti, squared_zero = _complex_ranks()
        if (not squared_zero or ranks != actual_ranks or
            betti != actual_betti or ranks != [4, 6, 4] or
            betti != [1, 0, 0, 1]):
            raise ValueError("wrong finite GF(2) chain complex certificate")
        return "EXACT_GF2_BOUNDARY_AND_RANK_CHECK"

    raise ValueError(f"unknown proof kind {kind!r}")


def verify_candidates(
    candidates: Any, *,
    track: str = "all",
    manifest_path: Path = MANIFEST,
    register_path: Path = OBLIGATIONS,
    targets_path: Path = TARGETS_PATH,
    hypotheses_path: Path = HYPOTHESES,
) -> dict[str, Any]:
    """Fail closed on *all* input changes or witness errors, without promotion."""
    originals = {
        "claim_manifest": manifest_path.read_bytes(),
        "obligations": register_path.read_bytes(),
        "targets": targets_path.read_bytes(),
        "hypotheses": hypotheses_path.read_bytes(),
        "verifier": Path(__file__).read_bytes(),
    }
    audit = audit_clay_alignment(
        targets_path=targets_path, register_path=register_path,
        hypotheses_path=hypotheses_path,
    )
    if audit["certification"] != "NOT_CERTIFIED" or audit["open_work_packages"] != 14:
        raise ValueError("canonical proof assurance gate changed")

    manifest = json.loads(originals["claim_manifest"])
    _strict_keys(manifest, {"schema_version", "purpose", "policy", "claims"},
                 "manifest")
    if (manifest["schema_version"] != "1.0.0" or
        manifest["policy"] != EXPECTED_POLICY or
        not isinstance(manifest["purpose"], str) or
        "not Millennium theorem certification" not in manifest["purpose"]):
        raise ValueError("manifest attempts to change the proof scope")
    claim_records = manifest["claims"]
    if type(claim_records) is not list or len(claim_records) != 7:
        raise ValueError("manifest must have exactly seven bounded claims")
    entries = {}
    for entry in claim_records:
        _strict_keys(entry, {
            "model_key", "claim_id", "kind", "statement",
            "parameters", "scope", "limitations", "complete_millennium_problem"
        }, "manifest claim")
        key = entry["model_key"]
        if key not in PINNED or key in entries:
            raise ValueError("unknown or repeated bounded claim")
        cid, kind, statement, params = PINNED[key]
        if ((entry["claim_id"], entry["kind"], entry["statement"]) !=
            (cid, kind, statement) or
            _json_canonical(entry["parameters"]) != _json_canonical(params) or
            entry["scope"] != SCOPE or
            entry["complete_millennium_problem"] is not False or
            type(entry["limitations"]) is not str or
            len(entry["limitations"]) < 60):
            raise ValueError(f"{key}: scope drift or forged claim manifest")
        entries[key] = entry
    if set(entries) != set(PINNED):
        raise ValueError("missing pinned claim")

    if track != "all" and track not in PINNED:
        raise ValueError("unknown digital-twin track")
    selected = list(PINNED) if track == "all" else [track]
    if type(candidates) is not list or len(candidates) != len(selected):
        raise ValueError("one candidate per selected track is required")
    seen = set()
    receipts = []
    for item in candidates:
        _strict_keys(item, {
            "model_key", "claim_id", "kind", "statement",
            "parameters", "scope", "witness"
        }, "candidate")
        key = item["model_key"]
        if key not in selected or key in seen:
            raise ValueError("unknown, duplicated or mismatched candidate")
        seen.add(key)
        cid, kind, statement, params = PINNED[key]
        if ((item["claim_id"], item["kind"], item["statement"]) !=
            (cid, kind, statement) or
            _json_canonical(item["parameters"]) != _json_canonical(params) or
            item["scope"] != SCOPE):
            raise ValueError(f"{key}: certificate cannot establish a broader claim")
        verified_by = _check_witness(kind, params, item["witness"])
        receipts.append({
            "model_key": key, "claim_id": cid, "statement": statement,
            "scope": SCOPE,
            "bounded_certificate_status": STATUS,
            "checker_method": verified_by,
            "witness_sha256": _digest(_json_canonical(item["witness"])),
            "official_problem_certification": "NOT_CERTIFIED",
            "global_proof_completed": False,
            "canonical_mathematical_state": "BLOCKED",
            "independent_expert_review": False,
            "formal_kernel_check": False,
            "limitations": entries[key]["limitations"],
        })
    if set(selected) != seen:
        raise ValueError("missing candidate witness")

    for name, path in (
        ("claim_manifest", manifest_path), ("obligations", register_path),
        ("targets", targets_path), ("hypotheses", hypotheses_path),
        ("verifier", Path(__file__)),
    ):
        if path.read_bytes() != originals[name]:
            raise RuntimeError("trusted digital-twin source changed during verification")

    report = {
        "schema_version": "1.0.0",
        "digital_twin": "MathOS/fixed-scope-claim-certificate-v1",
        "source_sha256": {k: _digest(v) for k, v in originals.items()},
        "certification": "NOT_CERTIFIED",
        "canonical_proof_promotion": "NONE",
        "open_millennium_obligations": 14,
        "full_millennium_solutions_certified": 0,
        "bounded_certificates_verified": len(receipts),
        "bounded_status_definition": (
            "Exact finite arithmetic or resolution witness replayed for the "
            "PINNED stated mathematical object only, not a Clay proof"
        ),
        "cryptographically_signed": False,
        "witness_attestations": receipts,
    }
    report["report_sha256"] = _digest(_json_canonical(report))
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--track", default="all")
    parser.add_argument("--input", type=Path, default=None,
                        help="optional untrusted JSON list of bounded claim witnesses")
    parser.add_argument("--output-dir", type=Path,
                        default=Path("artifacts/claim-twin"))
    args = parser.parse_args(argv)
    if args.input is None:
        candidates = build_candidates(args.track)
    else:
        if args.input.stat().st_size > MAX_INPUT_BYTES:
            raise ValueError("certificate input exceeds size cap")
        candidates = json.loads(args.input.read_bytes())
    report = verify_candidates(candidates, track=args.track)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "bounded_claim_certificates.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "bounded_certificates_verified": report["bounded_certificates_verified"],
        "official_certification": report["certification"],
        "full_millennium_solutions_certified": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
