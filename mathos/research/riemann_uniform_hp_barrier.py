"""TECT-X: uniform first-zero obstruction for bounded self-adjoint perturbations.

H0 is a known-density diagonal operator with eigenvalues a_n=F^{-1}(n).
For *every* bounded self-adjoint B of norm <= 14/5, H0+B has no spectrum
below the first nontrivial zeta zero ordinate. This excludes the proposed
global Hilbert--Polya divisor identity for an entire class of operators.

Does not construct a Hilbert--Polya operator, prove RH, or independently
verify the externally tabulated first zeta zero.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from mathos.research.riemann_arithmetic_spectral import inverse_main_term, main_term

# Conservative strict rational bounds; π>3.14 and e>2.71 are classical.
PI_LOWER = Fraction(157, 50)
E_LOWER = Fraction(271, 100)
# External established zero ordinate bound; not computed or proved here.
FIRST_ZERO_UPPER = Fraction(707, 50)  # 14.14
BUDGET = Fraction(14, 5)  # 2.8


def _frac(q: Fraction) -> str:
    return str(q.numerator) + "/" + str(q.denominator)


def lower_spectral_margin(norm_budget: Fraction) -> Fraction:
    """Strict lower margin based on rational π, e, and first-zero bounds."""
    if not isinstance(norm_budget, Fraction) or norm_budget < 0:
        raise ValueError("a nonnegative rational norm bound is required")
    # a1 > 2*pi*e, so inf(H0+B) > 2*pi_lower*e_lower - norm_budget.
    return 2 * PI_LOWER * E_LOWER - norm_budget - FIRST_ZERO_UPPER


def audit(norm_budget: Fraction = BUDGET, sample_size: int = 128) -> dict:
    if type(sample_size) is not int or not 16 <= sample_size <= 4096:
        raise ValueError("sample_size must be an integer in 16..4096")
    margin = lower_spectral_margin(norm_budget)
    if margin <= 0:
        raise ValueError("the conservative analytic barrier does not apply at this budget")
    initial = inverse_main_term(1)
    last = inverse_main_term(sample_size)
    if not (initial < last and main_term(last) > sample_size-1e-9):
        raise AssertionError("diagonal-counting regression failed")
    return {
        "schema": "mathos_tectx_uniform_hp_perturbation_barrier/1",
        "status": "UNIFORM_BOUNDED_PERTURBATION_FAMILY_REFUTED_AS_HILBERT_POLYA",
        "candidate_family": {
            "space": "ell2(N>=1)",
            "H0": "H0 e_n=a_n e_n, F(a_n)=n, F(T)=T/(2*pi)*(log(T/(2*pi))-1), a_n>2*pi*e",
            "B": "every bounded self-adjoint operator B with ||B|| <= chosen norm_budget, including arbitrary nonlocal arithmetic couplings",
            "H": "H0+B on the maximal diagonal domain of H0",
            "self_adjointness": "bounded self-adjoint perturbation of a self-adjoint operator",
            "compact_resolvent": True,
            "spectral_count": "N_H(T)=F(T)+O(log T) via min-max with any fixed norm bound",
            "no_zero_inputs_in_operator": True,
            "universality": "all B satisfying a single operator-norm inequality, not only Jacobi or finite-rank perturbations",
        },
        "strict_certified_rational_inputs": {
            "pi_lower": _frac(PI_LOWER),
            "e_lower": _frac(E_LOWER),
            "first_nontrivial_zero_ordinate_upper_external": _frac(FIRST_ZERO_UPPER),
            "norm_budget": _frac(norm_budget),
            "margin_strictly_greater_than": _frac(margin),
            "note": "π and e bounds elementary; existence and ordinate bound of first zero are external mathematical knowledge",
        },
        "obstruction": {
            "theorem": "inf spectrum(H0+B) >= a1-||B|| > 2*pi_lower*e_lower - norm_budget > gamma1",
            "determinant": "D_H(z)=det(I-z^2*H^-2) is entire; all zeros are real +/- eigenvalues of H",
            "zero_free_factor_identity": "xi(1/2+i*z)=E(z)*D_H(z) with E entire nowhere-zero",
            "zero_free_factor_identity_possible": False,
            "reason": "D_H(gamma1) != 0 but xi(1/2+i*gamma1)=0",
            "does_not_exclude": [
                "unbounded perturbations with controlled self-adjoint domains",
                "bounded perturbations whose norm exceeds this conservative threshold",
                "operators not based on the artificially engineered main-term diagonal",
                "a different global spectral mechanism for a genuinely arithmetic operator",
            ],
        },
        "finite_regression": {
            "sample_size": sample_size,
            "first_diagonal_approx": initial,
            "last_diagonal_approx": last,
            "finite_numbers_do_not_prove_global_result": True,
        },
        "still_required": [
            "new independently specified fixed arithmetic operator not excluded by the spectral obstruction",
            "prove a global trace identity including complete prime-power and archimedean data from operator dynamics",
            "noncircular all-zero divisor identity with analytic multiplicities, including hypothetical off-line zeros",
            "self-adjointness combined with the proved divisor mapping, not merely real-valued fitted eigenvalues",
            "independent verification and complete formalization of any actually new theorem",
        ],
        "assurance": {
            "riemann_hypothesis_proved": False,
            "global_zero_correspondence": False,
            "new_mathematical_breakthrough_claimed": False,
            "external_review_completed": False,
        },
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget-numerator", type=int, default=14)
    parser.add_argument("--budget-denominator", type=int, default=5)
    parser.add_argument("--sample-size", type=int, default=128)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = audit(Fraction(args.budget_numerator, args.budget_denominator), args.sample_size)
    except (ValueError, ZeroDivisionError) as exc:
        parser.error(str(exc))
    payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
