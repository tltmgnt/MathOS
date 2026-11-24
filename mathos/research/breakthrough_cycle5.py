"""Cycle 5: mixed parity projection and CM rank-two localization audit."""
from itertools import product
from fractions import Fraction as F
import json
from mathos.research.breakthrough_focus import build_queue, intake, load
from mathos.research.breakthrough_cycle4 import count, bsd as prior_bsd


def pnp():
    rows=[]
    for n in range(2,8):
        # Pair states 0=00, 1=01, 2=10, 3=11.
        # A maximal forbidden cube fixes 11 on an odd subset of pairs
        # and chooses one zero on every remaining pair.
        hits={}
        cubes=0
        for types in product((0,1,2),repeat=n):
            if types.count(0)%2!=1:continue
            choices=[(3,) if t==0 else (0,1) if t==1 else (0,2) for t in types]
            witness=tuple(3 if t==0 else t for t in types)
            cubes+=1
            for x in product(*choices):hits[x]=hits.get(x,0)+1
            assert witness in hits
        odd={x for x in product(range(4),repeat=n) if x.count(3)%2}
        assert set(hits)==odd
        essential=sum(v==1 for v in hits.values())
        assert essential==cubes==(3**n-1)//2
        # All zero and each coordinate unit are accepted, hence affine hull full.
        assert (0,)*n not in odd
        for i in range(n):
            for bit in (1,2):
                v=[0]*n;v[i]=bit;assert tuple(v) not in odd
        rows.append(dict(n=n,visible_bits=2*n,input_and_clauses=3*n,
                         input_xor_rows=1,minimum_projected_clauses=cubes,
                         unique_witnesses=essential,forbidden_assignments=len(odd)))
    return dict(cases=rows,affine_hull="full",general_sat_lower_bound_proved=False)


def add(P,Q):
    if P is None:return Q
    if Q is None:return P
    x,y=P;z,w=Q
    if x==z and y==-w:return None
    m=(3*x*x-1681)/(2*y) if P==Q else (w-y)/(z-x)
    X=m*m-x-z;Y=m*(x-X)-y
    assert Y*Y==X**3-1681*X
    return X,Y


def mul(k,P):
    R=None
    while k:
        if k&1:R=add(R,P)
        k//=2
        if k:P=add(P,P)
    return R


def valuation(n,p):
    assert n!=0
    n=abs(n);v=0
    while n%p==0:n//=p;v+=1
    return v


def local_parameter(P,p,N):
    R=mul(N,P);assert R is not None
    x,y=R;z=-x/y
    v=valuation(z.numerator,p)-valuation(z.denominator,p)
    assert v>=1
    # t/p mod p is the first formal-log digit: log(t)=t+O(t^2)
    # with integral coefficients in degrees <p, and higher degrees
    # cannot affect the answer modulo p^2 for p>=5.
    residue=0 if v>1 else (z.numerator//p)*pow(z.denominator,-1,p)%p
    return {"valuation":v,"parameter_over_p_mod_p":residue}


def bsd():
    P=(F(-9),F(120));Q=(F(-64,25),F(8184,125))
    ordinary=[];outside=[]
    for p in (3,5,7,11,13,17,19,23,29,31,37,41):
        if p==41:
            outside.append(dict(p=p,reason="bad reduction"));continue
        N=count(p);ap=p+1-N
        if p<5 or ap%p==0:
            outside.append(dict(p=p,point_count=N,trace=ap,reason="p<5 or supersingular"));continue
        assert p%4==1
        a=local_parameter(P,p,N);b=local_parameter(Q,p,N)
        r=a["parameter_over_p_mod_p"];s=b["parameter_over_p_mod_p"]
        assert r or s
        ordinary.append(dict(p=p,point_count=N,trace=ap,P=a,Q=b,
                             kernel_vector_mod_p=[s,(-r)%p]))
    assert len(ordinary)==5
    previous=prior_bsd()
    assert previous["analytic_rank"]==previous["mordell_weil_rank"]==2
    return dict(curve="E_41",ordinary_local_certificates=ordinary,excluded_primes=outside,
                analytic_rank_from_cycle4=2,rational_rank_from_cycle4=2,
                theorem="Castella CM Theorem B (2026-02-13), conditional on admissible auxiliary characters",
                implication="Kato nonvanishing iff p-primary Sha finite on E_41; neither side computed",
                kato_nonvanishing_established=False,odd_primary_sha_finiteness_established=False)


def run():
    q=build_queue(load("docs/research/BREAKTHROUGH_FOCUS.v2.json"),
                  load("docs/proof-analysis/OBLIGATIONS.v1.json"),
                  load("docs/research/CLAY_PROOF_ROUTES.v1.json"))
    return dict(status="RESEARCH_ONLY",promotion="NONE",cycle=5,open_obligations=14,
                results={short:{"intake":intake(load(f"docs/research/breakthrough/{short}.candidate.json"),q),
                                "controls":fn()} for short,fn in (("PNP-B005",pnp),("BSD-B005",bsd))})


if __name__=="__main__":print(json.dumps(run(),indent=2))
