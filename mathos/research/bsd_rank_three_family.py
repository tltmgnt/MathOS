"""MathOS BSD milestone 03: exact polynomial and section audit.

Verifies identities for an explicit quadratic base change of an elliptic
family. Does NOT independently verify LMFDB ranks, Silverman's theorem,
analytic ranks, originality, or the Birch--Swinnerton--Dyer conjecture.
"""
from __future__ import annotations
import json


def trim(a):
    a = list(a)
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return tuple(a)


def add(a, b):
    return trim(tuple((a[i] if i < len(a) else 0) +
                      (b[i] if i < len(b) else 0)
                      for i in range(max(len(a), len(b)))))


def scale(a, c):
    return trim(tuple(c*x for x in a))


def mul(a, b):
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] += x * y
    return trim(result)


def power(a, n):
    if type(n) is not int or n < 0:
        raise ValueError('polynomial exponent must be a nonnegative integer')
    p = (1,)
    for _ in range(n):
        p = mul(p, a)
    return p


def evaluate(a, u):
    value = 0
    for coeff in reversed(a):
        value = value * u + coeff
    return value


def invariants():
    """Exact Z[U] formulas for c4 and discriminant."""
    u = (0, 1)
    s = add(power(u, 2), u)
    c4 = scale(mul(add(power(u, 2), (3,)),
                   add(add(power(u, 2), scale(u, 2)), (4,))), 4)
    delta = add(add(power(s, 4), scale(power(s, 3), 10)),
                add(add(scale(power(s, 2), 34), scale(s, 60)), (37,)))
    return c4, delta


def section_identity_twice(x, y):
    """2(y²+y) - [2x³ + Sx² -(S+2)x] in Z[U], S=U²+U."""
    u = (0, 1)
    s = add(power(u, 2), u)
    lhs = scale(add(power(y, 2), y), 2)
    rhs = add(add(scale(power(x, 3), 2), mul(s, power(x, 2))),
              scale(mul(add(s, (2,)), x), -1))
    return add(lhs, scale(rhs, -1))


def audit():
    u = (0, 1)
    c4, delta = invariants()
    assert c4 == (48, 24, 28, 8, 4)
    assert delta == (37, 60, 94, 78, 65, 34, 16, 4, 1)

    # Positive polynomial identity proves Δ(U)>0 for every real U.
    # 256Δ=(2U+1)^8 + 36(2U+1)^6 + 430(2U+1)^4
    #                       + 2868(2U+1)^2 + 6137.
    z = add(scale(u, 2), (1,))
    sos = add(add(power(z, 8), scale(power(z, 6), 36)),
              add(add(scale(power(z, 4), 430), scale(power(z, 2), 2868)),
                  (6137,)))
    assert scale(delta, 256) == sos

    sections = {'P': ((0,), (0,)), 'Q': ((1,), (0,)), 'R': ((-1,), u)}
    for name, (x, y) in sections.items():
        assert section_identity_twice(x, y) == (0,), name

    def t_num(parameter):
        return parameter*parameter + parameter - 2

    assert {n: t_num(n)//2 for n in (2, -3, 1, -2)} == {
        2: 2, -3: 2, 1: 0, -2: 0
    }
    assert evaluate(delta, 2) == 5077
    assert evaluate(delta, -3) == 5077
    assert evaluate(delta, 1) == 389
    assert evaluate(delta, -2) == 389

    # At U=2: y²+y=x³+3x²−4x; X=x+1 gives X³−7X+6.
    for x in range(-30, 31):
        X = x + 1
        assert x**3 + 3*x*x - 4*x == X**3 - 7*X + 6
    assert [(0+1, 0), (1+1, 0), (-1+1, 2)] == [
        (1, 0), (2, 0), (0, 2)
    ]

    for n in range(-40, 41):
        assert evaluate(delta, n) > 0
        assert n * (n+1) % 2 == 0

    return {
        'milestone': 'MATHOS-BSD-RANK-THREE-BASE-CHANGE-03',
        'status': 'EXACT_POLYNOMIAL_AND_SECTION_AUDIT',
        'quadratic_base_change': 'T=(U^2+U-2)/2',
        'c4_coefficients_ascending': list(c4),
        'delta_coefficients_ascending': list(delta),
        'three_sections_verified_as_polynomial_identities': True,
        'discriminant_positive_identity_verified': True,
        'U2_LMFDB': '5077.a1',
        'known_exceptional_parameters_from_rank_drop': [1, -2],
        'rank_three_generators_independently_proved_by_script': False,
        'Silverman_specialization_theorem_proved_by_script': False,
        'analytic_L_values_calculated': False,
        'effective_exceptional_set_computed': False,
        'exact_generic_rank_proved': False,
        'analytic_rank_exact_equality_for_infinite_family_proved': False,
        'mathematical_novelty_established': False,
        'BSD_proved': False,
    }


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2, sort_keys=True))
