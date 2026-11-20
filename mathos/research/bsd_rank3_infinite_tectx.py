"""MathOS BSD 06: scoped arithmetic checks for Zywina's *different* rank-3 family.

An external 2026 preprint (arXiv:2602.10865, Theorem 4.1 and §6.4)
proves infinitely many rank-three specializations for its specific 2-isogeny
family. This script checks rational polynomial identities, displayed points,
and lower-bound squareclass evidence for a *single* rational parameter.

DOES NOT compute isogeny Selmer upper bounds, certify any fiber's exact
rank 3, enumerate infinitely many rank-3 parameters, apply the published
theorem to MathOS's E_U family, establish mathematical novelty, or solve BSD.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as Q
from math import isqrt


def trim(poly):
    v = list(poly)
    while len(v) > 1 and v[-1] == 0:
        v.pop()
    return tuple(v)


def add(left, right):
    return trim(tuple(
        (left[i] if i < len(left) else Q(0)) +
        (right[i] if i < len(right) else Q(0))
        for i in range(max(len(left), len(right)))
    ))


def scalar(poly, c):
    return trim(tuple(Q(c) * x for x in poly))


def mul(left, right):
    v = [Q(0)] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            v[i+j] += x*y
    return trim(v)


def power(poly, n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative integral polynomial power required")
    result = (Q(1),)
    for _ in range(n):
        result = mul(result, poly)
    return result


def evaluate(poly, x):
    result = Q(0)
    for c in reversed(poly):
        result = result*Q(x)+c
    return result


def model():
    t = (Q(0), Q(1))
    t2 = power(t, 2)
    p4 = add(t2, (Q(-4),))
    p121 = add(t2, (Q(-121),))
    a = (Q(9725), Q(0), Q(-98))
    b = scalar(mul(p4, p121), 7**4)
    a_iso = scalar(a, -2)
    b_iso = add(power(a, 2), scalar(b, -4))
    return t, a, b, a_iso, b_iso, p4, p121


def equation_difference(x, y, a, b):
    """Return y² - x³ - a*x² - b*x in Q[T]."""
    return add(add(power(y, 2), scalar(power(x, 3), -1)),
               add(scalar(mul(a, power(x, 2)), -1),
                   scalar(mul(b, x), -1)))


def exact_source_identities():
    t, a, b, ap, bp, p4, p121 = model()
    t_minus2 = (Q(-2), Q(1))
    t_plus11 = (Q(11), Q(1))
    p0 = ((Q(0),), (Q(0),))
    p1 = (scalar(p4, 7**4), scalar(mul(t, p4), 115248))
    p2 = (scalar(mul(t_minus2, t_plus11), 7**2),
          scalar(mul(t_minus2, t_plus11), 4263))
    q0 = p0
    q1 = (add(scalar(t, 630), (Q(28449,4),)),
          add(add(scalar(power(t, 2), 8820), scalar(t, Q(177093,2))),
              (Q(-995715,8),)))

    expected_bp = scalar(mul((Q(-3161), Q(280)),
                             (Q(3161), Q(280))), -9)
    assert bp == expected_bp, (bp, expected_bp)
    for label, (x, y) in (("P0",p0),("P1",p1),("P2",p2)):
        assert equation_difference(x, y, a, b) == (Q(0),), label
    for label, (x, y) in (("Q0",q0),("Q1",q1)):
        assert equation_difference(x, y, ap, bp) == (Q(0),), label

    delta = scalar(mul(power(b, 2), bp), 16)
    factor = add(power(t, 2), (Q(-3161**2, 280**2),))
    expected_delta = scalar(
        mul(mul(power(p4, 2), power(p121, 2)), factor),
        -(2**10)*(3**2)*(5**2)*(7**10),
    )
    assert delta == expected_delta
    assert len(delta)-1 == 10
    bad = [Q(-11), Q(-2), Q(2), Q(11), Q(-3161,280), Q(3161,280)]
    for z in bad:
        assert evaluate(delta, z) == 0

    # MathOS E_U at U=2: no rational 2-torsion because completed-square
    # cubic 4x³+12x²-16x+1 has no rational root, by rational root theorem.
    candidates = [Q(n,d) for n in (-1,1) for d in (1,2,4)]
    assert all(4*z**3+12*z**2-16*z+1 != 0 for z in candidates)

    return {
        "model_polynomial_identity":True,
        "dual_isogeny_coefficients_identity":True,
        "source_discriminant_factorization_identity":True,
        "five_published_point_equations":True,
        "original_mathos_u2_has_no_rational_two_torsion":True,
        "source_singular_rational_parameters":
            [str(z) for z in sorted(bad)],
        "source_model_discriminant_degree":len(delta)-1,
    }


def prime_parity(n):
    """Odd-valuation rational prime factors of a nonzero integer, trial division."""
    if type(n) is not int or n == 0:
        raise ValueError("nonzero integer expected")
    res = set()
    if n < 0:
        res.add(-1)
    n = abs(n)
    p = 2
    while p*p <= n:
        k = 0
        while n % p == 0:
            n //= p
            k ^= 1
        if k:
            res.add(p)
        p = 3 if p == 2 else p+2
    if n > 1:
        res.add(n)
    return res


def rational_squareclass(value):
    """Squareclass in Q*/Q*², represented by parity of signed prime valuations."""
    value = Q(value)
    if value == 0:
        raise ValueError("squareclass of zero is undefined")
    return prime_parity(value.numerator) ^ prime_parity(value.denominator)


def span_rank(classes):
    primes = sorted(set().union(*classes))
    slots = {p:i for i,p in enumerate(primes)}
    pivots = {}
    for cls in classes:
        mask = 0
        for p in cls:
            mask ^= 1 << slots[p]
        while mask:
            top = mask.bit_length()-1
            if top in pivots:
                mask ^= pivots[top]
            else:
                pivots[top] = mask
                break
    return len(pivots)


def source_squareclass_dimensions(t):
    """Check five *exhibited point* images, not any Selmer upper bound."""
    t = Q(t)
    excluded = {Q(-11),Q(-2),Q(2),Q(11),Q(-3161,280),Q(3161,280)}
    if t in excluded:
        raise ValueError("source family is singular at this parameter")
    source_3 = [
        (t*t-4)*(t*t-121),
        (t*t-4),
        (t-2)*(t+11),
    ]
    source_2 = [
        -9*(280*t-3161)*(280*t+3161),
        9*(280*t+3161),
    ]
    a = span_rank([rational_squareclass(c) for c in source_3])
    b = span_rank([rational_squareclass(c) for c in source_2])
    return {
        "t":str(t),
        "source_E_classes":[str(x) for x in source_3],
        "source_Eprime_classes":[str(x) for x in source_2],
        "independent_source_E_images":a,
        "independent_source_Eprime_images":b,
        "two_isogeny_descent_rank_lower_bound":a+b-2,
        "Selmer_phi_dimension_computed":False,
        "Selmer_dual_dimension_computed":False,
        "exact_rank_three_certified_by_this_program":False,
    }


def audit(t=Q(3)):
    identities = exact_source_identities()
    classes = source_squareclass_dimensions(t)
    return {
        "program":"ResearchOS TECT X / MathOS BSD 06",
        "comparison_source":"Zywina arXiv:2602.10865, Thm 4.1 and Section 6.4",
        "source_proves_infinite_rank_three_for_ITS_FAMILY":True,
        "source_family_is_original_MathOS_family":False,
        "source_theorem_independently_reproved_by_this_program":False,
        "infinite_parameter_set_enumerated_by_this_program":False,
        "MathOS_family_infinite_exact_rank_three_proved":False,
        "exact_analytic_rank_three_infinite_proved":False,
        "independent_novelty_review_completed":False,
        "canonical_TECT_runtime_executed":False,
        "canonical_assurance_state":"UNVERIFIED",
        "BSD_proved":False,
        **identities,
        "finite_parameter_evidence":classes,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--numerator",type=int,default=3)
    parser.add_argument("--denominator",type=int,default=1)
    args = parser.parse_args()
    if args.denominator == 0:
        parser.error("denominator must be nonzero")
    print(json.dumps(audit(Q(args.numerator,args.denominator)),
                     sort_keys=True,indent=2))
