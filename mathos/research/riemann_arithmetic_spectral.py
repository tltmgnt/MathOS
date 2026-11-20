"""TECT-X arithmetic spectral candidate with RH Weyl law and a failed identity test.

This is a diagonal self-adjoint toy operator built from the Riemann--von
Mangoldt *main term*, plus an optional von Mangoldt prime-power perturbation.
It cannot prove RH. Finite checks supplement the analytic arguments in docs.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
import hashlib
import json
import math
from pathlib import Path

TAU = 2.0 * math.pi
FIRST_ZETA_ZERO_REFERENCE = 14.134725141734693  # externally tabulated, not re-evaluated
MAX_INDEX = 4096


def von_mangoldt(n: int) -> float:
    """Λ(n): log p for n=p^k, k>=1; zero otherwise; also Λ(1)=0."""
    if type(n) is not int or n < 1:
        raise ValueError("n must be a positive integer")
    if n == 1:
        return 0.0
    x = n
    base = None
    d = 2
    while d * d <= x:
        if x % d == 0:
            if base is not None:
                return 0.0
            base = d
            while x % d == 0:
                x //= d
        d += 1 if d == 2 else 2
    if x != 1:
        if base is not None:
            return 0.0
        base = x
    return math.log(base)


def main_term(t: float) -> float:
    """F(T)=T/(2pi)*(log(T/(2pi))-1), T>0."""
    if not math.isfinite(t) or t <= 0:
        raise ValueError("positive finite T required")
    u = t / TAU
    return u * (math.log(u) - 1.0)


def inverse_main_term(n: int) -> float:
    """Unique T>2*pi*e satisfying F(T)=n, via fixed bracketing."""
    if type(n) is not int or not 1 <= n <= MAX_INDEX:
        raise ValueError("index outside supported range")
    lo = math.e
    hi = max(math.e * 2, float(n) + math.e)
    while hi * (math.log(hi) - 1) < n:
        hi *= 2
    for _ in range(90):
        mid = (lo + hi) / 2
        if mid * (math.log(mid) - 1) >= n:
            hi = mid
        else:
            lo = mid
    return TAU * (lo + hi) / 2


def arithmetic_shift(n: int) -> float:
    """Bounded prime-power perturbation 0<=Λ(n)/(1+log(n+1))<1."""
    return von_mangoldt(n) / (1.0 + math.log(n + 1))


def eigenvalue(n: int, epsilon: float = 1.0) -> float:
    if not isinstance(epsilon, (int, float)) or not math.isfinite(epsilon) or not 0 <= epsilon <= 1:
        raise ValueError("epsilon must lie between 0 and 1")
    return inverse_main_term(n) + epsilon * arithmetic_shift(n)


def spectral_count(t: float, eigenvalues: list[float]) -> int:
    if not math.isfinite(t) or t < 0:
        raise ValueError("nonnegative finite T required")
    if not eigenvalues or any(not math.isfinite(v) for v in eigenvalues):
        raise ValueError("nonempty finite eigenvalue list required")
    return bisect_right(sorted(eigenvalues), t)


def build_report(max_index: int = 2048, epsilon: float = 1.0) -> dict:
    if type(max_index) is not int or not 32 <= max_index <= MAX_INDEX:
        raise ValueError("max_index must lie between 32 and 4096")
    if not isinstance(epsilon, (int, float)) or not math.isfinite(epsilon) or not 0 <= epsilon <= 1:
        raise ValueError("epsilon must lie between 0 and 1")
    base = [inverse_main_term(n) for n in range(1, max_index + 1)]
    shifted = [v + epsilon * arithmetic_shift(n) for n, v in enumerate(base, 1)]
    thresholds = (25.0, 50.0, 100.0, 250.0, 500.0)
    if min(base[-1], shifted[-1]) <= max(thresholds):
        raise ValueError("insufficient eigenvalue coverage for T <= 500")
    rows = []
    for t in thresholds:
        f = main_term(t)
        base_count = spectral_count(t, base)
        count = spectral_count(t, shifted)
        # The exact mathematical inequality N_0(T-1) <= N_epsilon(T) <= N_0(T)
        # follows termwise from 0 <= epsilon*delta_n <= 1.
        lower = spectral_count(max(0.0, t - 1), base)
        if not lower <= count <= base_count:
            raise AssertionError("bounded prime-power perturbation count invariant failed")
        rows.append({
            "height": t,
            "rv_mangoldt_main_term": f,
            "unperturbed_count": base_count,
            "arithmetic_count": count,
            "count_bracket_lower": lower,
            "count_bracket_upper": base_count,
            "arithmetic_minus_main_term": count - f,
        })
    # Truncated positive heat-trace diagnostic, NOT a zeta explicit formula.
    heat_t = 0.1
    heat_n = 256
    heat_base = math.fsum(math.exp(-heat_t * v) for v in base[:heat_n])
    heat_arithmetic = math.fsum(math.exp(-heat_t * v) for v in shifted[:heat_n])
    if heat_arithmetic > heat_base + 1e-12:
        raise AssertionError("heat-trace monotonicity violated")
    first = base[0]
    if not first > TAU * math.e > FIRST_ZETA_ZERO_REFERENCE:
        raise AssertionError("documented first-zero mismatch invariant failed")
    return {
        "schema": "mathos_tectx_rh_arithmetic_spectral/1",
        "status": "DENSITY_MATCHES_BUT_ZERO_IDENTITY_REFUTED_FOR_THIS_OPERATOR",
        "operator": "diagonal H_epsilon on l2(N>=1), H e_n = lambda_n(epsilon)*e_n",
        "domain": "{a in l2: sum_n lambda_n(epsilon)^2*|a_n|^2 < infinity}",
        "lambda_definition": "F(lambda_n(0))=n, lambda_n(0)>2*pi*e; F(T)=T/(2*pi)*(log(T/(2*pi))-1)",
        "prime_power_perturbation": "lambda_n(epsilon)=lambda_n(0)+epsilon*Lambda(n)/(1+log(n+1))",
        "epsilon": epsilon,
        "max_index_computed": max_index,
        "zero_count_comparison": {
            "theorem": "N_H_epsilon(T)=F(T)+O(log T); matches Riemann-von Mangoldt up to its known O(log T) remainder",
            "proof": "N_0(T-1) <= N_epsilon(T) <= N_0(T); N_0(T)=floor(F(T)) for T>=lambda_1; F'(T)=log(T/(2*pi))/(2*pi)",
            "rows": rows,
        },
        "spectrum_and_trace": {
            "self_adjointness": "diagonal real multiplication on its maximal weighted l2 domain",
            "compact_resolvent": True,
            "heat_trace": "Tr(exp(-t H_epsilon)) = sum_{n>=1} exp(-t lambda_n(epsilon)), t>0",
            "spectral_determinant": "D_epsilon(z)=prod_{n>=1}(1-z^2/lambda_n(epsilon)^2), converges locally uniformly",
            "positive_heat_parameter": heat_t,
            "heat_prefix_length": heat_n,
            "finite_heat_trace_unperturbed": heat_base,
            "finite_heat_trace_arithmetic": heat_arithmetic,
            "trace_identity_status": "NOT_DERIVED",
            "prime_explicit_formula_status": "NOT_DERIVED",
            "first_eigenvalue": first,
            "external_first_zeta_ordinate_reference": FIRST_ZETA_ZERO_REFERENCE,
            "first_ordinate_mismatch": True,
            "distinct_operators_share_asymptotic": True,
        },
        "missing_bridges": [
            "Derive a prime-side trace or resolvent formula with rigorously justified regularization, independently of any assumed RH zero locations",
            "Prove a noncircular determinant/zero-correspondence including all nontrivial zeros and multiplicities",
            "Explain and repair the actual first-zero mismatch; matching counting density is insufficient",
            "Review whether the operator is arithmetically canonical rather than an inverse engineered from the already-known counting main term",
        ],
        "external_reference": {
            "zero_table": "https://www.lmfdb.org/zeros/zeta/",
            "zero_count": "https://mathworld.wolfram.com/Riemann-vonMangoldtFormula.html",
        },
        "assurance": {
            "riemann_hypothesis_proved": False,
            "spectral_zero_identity_established": False,
            "clay_route_closed": False,
            "independent_review_completed": False,
            "novel_mathematical_theorem_claimed": False,
        },
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "limitations": [
            "Diagonal eigenvalues are reverse engineered from a known zero-counting main term; no connection to zeta zeros follows.",
            "The finite prefix heat trace is a diagnostic, not the full trace or an independent analytic proof.",
            "The Riemann-von Mangoldt error bound is invoked as an established external theorem, not proved here.",
            "Numerical values are float64 and are not certified interval enclosures; analytic results are documented separately.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-index", type=int, default=2048)
    parser.add_argument("--epsilon", type=float, default=1.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = build_report(args.max_index, args.epsilon)
    except (ValueError, OverflowError) as exc:
        parser.error(str(exc))
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
