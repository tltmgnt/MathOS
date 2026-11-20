"""TECT-X: exact rational *analytic* bound on omitted Weil prime powers.

For a=1/50, Gaussian-cosine centers c_j in [0,1/2], and prime cutoff
N >= 256, gives a conservative uniform bound on the OMITTED prime-power
part of every Weil Gram entry. This is independent of zeta zero data and
does not assume RH.

Only this one analytical tail is bounded. Other errors (digamma evaluation,
quadrature, floating-point matrix entries) remain UNBOUNDED in the parent
experiment, so this does NOT certify even a finite Weil Gram PSD claim.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

DEFAULT_GAUSSIAN_A = Fraction(1, 50)
CENTER_UPPER = Fraction(1, 2)
MIN_CUTOFF = 256
# Each entry h_jk uses c_j+c_k <=1 and a=1/50.
U_LOWER = Fraction(5)
C_BOUND = Fraction(1)
K = 16


def _as_string(f: Fraction) -> str:
    return f"{f.numerator}/{f.denominator}"


def per_entry_prime_tail_bound() -> Fraction:
    """Exact rational upper bound for sum_{n>256} omitted Weil prime terms.

    On u=log n >=5, the elementary log derivatives show
    f(x) = log(x)*x^(-1/2)*exp(-(log x-1)^2/(4a))
    decreases. Bound the integer tail by its integral. Complete the square:
    integral_5^infty u exp(u/2-(u-1)^2/(4a))du
      = exp(1/2+a/4) * integral_5^infty u exp(-(u-1-a)^2/(4a))du.

    Since (u-1-a)^2 >= (5-1-a)^2 +2(5-1-a)(u-5),
    the remaining integral is <= exp(-X)*(5/beta+1/beta^2),
    beta=(5-1-a)/(2a), X=(5-1-a)^2/(4a).

    1/(sqrt(pi*a))<5 since pi>3; exp(1/2+a/4)<2
    since 1/2+1/200 <2/3<log(2); and exp(-X) <=
    (1+X/16)^(-16). All these are standard real inequalities.

    Thus the omitted prime-power term of every W_jk has magnitude
    at most 10 * (5/beta+1/beta²) / (1+X/16)^16.
    No floating point appears in the bound.
    """
    a = DEFAULT_GAUSSIAN_A
    beta = (U_LOWER - C_BOUND - a)/(2*a)
    exponent = (U_LOWER - C_BOUND - a)**2/(4*a)
    return 10 * (U_LOWER/beta + 1/(beta*beta)) / (1+exponent/K)**K


def gram_quadratic_tail_bound(dimension: int) -> Fraction:
    """Operator-norm/real Rayleigh error bound m*delta for m×m entries.

    For any real vector x, |x^T E x| <= delta*(sum|x_j|)^2
      <= m*delta*||x||_2².
    """
    if type(dimension) is not int or not 1 <= dimension <= 100000:
        raise ValueError("dimension must be an integer in 1..100000")
    return dimension * per_entry_prime_tail_bound()


def report(centers: tuple[Fraction, ...] = (
    Fraction(0), Fraction(1, 5), Fraction(1, 2)),
    prime_cutoff: int = MIN_CUTOFF) -> dict:
    if type(prime_cutoff) is not int or not MIN_CUTOFF <= prime_cutoff <= 10**9:
        raise ValueError("prime cutoff must be an integer >=256 and <=1e9")
    if (not isinstance(centers, tuple) or not 1 <= len(centers) <= 20
            or any(not isinstance(c, Fraction) or not 0 <= c <= CENTER_UPPER
                   for c in centers)):
        raise ValueError("centers must be 1..20 rational values in [0,1/2]")
    per = per_entry_prime_tail_bound()
    global_norm = gram_quadratic_tail_bound(len(centers))
    return {
        "schema": "mathos_tectx_weil_uniform_prime_tail/1",
        "status": "ANALYTIC_PRIME_TAIL_BOUND_ONLY_NOT_GLOBAL_WEIL_POSITIVITY",
        "parameters": {
            "gaussian_a_exact": _as_string(DEFAULT_GAUSSIAN_A),
            "centers_exact": [_as_string(c) for c in centers],
            "cutoff": prime_cutoff,
            "max_center": _as_string(CENTER_UPPER),
            "bound_valid_for_all_larger_cutoffs": True,
        },
        "analytic_prime_tail": {
            "per_gram_entry_upper_rational": _as_string(per),
            "quadratic_form_norm_upper_rational": _as_string(global_norm),
            "meaning": "For any real vector x in the selected m-dimensional Gaussian span, |Q_full_prime(x)-Q_truncated_prime(x)| <= m*delta*||x||_2^2",
            "proof": "Gaussian Fourier envelope, Lambda(n)<=log(n), decreasing-tail integral, complete-the-square, exponential tangent inequality, Cauchy-Schwarz",
            "works_for_all_allowed_center_choices": True,
            "does_not_assume_rh": True,
            "zero_inputs_used": False,
            "all_prime_power_terms_above_cutoff_included_in_bound": True,
            "numeric_interval_roundoff_required_to_prove_the_rational_bound": False,
        },
        "other_unbounded_errors": [
            "finite digamma asymptotic/remainder in the archived Weil experiment",
            "finite Simpson quadrature of the archimedean integral",
            "rounding/representation errors of computed finite prime sums",
            "eigenvalue and matrix entry roundoff errors",
            "extension from one finite span to all Weil-admissible test functions",
        ],
        "positivity_contract": {
            "finite_matrix_psd_certified": False,
            "global_weil_psd_certified": False,
            "uniform_coercivity_constant_established": False,
            "hilbert_space_completed": False,
            "riemann_hypothesis_proved": False,
        },
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prime-cutoff", type=int, default=256)
    parser.add_argument("--centers", default="0,1/5,1/2")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        centers = tuple(Fraction(x) for x in args.centers.split(","))
        data = report(centers, args.prime_cutoff)
    except (ValueError, ZeroDivisionError) as exc:
        parser.error(str(exc))
    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
