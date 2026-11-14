"""Seven Millennium-problem hypothesis probes with separate certification safeguards.

Exploratory experiments are permitted while a mathematical obligation is BLOCKED.
No probe can promote a proof or change the canonical obligation register.
Python 3.10+, standard library only. Run from repository root:
  python -m mathos.research.hypothesis_pipeline
  python -m mathos.research.hypothesis_pipeline --output-dir artifacts/hypotheses
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
import math
from pathlib import Path

from mathos.research.millennium_attacks_002 import abc_identities

ROOT = Path(__file__).resolve().parents[2]
OBLIGATIONS = ROOT / "docs/proof-analysis/OBLIGATIONS.v1.json"
HYPOTHESES = ROOT / "docs/research/HYPOTHESES.v1.json"
EXPECTED_PROBES = {
    "Riemann": "li_first_coefficient",
    "P-versus-NP": "k4_tseitin",
    "Navier-Stokes": "abc_perturbation_bound",
    "Yang-Mills": "transfer_gap_obstruction",
    "Hodge": "projective_hodge",
    "Birch-Swinnerton-Dyer": "elliptic_local_counts",
    "Poincare": "simplicial_three_sphere",
}


def probe_li_first_coefficient() -> dict:
    """Non-certified floating-point check of known positive lambda_1.

    Classical inequality for gamma:
      H_n - log(n) - 1/(2n) < gamma
      gamma < H_n - log(n) - 1/(2(n+1)).
    Floating-point evaluation of logs is NOT interval arithmetic.
    """
    n = 2048
    harmonic = math.fsum(1.0 / k for k in range(1, n + 1))
    delta = harmonic - math.log(n)
    low_gamma = delta - 1 / (2 * n)
    high_gamma = delta - 1 / (2 * (n + 1))
    offset = 1 - math.log(4 * math.pi) / 2
    lower = offset + low_gamma / 2
    upper = offset + high_gamma / 2
    return {
        "passed": 0 < lower < upper < 0.1,
        "n": n, "lambda1_lower_approx": lower, "lambda1_upper_approx": upper,
        "scope": "first Li coefficient only; numerical logs, not certified intervals",
    }


def k4_tseitin_clauses() -> tuple[tuple[int, ...], ...]:
    """Odd total XOR charge on K4, encoded by 16 clauses of width 3."""
    edges = tuple(combinations(range(4), 2))  # six edge variables
    result: list[tuple[int, ...]] = []
    for vertex in range(4):
        incident = tuple(i + 1 for i, edge in enumerate(edges) if vertex in edge)
        assert len(incident) == 3
        charge = 1 if vertex == 0 else 0  # odd total charge => contradiction
        for bits in product((0, 1), repeat=3):
            if sum(bits) % 2 != charge:
                result.append(tuple(sorted(
                    -variable if bit else variable
                    for variable, bit in zip(incident, bits))))
    return tuple(sorted(result))


def _resolvent(
    a: tuple[int, ...], b: tuple[int, ...], pivot: int
) -> tuple[int, ...] | None:
    if pivot in a and -pivot in b:
        leftovers = (set(a) - {pivot}) | (set(b) - {-pivot})
    elif -pivot in a and pivot in b:
        leftovers = (set(a) - {-pivot}) | (set(b) - {pivot})
    else:
        return None
    if any(-x in leftovers for x in leftovers):
        return None  # tautological resolvent
    return tuple(sorted(leftovers))


def resolution_certificate_k4() -> dict:
    """Compute a finite resolution closure and record a checkable refutation."""
    initial = k4_tseitin_clauses()
    known = list(initial)
    seen = set(initial)
    steps = []
    i = 0
    while i < len(known):
        a = known[i]
        for j in range(i):
            b = known[j]
            for pivot in sorted({abs(lit) for lit in a if -lit in b}):
                conclusion = _resolvent(a, b, pivot)
                if conclusion is None or conclusion in seen:
                    continue
                seen.add(conclusion)
                steps.append({"left": i, "right": j, "pivot": pivot,
                              "clause": list(conclusion)})
                known.append(conclusion)
                if not conclusion:
                    return {"initial": [list(c) for c in initial],
                            "steps": steps, "last": len(known) - 1}
                if len(known) > 1000:
                    raise RuntimeError("finite K4 resolution budget exceeded")
        i += 1
    raise RuntimeError("no resolution refutation discovered for contradictory K4")


def verify_resolution_certificate_k4(proof: dict) -> bool:
    """Independently replay all recorded resolution operations and final empty."""
    if type(proof) is not dict:
        return False
    initial = [list(c) for c in k4_tseitin_clauses()]
    if proof.get("initial") != initial or type(proof.get("steps")) is not list:
        return False
    known = [tuple(c) for c in initial]
    for step in proof["steps"]:
        if type(step) is not dict:
            return False
        try:
            a, b, pivot = step["left"], step["right"], step["pivot"]
            if any(type(x) is not int for x in (a, b, pivot)):
                return False
            if not (0 <= a < len(known) and 0 <= b < len(known) and pivot > 0):
                return False
            new = _resolvent(known[a], known[b], pivot)
            if new is None or step["clause"] != list(new):
                return False
            known.append(new)
        except (KeyError, ValueError, TypeError):
            return False
    return proof.get("last") == len(known) - 1 and known[-1] == ()


def probe_k4_tseitin() -> dict:
    clauses = k4_tseitin_clauses()
    variables = 6
    satisfying_assignments = 0
    for bits in product((False, True), repeat=variables):
        if all(any(bits[abs(lit) - 1] == (lit > 0) for lit in clause)
               for clause in clauses):
            satisfying_assignments += 1
    certificate = resolution_certificate_k4()
    verified = verify_resolution_certificate_k4(certificate)
    occurrence = {lit for clause in clauses for lit in clause}
    return {
        "passed": len(clauses) == 16 and all(len(x) == 3 for x in clauses)
                  and occurrence == {i for j in range(1, 7) for i in (j, -j)}
                  and satisfying_assignments == 0 and verified,
        "variables": variables, "clauses": len(clauses),
        "satisfying_assignments": satisfying_assignments,
        "resolution_steps": len(certificate["steps"]),
        "refutation_verified": verified,
        "scope": "one bounded K4 Tseitin instance; no asymptotic complexity lower bound",
    }


def probe_abc_perturbation_bound() -> dict:
    """Conditional L2 energy estimate for smooth perturbations about ABC.

    Jacobian of the A=B=C=1 ABC field has six entries each bounded by 1.
    Hence operator norm <= Frobenius norm <= sqrt(6) < K=3.
    If E(t)=||w(t)||_2^2, then E'(t) <= 2 K exp(-nu*t) E(t).
    Integrated bound E(t) <= exp(2 K (1-exp(-nu*t))/nu) E(0).
    This assumes a smooth solution w exists and does NOT grant regularity.
    """
    identities = abc_identities()
    required = ("divergence_zero", "curl_equals_velocity",
                "laplacian_equals_negative_velocity",
                "convection_equals_pressure_gradient_cancelled",
                "convection_nonzero")
    values = []
    K = 3
    nu = Fraction(1, 1)
    for q in (Fraction(1), Fraction(1, 2), Fraction(1, 4), Fraction(1, 8)):
        exponent = Fraction(2 * K, 1) * (1 - q) / nu
        values.append({"exp_minus_nu_t": str(q), "gronwall_exponent": str(exponent)})
    return {
        "passed": all(identities[key] for key in required) and K * K > 6
                  and [Fraction(x["gronwall_exponent"]) for x in values]
                  == [Fraction(0), Fraction(3), Fraction(9, 2), Fraction(21, 4)],
        "gradient_operator_bound_K": K, "nu": str(nu),
        "sample_exponents": values,
        "scope": "conditional L2 perturbation energy, not global 3D regularity",
    }


def probe_transfer_gap_obstruction() -> dict:
    """Two-state transfer-model ratios: each gap>0, no uniform gap as q->0.

    Eigenvalue ratio r(q)=(1-q)/(1+q), with q=exp(-2 beta) in (0,1).
    r<1 for each q, but r->1 as q->0; -log(r)->0.
    Neither beta nor this 2x2 transfer matrix defines 4D Yang-Mills.
    """
    rows = []
    for n in range(1, 9):
        q = Fraction(1, 2**n)
        r = (1 - q) / (1 + q)
        difference = 1 - r
        rows.append({"n": n, "q": str(q), "eigenvalue_ratio": str(r),
                     "one_minus_ratio": str(difference)})
    ratios = [Fraction(row["eigenvalue_ratio"]) for row in rows]
    return {
        "passed": all(0 < r < 1 for r in ratios) and
                  all(a < b for a, b in zip(ratios, ratios[1:])) and
                  all(Fraction(row["one_minus_ratio"]) == 2 * Fraction(row["q"]) /
                      (1 + Fraction(row["q"])) for row in rows),
        "samples": rows, "limit_as_q_to_zero": "eigenvalue ratio -> 1; gap -> 0",
        "scope": "two-state regulated toy, not non-Abelian continuum Yang-Mills",
    }


def probe_projective_hodge() -> dict:
    """Formal hyperplane ring Q[h]/(h^(n+1)) for known projective spaces."""
    n = 4
    # Multiplication of monomials in H*(CP^n; Q); coeffs are exact.
    def multiply(a: tuple[int, Fraction], b: tuple[int, Fraction]):
        exponent = a[0] + b[0]
        return (exponent, a[1] * b[1] if exponent <= n else Fraction(0))
    h = (1, Fraction(1))
    powers = [(0, Fraction(1))]
    for _ in range(n + 1):
        powers.append(multiply(powers[-1], h))
    pairings = [
        multiply(powers[p], powers[n - p])[1]
        for p in range(n + 1)
    ]
    return {
        "passed": all(powers[i] == (i, Fraction(1)) for i in range(n + 1))
                  and powers[n + 1][1] == 0 and pairings == [1] * (n + 1),
        "projective_dimension": n, "top_degree_pairings": [int(x) for x in pairings],
        "h_to_n_plus_one": str(powers[n + 1][1]),
        "scope": "known projective-space algebraic classes; not primitive Hodge classes",
    }


def probe_elliptic_local_counts() -> dict:
    """Point counts on E: y^2=x^3-x mod p, p>=5, via independent methods."""
    primes = (5, 7, 11, 13, 17, 19, 23, 29)
    rows = []
    for p in primes:
        brute = 1 + sum(
            (y * y - (x**3 - x)) % p == 0
            for x in range(p) for y in range(p))
        residues = {(y * y) % p for y in range(p)}
        character_count = 1 + sum(
            1 if (x**3 - x) % p == 0
            else 2 if (x**3 - x) % p in residues else 0
            for x in range(p))
        trace = p + 1 - brute
        rows.append({"p": p, "points": brute, "trace": trace,
                     "same_independent_count": brute == character_count,
                     "hasse_bound": trace * trace <= 4 * p})
    return {
        "passed": all(r["same_independent_count"] and r["hasse_bound"] for r in rows),
        "curve": "y^2=x^3-x", "local_data": rows,
        "scope": "good-prime finite-field counts; not algebraic/analytic ranks or Sha",
    }


def _gf2_rank(columns: list[int]) -> int:
    pivots: dict[int, int] = {}
    for vector in columns:
        while vector:
            leading = vector.bit_length() - 1
            if leading in pivots:
                vector ^= pivots[leading]
            else:
                pivots[leading] = vector
                break
    return len(pivots)


def probe_simplicial_three_sphere() -> dict:
    """Mod-2 homology of boundary of the 4-simplex (triangulated S^3)."""
    cells = {d: list(combinations(range(5), d + 1)) for d in range(4)}
    boundary: dict[int, list[int]] = {}
    for d in range(1, 4):
        index = {face: j for j, face in enumerate(cells[d - 1])}
        boundary[d] = [
            sum(1 << index[face] for face in combinations(simplex, d))
            for simplex in cells[d]
        ]
    composition_zero = True
    for d in range(2, 4):
        for column in boundary[d]:
            result = 0
            for i, lower in enumerate(boundary[d - 1]):
                if column & (1 << i):
                    result ^= lower
            composition_zero &= result == 0
    ranks = {0: 0, 4: 0}
    ranks.update({d: _gf2_rank(boundary[d]) for d in range(1, 4)})
    betti = [len(cells[d]) - ranks[d] - ranks[d + 1] for d in range(4)]
    euler = sum((-1)**d * len(cells[d]) for d in range(4))
    return {
        "passed": composition_zero and betti == [1, 0, 0, 1] and euler == 0,
        "simplices": {str(k): len(v) for k, v in cells.items()},
        "betti_mod_2": betti, "euler_characteristic": euler,
        "boundary_squared_zero": composition_zero,
        "scope": "known triangulated S3 only; homology does not certify simple connectivity",
    }


PROBES = {
    "li_first_coefficient": probe_li_first_coefficient,
    "k4_tseitin": probe_k4_tseitin,
    "abc_perturbation_bound": probe_abc_perturbation_bound,
    "transfer_gap_obstruction": probe_transfer_gap_obstruction,
    "projective_hodge": probe_projective_hodge,
    "elliptic_local_counts": probe_elliptic_local_counts,
    "simplicial_three_sphere": probe_simplicial_three_sphere,
}


def run_exploration(
    register_path: Path = OBLIGATIONS,
    hypothesis_path: Path = HYPOTHESES,
) -> dict:
    """Execute bounded experiments while retaining all proof-promotion gates."""
    original_register = register_path.read_bytes()
    original_hypotheses = hypothesis_path.read_bytes()
    register = json.loads(original_register)
    program = json.loads(original_hypotheses)
    if register.get("certification") != "NOT_CERTIFIED" or (
        program.get("certification") != "NOT_CERTIFIED"
        or program.get("exploration_policy") != "ALLOW_BLOCKED_RESEARCH_WITHOUT_PROMOTION"
    ):
        raise ValueError("non-certification / exploration policy invariant violated")
    tracks = {t["model_key"]: t for t in register["tracks"]}
    experiments = program["experiments"]
    if len(tracks) != 7 or len(experiments) != 7:
        raise ValueError("expected exactly seven Millennium tracks")
    if len({x["model_key"] for x in experiments}) != 7:
        raise ValueError("hypothesis tracks are missing or duplicated")
    if set(tracks) != set(EXPECTED_PROBES):
        raise ValueError("canonical track identity differs from pinned names")
    if program.get("schema_version") != "1.0.0":
        raise ValueError("unsupported hypothesis program schema")
    if not (register["external_result"]["graph_state"] == "established_external"
            and register["external_result"]["claim_id"] == "POINCARE.published"):
        raise ValueError("externally solved Poincare status must remain distinct")
    records = []
    for hypothesis in experiments:
        key = hypothesis["model_key"]
        if key not in tracks:
            raise ValueError("hypothesis not found in proof register")
        track = tracks[key]
        obligations = track["work_packages"]
        if track["modeled_target_status"] != "BLOCKED" or any(
            p["graph_state"] != "open" or p["review_verdict"] != "not_reviewed"
            or p["formal_check"] != "not_performed" for p in obligations
        ):
            raise ValueError("open-obligation safety invariant violated")
        if set(hypothesis["obligations"]) != {p["claim_id"] for p in obligations}:
            raise ValueError(f"hypothesis obligation mismatch: {key}")
        if hypothesis.get("novelty_claim") is not False:
            raise ValueError("unauthorized mathematical novelty claim")
        probe_id = hypothesis["bounded_probe"]
        if probe_id != EXPECTED_PROBES[key]:
            raise ValueError("untrusted or wrong probe mapping")
        for required in ("hypothesis", "use_case", "falsifier",
                         "next_lemma", "missing_global_step", "source"):
            if not isinstance(hypothesis.get(required), str) or not hypothesis[required]:
                raise ValueError(f"missing hypothesis field: {key}.{required}")
        result = PROBES[probe_id]()
        if result["passed"] is not True:
            raise RuntimeError(f"bounded probe failed: {key}")
        records.append({
            "model_key": key, "hypothesis_id": hypothesis["id"],
            "hypothesis": hypothesis["hypothesis"],
            "use_case": hypothesis["use_case"],
            "next_lemma": hypothesis["next_lemma"],
            "missing_global_step": hypothesis["missing_global_step"],
            "probe": probe_id, "probe_result": result,
            "exploration_state": "EXPLORATORY_TESTED",
            "mathematical_status": "BLOCKED",
            "certification": "NOT_CERTIFIED",
            "promoted_to_solution": False,
        })
    report = {
        "schema_version": "1.0.0",
        "certification": "NOT_CERTIFIED",
        "external_poincare": "ESTABLISHED_EXTERNALLY_ONLY",
        "proof_promotion": "NONE",
        "allow_blocked_exploration": True,
        "all_probes_passed": True,
        "open_work_packages": sum(len(t["work_packages"]) for t in tracks.values()),
        "source_sha256": {
            "register": hashlib.sha256(original_register).hexdigest(),
            "hypotheses": hashlib.sha256(original_hypotheses).hexdigest(),
        },
        "experiments": records,
        "limitations": [
            "All seven probes are intentionally bounded examples or conditional estimates.",
            "Passing a numerical test or finite model is not a Millennium theorem.",
            "The canonical obligations and third-party problem statuses are untouched.",
        ],
    }
    if report["open_work_packages"] != 14:
        raise ValueError("canonical open-work-package count unexpectedly changed")
    if register_path.read_bytes() != original_register:
        raise RuntimeError("canonical proof register modified during exploration")
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args(argv)
    report = run_exploration()
    formatted = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output_dir is None:
        print(formatted, end="")
    else:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "seven_hypotheses_report.json").write_text(
            formatted, encoding="utf-8")
        print("Wrote exploration-only report; certification remains NOT_CERTIFIED")


if __name__ == "__main__":
    main()
