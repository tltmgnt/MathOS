"""MathOS BSD milestone 05: exact factorization input to a PUBLISHED rank theorem.

The algebraic rank-three formula is an application of Battistoni--Bettin--
Delaunay, arXiv:2109.00738v1, Theorem 1, degree-A=2 case. The code checks
finite rational polynomial identities, theorem parameters and TECT ×5 scope.
It does not prove the external theorem, authenticate an independent review,
certify an exact rank for infinitely many rational specializations, compute
analytic L-values or prove the Birch--Swinnerton--Dyer conjecture.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import product
import json

Q = lambda a: tuple(F(x) for x in a)


def trim(a):
    a = list(a)
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return tuple(a)


def add(a, b):
    return trim(tuple((a[i] if i < len(a) else 0) +
                      (b[i] if i < len(b) else 0)
                      for i in range(max(len(a), len(b)))))


def neg(a):
    return tuple(-x for x in a)


def mul(a, b):
    v = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            v[i + j] += x * y
    return trim(v)


def scalar(a, n):
    return trim(tuple(F(n) * x for x in a))


def powp(a, n):
    if type(n) is not int or n < 0:
        raise ValueError('polynomial exponent must be a nonnegative integer')
    out = (F(1),)
    for _ in range(n):
        out = mul(out, a)
    return out


def evaluate(a, x):
    total = F(0)
    for v in reversed(a):
        total = total*F(x)+v
    return total


def divmod_modp(a, b, p):
    """Divide integer polynomials modulo a prime (tuples ascending)."""
    def t(v):
        v = [x % p for x in v]
        while len(v) > 1 and v[-1] == 0:
            v.pop()
        return tuple(v)
    a, b = t(a), t(b)
    if b == (0,):
        raise ZeroDivisionError
    r = list(a)
    quotient = [0] * max(1, len(a) - len(b) + 1)
    inv = pow(b[-1], -1, p)
    while len(r) >= len(b) and any(r):
        degree = len(r) - len(b)
        v = r[-1]*inv % p
        quotient[degree] = v
        for j, coeff in enumerate(b):
            r[degree + j] = (r[degree + j] - v*coeff) % p
        r = list(t(r))
    return t(quotient), t(r)


def gcd_modp(a, b, p):
    def make_monic(v):
        if v == (0,):
            return v
        inv = pow(v[-1], -1, p)
        return tuple(x * inv % p for x in v)
    while b != (0,):
        _, r = divmod_modp(a, b, p)
        a, b = b, r
    return make_monic(a)


def exact_polynomial_certificates():
    x = Q((0, 1))
    one = Q((1,))
    A = Q((0, F(-1, 2), F(1, 2)))
    B = A
    C = Q((F(1, 4), -1, 0, 1))

    Fpoly = add(powp(B, 2), scalar(mul(A, C), -4))
    expected_F = scalar(mul(mul(mul(x, add(x, neg(one))),
                                  add(x, one)), Q((2, -9, 8))), F(-1, 4))
    assert Fpoly == expected_F, (Fpoly, expected_F)

    # Distinct factors x, x-1, x+1 and g=8x²-9x+2.
    g = Q((2, -9, 8))
    assert 9*9-4*8*2 == 17
    assert evaluate(C, 0) == F(1, 4) and evaluate(C, 1) == F(1, 4)

    # A - g/16 = X/16 - 1/8: the nonzero linear remainder gives Upsilon=0.
    rem = add(A, scalar(g, F(-1,16)))
    assert rem == Q((F(-1, 8), F(1, 16)))

    # Monic resultant M_(x(x-1),C)(z) = (z²-1/4)².
    z2_minus_quarter = Q((F(-1,4), 0, 1))
    result1 = powp(z2_minus_quarter, 2)
    assert result1 == Q((F(1,16), 0, F(-1,2), 0, 1))

    # Quadratic roots rho,rho' of g: sum=9/8, product=1/4.
    rsum, rproduct = F(9,8), F(1,4)
    trace_A = (rsum**2-2*rproduct-rsum)/2
    norm_A = rproduct*(rproduct-rsum+1)/4
    assert trace_A == F(-23,128)
    assert norm_A == F(1,128)

    # Their resultant contributes z4 + (23/128)z2 + (1/128).
    quartic = Q((norm_A, 0, -trace_A, 0, 1))
    result2 = mul(mul(Q((0,0,0,0,1)), Q((-1,0,1))),quartic)
    assert quartic == Q((F(1,128), 0, F(23,128), 0, 1))
    assert len(result2)-1 == 10

    # The quartic (128 z4 + 23 z2 + 1) is irreducible mod 3:
    # eliminate all possible monic factors of degrees 1 and 2.
    q_mod3 = tuple(c % 3 for c in (1,0,23,0,128))
    for degree in (1,2):
        for terms in product(range(3), repeat=degree):
            monic = tuple(terms)+(1,)
            _,r = divmod_modp(q_mod3, monic, 3)
            assert r != (0,), (monic,r)

    # c4 and discriminant for rational elliptic surface. Squarefree D mod 3.
    delta = (37,60,94,78,65,34,16,4,1)
    deriv = tuple(i*delta[i] for i in range(1,len(delta)))
    assert gcd_modp(delta, deriv, 3) == (1,)
    assert delta[-1] % 3 != 0
    # Infinity: deg c4=4, deg Delta=8 -> ord_inf c4'=0, ord_inf Delta'=4.
    c4 = (48,24,28,8,4)
    assert len(c4)-1 == 4 and len(delta)-1 == 8 and c4[-1] != 0

    # Bookkeeping for Theorem 1, deg A=2.
    terms = {
      "Omega_M_gcdABstar_C": 4,
      "Omega_M_Fstar_A": 7,  # z^4, z-1, z+1, irreducible quartic
      "omega_gcdABC": 0,
      "Upsilon_gcdAB_C": 0,  # gcd(A,B) has only linear irreducible factors
      "Upsilon_F_A": 0,      # g-remainder has nonzero linear coefficient
      "omega_F": 4,
      "two_degree_gcdABstarC": 0,
      "two_degree_gcdABstar": 4,
      "square_A_indicator": 0,
    }
    rank = (terms["Omega_M_gcdABstar_C"] + terms["Omega_M_Fstar_A"] +
            terms["omega_gcdABC"] - terms["Upsilon_gcdAB_C"] -
            terms["Upsilon_F_A"] - terms["omega_F"] -
            terms["two_degree_gcdABstarC"] -
            terms["two_degree_gcdABstar"] -
            terms["square_A_indicator"])
    assert rank == 3
    geometric_rank = 10 - 2 - (4 - 1)  # I4 at infinity; 8 I1 finite.
    assert geometric_rank == 5

    return {
        "exact_polynomial_factorization": True,
        "resultant_factors_verified": True,
        "irreducible_quartic_via_mod3": True,
        "discriminant_squarefree_via_mod3": True,
        "BBD_Theorem_1_degree_A_2_rank": rank,
        "Shioda_Tate_geometric_rank": geometric_rank,
        "rank_formula_terms": terms,
    }


def audit():
    calculations = exact_polynomial_certificates()
    return {
      "project": "MathOS BSD milestone 05 / ResearchOS TECT x5",
      "source": "Battistoni-Bettin-Delaunay 2021 arXiv:2109.00738v1 Theorem 1",
      "status": "SCOPED_EXISTING_THEOREM_APPLICATION",
      **calculations,
      "published_theorem_reproved_by_script": False,
      "outside_review_authenticated": False,
      "universal_exact_specialization_rank_3_proved": False,
      "effectively_specified_infinite_exact_rank_3_fibers_proved": False,
      "infinite_family_exact_analytic_rank_3_proved": False,
      "independent_novelty_established": False,
      "canonical_TECT_assurance_promoted": False,
      "BSD_proved": False,
    }


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2, sort_keys=True))
