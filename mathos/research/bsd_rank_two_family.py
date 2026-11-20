"""MathOS BSD milestone 01 exact Z[T] invariant audit (not BSD proof)."""
from __future__ import annotations
import json

def trim(v):
    v=list(v)
    while len(v)>1 and v[-1]==0: v.pop()
    return tuple(v)

def add(a,b):
    return trim(tuple((a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0)
                      for i in range(max(len(a),len(b)))))

def mul(a,b):
    v=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): v[i+j]+=x*y
    return trim(v)

def scale(a,n): return trim(tuple(n*x for x in a))
def neg(a): return scale(a,-1)

def powp(a,n):
    out=(1,)
    for _ in range(n): out=mul(out,a)
    return out

def evalp(a,t):
    n=0
    for x in reversed(a): n=n*t+x
    return n

def invariants():
    a2,a4=(1,1),(-2,-1)
    b2=scale(a2,4)
    b4=scale(a4,2)
    b6=(1,)
    b8=add(a2,neg(powp(a4,2)))
    c4=add(powp(b2,2),scale(b4,-24))
    delta=add(add(neg(mul(powp(b2,2),b8)),scale(powp(b4,3),-8)),
              add(scale(powp(b6,2),-27),scale(mul(mul(b2,b4),b6),9)))
    return c4,delta

def audit():
    c4,delta=invariants()
    assert c4==(112,80,16)
    assert delta==(389,696,472,144,16)
    assert evalp(delta,0)==389 and evalp(delta,2)==5077
    assert len(powp(c4,3))-1==6 and len(delta)-1==4
    for t in range(-25,26):
        for x,y in ((0,0),(1,0)):
            assert y*y+y==x**3+(1+t)*x*x-(2+t)*x
    for x in range(-25,26):
        X=x+1
        assert x**3+3*x*x-4*x == X**3-7*X+6
    return {
        "result":"EXACT_POLYNOMIAL_AUDIT_PASSED",
        "c4_coeffs_ascending":list(c4),
        "discriminant_coeffs_ascending":list(delta),
        "T0_LMFDB":"389.a1",
        "T2_LMFDB":"5077.a1",
        "rank_source_independently_verified_by_script":False,
        "specialization_theorem_proved_by_script":False,
        "analytic_rank_for_family_proved":False,
        "novelty_established":False,
        "BSD_proved":False
    }

if __name__=="__main__": print(json.dumps(audit(),indent=2,sort_keys=True))
