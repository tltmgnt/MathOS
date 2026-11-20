"""MathOS BSD milestone 04: exact finite prime-discriminant/sign audit.

Uses exact integer arithmetic and standard external reduction/root-number
formula. LMFDB rank records are external; no analytic order, BSD equality,
novelty, or infinitude of prime values is established.
"""
from __future__ import annotations
import argparse
import json
from math import isqrt

LMFDB_RECORDED = {
    0: {"label": "37.a1", "rank": 1, "analytic_rank": 1},
    2: {"label": "389.a1", "rank": 2, "analytic_rank": 2},
    6: {"label": "5077.a1", "rank": 3, "analytic_rank": 3},
    12: {"label": "43669.a1", "rank": 3, "analytic_rank": 3},
}


def is_prime_trial_division(n: int) -> bool:
    if type(n) is not int:
        raise TypeError("integer primality input required")
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for d in range(3, isqrt(n) + 1, 2):
        if n % d == 0:
            return False
    return True


def elliptic_invariants(u: int) -> dict:
    if type(u) is not int:
        raise TypeError("integer parameter required")
    s = u * (u + 1)
    a2 = s // 2
    a4 = -(s + 2) // 2
    c4 = 4 * (u*u+3) * (u*u+2*u+4)
    c6 = -8*s**3 - 72*s*s - 144*s - 216
    delta = (u**8 + 4*u**7 + 16*u**6 + 34*u**5 + 65*u**4
             + 78*u**3 + 94*u*u + 60*u + 37)
    assert s % 2 == 0
    assert c4**3 - c6**2 == 1728 * delta
    assert delta > 0
    return {"u":u, "s":s, "a2":a2, "a4":a4, "c4":c4, "c6":c6,
            "delta":delta}


def legendre_at_prime(a: int, p: int) -> int:
    if p < 3 or not is_prime_trial_division(p):
        raise ValueError("odd prime required")
    r = pow(a % p, (p-1)//2, p)
    return 1 if r == 1 else (-1 if r == p-1 else 0)


def root_number_certificate(u: int) -> dict:
    d = elliptic_invariants(u)
    p = d["delta"]
    prime = is_prime_trial_division(p)
    result = {
        "u":u, "S":d["s"], "ainvs":[0,d["a2"],1,d["a4"],0],
        "c4":d["c4"], "c6":d["c6"], "discriminant":p,
        "discriminant_prime_by_exact_trial_division":prime,
        "root_number":None,
        "root_number_theorem_input":"standard multiplicative reduction local signs",
        "source_rank_record":LMFDB_RECORDED.get(d["s"]),
        "independent_rank_certificate_produced":False,
        "exact_analytic_rank_proved":False,
        "analytic_L_derivative_evaluated":False,
        "BSD_proved":False,
    }
    if not prime or p < 5:
        return result
    if d["c4"] % p == 0:
        raise AssertionError("c4 must be a p-unit for prime discriminant")
    sign = legendre_at_prime(-d["c6"], p)
    if sign == 0:
        raise AssertionError("c6 must be nonzero modulo p")
    # Good reduction outside p, type I1 at p and w_infinity=-1.
    # Split iff Legendre(-c6,p)=+1; global w=Legendre(-c6,p).
    result.update({
        "split_multiplicative":sign == 1,
        "global_root_number_from_exact_prime_discriminant_certificate":sign,
        "root_number":sign,
        "Euler_criterion_residue":pow((-d["c6"])%p,(p-1)//2,p),
        "reduction_type_at_p":"I_1",
        "conductor_from_semistable_prime_discriminant":p,
    })
    return result


def audit(start: int=-8, end: int=7) -> dict:
    if type(start) is not int or type(end) is not int:
        raise TypeError("integer bounds required")
    if start > end or max(abs(start),abs(end)) > 12:
        raise ValueError("bounds must satisfy start<=end and abs(u)<=12")
    all_cases=[root_number_certificate(u) for u in range(start,end+1)]
    selected=[x for x in all_cases if x["discriminant_prime_by_exact_trial_division"]]
    for case in all_cases:
        mirror=elliptic_invariants(-case["u"]-1)
        assert mirror["delta"] == case["discriminant"]
        assert mirror["c4"] == case["c4"]
        assert mirror["c6"] == case["c6"]
    return {
        "milestone":"MathOS-BSD-04",
        "result":"FINITE_EXACT_ROOT_NUMBER_CERTIFICATES",
        "parameter_interval":[start,end],
        "prime_discriminant_cases":selected,
        "prime_discriminant_case_count":len(selected),
        "non_prime_discriminant_root_numbers_computed":False,
        "all_fibers_analytic_rank_three_proved":False,
        "infinite_prime_discriminant_subfamily_proved":False,
        "infinite_exact_rank_equality_proved":False,
        "mathematical_novelty_established":False,
        "BSD_proved":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--start",type=int,default=-8)
    p.add_argument("--end",type=int,default=7)
    a=p.parse_args()
    print(json.dumps(audit(a.start,a.end),indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
