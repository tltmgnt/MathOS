"""MathOS BSD 07: exact arithmetic for a cubic-field 2-descent bound.

For u=24*k, verifies polynomial identities, congruence conditions, and a
large parameter-dependent rank upper bound using established descent and
Minkowski theorems. It does NOT compute a Selmer group, a cubic class
group, a uniform rank-three bound, mathematical novelty, or BSD.
"""
from __future__ import annotations
import argparse
import json
from math import isqrt


def trim(coeffs):
    q = list(coeffs)
    while len(q) > 1 and q[-1] == 0:
        q.pop()
    return tuple(q)


def add(a, b):
    return trim([(a[i] if i < len(a) else 0) +
                 (b[i] if i < len(b) else 0)
                 for i in range(max(len(a), len(b)))])


def multiply(a, b):
    v = [0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            v[i+j] += x*y
    return trim(v)


def scale(a, n):
    return trim([n*x for x in a])


def power(a, n):
    if type(n) is not int or n < 0:
        raise ValueError('nonnegative integer exponent')
    ans = (1,)
    for _ in range(n):
        ans = multiply(ans, a)
    return ans


def cubic_discriminant_in_s():
    """In Z[s], discriminant of X^3 + 2s X^2 - 8(s+2)X + 16."""
    a = (0,2)
    b = (-16,-8)
    c = (16,)
    return add(add(multiply(power(a,2), power(b,2)),
                   scale(power(b,3),-4)),
               add(add(scale(multiply(power(a,3),c),-4),
                       scale(power(c,2),-27)),
                   scale(multiply(multiply(a,b),c),18)))


def D(u):
    if type(u) is not int:
        raise TypeError('integer u required')
    s = u*(u+1)
    return s**4 + 10*s**3 + 34*s**2 + 60*s + 37


def cubic_coeffs(u):
    s = u*(u+1)
    return (16, -8*(s+2), 2*s, 1)


def cubic_at_mod(f, x, p):
    value = 0
    for c in reversed(f):
        value = (value*x+c)%p
    return value


def omega_exact(n):
    """Distinct rational prime factors, using exact division, not a primality oracle."""
    if type(n) is not int or n < 1:
        raise ValueError('positive integer required')
    num = 0
    if n%2 == 0:
        num += 1
        while n%2 == 0:
            n //= 2
    p = 3
    while p*p <= n:
        if n%p == 0:
            num += 1
            while n%p == 0:
                n //= p
        p += 2
    if n > 1:
        num += 1
    return num


def minkowski_ceiling_from_D(d):
    """Exact ceil(32 sqrt(d)/9), avoiding floating-point arithmetic."""
    if type(d) is not int or d < 1:
        raise ValueError('positive integer required')
    target = 1024*d
    candidate = (isqrt(target)+8)//9
    while 81*candidate*candidate < target:
        candidate += 1
    while candidate > 1 and 81*(candidate-1)*(candidate-1) >= target:
        candidate -= 1
    return candidate


def rank_bound(u):
    if type(u) is not int or u%24 != 0:
        raise ValueError('proven congruence class requires u divisible by 24')
    s = u*(u+1)
    d = D(u)
    assert d%8 == 5 and d%3 == 1
    f = cubic_coeffs(u)
    assert all(cubic_at_mod(f,x,3) != 0 for x in (0,1,2))
    # 256D = discriminant of the integral monic 2-division cubic, symbolically.
    assert cubic_discriminant_in_s() == (
        256*37, 256*60, 256*34, 256*10, 256
    )
    assert d > 0
    distinct = omega_exact(d)
    n = minkowski_ceiling_from_D(d)
    ceil_log_2_n = (n-1).bit_length()
    # Standard Kummer bound: rank <= 2+|Sigma_K|+dim Cl(O_K,Sigma)[2].
    # <= 5+3omega(D)+dim Cl(O_K)[2], by |Sigma_K|<=3(1+omega(D)).
    # Minkowski: h_K<=N^3, so dim Cl(O_K)[2]<=3 ceil(log2 N).
    explicit_upper = 5 + 3*distinct + 3*ceil_log_2_n
    return {
      'u':u, 'S':s, 'D':d,
      'monic_two_division_cubic_coefficients_ascending':list(f),
      'cubic_discriminant':256*d,
      'cubic_irreducible_mod3':True,
      'cubic_galois_group':'S3 (discriminant nonsquare mod 8)',
      'cubic_signature':'(3,0) totally real',
      'distinct_prime_factors_of_D':distinct,
      'minkowski_N_upper':n, 'ceil_log2_N':ceil_log_2_n,
      'rank_bound_minkowski_proved_using_external_descent_theorems':explicit_upper,
      'rank_bound_requires_class_group_computation':False,
      'sharper_bound_symbolic':'rank <= 2 + |Sigma_K| + dim_F2 Cl(O_K,Sigma_K)[2]',
      'sharp_selmer_dimension_computed':False,
      'rank_3_for_this_fiber_certified':False,
      'uniform_rank_3_over_infinite_set_proved':False,
      'bounded_constant_upper_rank_for_infinite_set_proved':False,
      'generic_rank_3_from_previous_milestone_is_not_specialized_rank_3':True,
      'originality_established':False, 'BSD_proved':False,
    }


def audit(k=0):
    if type(k) is not int or abs(k) > 1000:
        raise ValueError('demo requires |k|<=1000; theorem has no such size restriction')
    return {
      'milestone':'MATHOS-BSD-07-CUBIC-DESCENT-BOUND',
      'infinite_parameter_set':'u=24*k for all k in Z',
      'what_is_proved':'Unconditional parameter-dependent 2-descent upper bound for u=24*k',
      'theorem_valid_for_all_k':True,
      'automatic_verification_only_exact_arithmetic':True,
      'external_cubic_descent_theorem_reproved_in_program':False,
      'external_specialization_theorem_reproved_in_program':False,
      'canonical_researchos_controller_executed':False,
      'canonical_TECT_state':'UNVERIFIED',
      'uniform_rank_3_proved':False,
      'originality_established':False, 'BSD_proved':False,
      'parameter_audit':rank_bound(24*k),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--k', type=int, default=0)
    opts = parser.parse_args()
    print(json.dumps(audit(opts.k),indent=2,sort_keys=True))
