"""Cycle 6: complete defined use cases without making external review a gate."""
from fractions import Fraction as F
from itertools import product
from math import isqrt
import json
from mathos.research.breakthrough_focus import build_queue, intake, load
from mathos.research.breakthrough_cycle4 import bsd as rank_baseline

M=10**65


class I:
    def __init__(self,l,h=None):
        self.l=l; self.h=l if h is None else h
        assert self.l<=self.h
    @classmethod
    def rat(cls,v):
        v=F(v)*M
        return cls(v.numerator//v.denominator,-((-v.numerator)//v.denominator))
    def __add__(a,b):return I(a.l+b.l,a.h+b.h)
    def __neg__(a):return I(-a.h,-a.l)
    def __sub__(a,b):return a+-b
    def __mul__(a,b):
        v=[x*y for x in (a.l,a.h) for y in (b.l,b.h)]
        return I(min(v)//M,-((-max(v))//M))
    def __truediv__(a,b):
        assert b.l>0
        v=[F(x*M,y) for x in (a.l,a.h) for y in (b.l,b.h)]
        lo=min(v);hi=max(v)
        return I(lo.numerator//lo.denominator,-((-hi.numerator)//hi.denominator))
    def sqrt(a):
        assert a.l>=0
        return I(isqrt(a.l*M),isqrt(a.h*M)+1)
    def pow(a,n):
        r=I.rat(1)
        for _ in range(n):r=r*a
        return r
    def scaled(a,n):return a*I.rat(n)
    def bounds(a):return F(a.l,M),F(a.h,M)


def atan(q):
    s=sum((F((-1)**j,(2*j+1)*q**(2*j+1)) for j in range(100)),F(0))
    err=F(1,201*q**201)
    return I(I.rat(s).l,I.rat(s+err).h)


def hecke_certificate():
    pi=atan(5).scaled(16)-atan(239).scaled(4)
    c=pi.scaled(2)/I.rat(53792).sqrt()
    assert c.l>M//40 and c.h<3*M//100
    a,b=I.rat(2).sqrt(),I.rat(1)
    for _ in range(12):a,b=(a+b).scaled(F(1,2)),(a*b).sqrt()
    period=pi/I(b.l,a.h)/I.rat(41).sqrt()
    def exp_poly(x,k):
        term=F(1);s=term
        for j in range(1,k+1):
            term*=(-x)/j;s+=term
        return s
    q=I(I.rat(exp_poly(F(c.h,M),49)).l,I.rat(exp_poly(F(c.l,M),50)).h)
    B=5000;coef=[0]*(B+1);coef[1]=1
    for p in range(2,B+1):
        if any(p%d==0 for d in range(2,isqrt(p)+1)):continue
        if p in (2,41):ap=pp=0
        else:
            t=-sum(0 if (v:=(x*x*x-1681*x)%p)==0 else
                   1 if pow(v,(p-1)//2,p)==1 else -1 for x in range(p))
            s0,s1=2,t
            for _ in range(2,6):s0,s1=s1,t*s1-p*s0
            ap=s1;pp=p**5
        pk=p;u,v=1,ap
        while pk<=B:
            for j in range(1,B//pk+1):
                if j%p:coef[j*pk]=coef[j]*v
            pk*=p;u,v=v,ap*v-pp*u
    qn=I.rat(1);ls=I.rat(0);der=I.rat(0);one=I.rat(1);c4=c.pow(4)
    for n in range(1,B+1):
        assert abs(coef[n])<=2*n**3
        qn=qn*q;cn=c.scaled(n);an=qn.scaled(coef[n])
        der=der+an*(I.rat(3)-cn)
        poly=one;term=one
        for j in range(1,5):
            term=(term*cn).scaled(F(1,j));poly=poly+term
        ls=ls+an*(poly.scaled(F(1,n**5))-c4.scaled(F(1,24*n)))
    r=F(40,41);m=B+1
    # n=m+j: n^k <= m^k(1+j)^k <= m^k k! binom(j+k,k).
    lt=12*m*m*2*r**m/(1-r)**3
    dt=8*m**4*24*r**m/(1-r)**5
    assert lt<F(1,10**35) and dt<F(1,10**25)
    def widen(x,t):
        z=I.rat(t).h
        return I(x.l-z,x.h+z)
    der=widen(der,dt)
    # If sign +1, derivative plus 3*value at t=1 must be zero.
    assert der.h<0 or der.l>0
    ls=widen(ls,lt)
    # Corrected CLS trace formula: f=82(1+i), f^5=-4*82^5*(1+i), which divides 8*82^5 in Z[i].
    # The rational result is an algebraic integer after this scaling. f-torsion killed by 164.
    # 164^5 times wp'''=24xy is integral; hence the rational scaled value
    # below is an integer. Justification and dependencies in BSD-B006.
    den=24*8*82**5*164**5
    scaled=(ls/period.pow(5)).scaled(den)
    l,h=scaled.bounds();n=-(-l.numerator//l.denominator)
    assert n==h.numerator//h.denominator
    assert n%125==50 and den%5!=0
    assert l>n-F(1,1000) and h<n+F(1,1000)
    value=F(n,den)
    return {"terms":B,"root_number_of_weight6_form":-1,
            "center_derivative_test_integer_interval":[str(der.l),str(der.h)],
            "fixed_point_scale":str(M),"scaled_integer":str(n),"scale_denominator":str(den),
            "scaled_interval_integer_endpoints":[str(scaled.l),str(scaled.h)],
            "normalized_hecke_value":str(value),"scaled_integer_mod_125":n%125,
            "valuation_at_5":2,"tail_bound_lt":"1e-35",
            "integer_reconstruction":"unique integer in rigorous interval, conditional on stated trace identity"}


def solve_blocks(blocks,rows):
    """Disjoint two-input blocks: each allowed set of pairs is explicit.
    Arbitrary GF(2) equations on their AND outputs; return witness or XOR proof.
    Rows are (bitmask, rhs). All row provenance is retained.
    """
    n=len(blocks);eq=list(rows)
    if any(a not in (0,1) or b not in (0,1) for block in blocks for a,b in block):
        raise ValueError("non-Boolean block input")
    if any(not isinstance(mask,int) or not 0<=mask<(1<<n) or rhs not in (0,1) for mask,rhs in eq):
        raise ValueError("invalid affine row")
    for b in blocks:
        if not b:return {"sat":False,"empty_block":blocks.index(b)}
    options=[{int(a and b):(a,b) for a,b in block} for block in blocks]
    for j,op in enumerate(options):
        if len(op)==1:eq.append((1<<j,next(iter(op))))
    basis={};operations=0
    for j,(mask,rhs) in enumerate(eq):
        assert 0<=mask<(1<<n) and rhs in (0,1)
        proof=1<<j
        while mask:
            p=mask.bit_length()-1
            if p not in basis:
                basis[p]=(mask,rhs,proof);break
            x,y,z=basis[p]
            mask^=x;rhs^=y;proof^=z;operations+=1
        if not mask and rhs:
            selected=[i for i in range(len(eq)) if proof>>i&1]
            a=b=0
            for i in selected:a^=eq[i][0];b^=eq[i][1]
            assert (a,b)==(0,1)
            return {"sat":False,"xor_certificate":selected,"row_xors":operations}
    y=0
    for p,(mask,rhs,_) in sorted(basis.items()):
        if (mask&y).bit_count()%2!=rhs:y|=1<<p
    witness=[op[(y>>i)&1] for i,op in enumerate(options)]
    assert all((mask&y).bit_count()%2==rhs for mask,rhs in eq)
    return {"sat":True,"witness":witness,"row_xors":operations}



def verify_result(blocks,rows,result):
    """Replay a certificate using only the original instance and returned data."""
    n=len(blocks)
    if result["sat"]:
        w=result["witness"]
        if len(w)!=n or any(tuple(pair) not in block for pair,block in zip(w,blocks)):
            return False
        y=sum((a*b)<<i for i,(a,b) in enumerate(w))
        return all((mask&y).bit_count()%2==rhs for mask,rhs in rows)
    if "empty_block" in result:
        j=result["empty_block"]
        return isinstance(j,int) and 0<=j<n and not blocks[j]
    eq=list(rows)
    for j,block in enumerate(blocks):
        outputs={a*b for a,b in block}
        if len(outputs)==1:eq.append((1<<j,next(iter(outputs))))
    sel=result.get("xor_certificate",[])
    if not sel or len(set(sel))!=len(sel) or any(not isinstance(j,int) or j<0 or j>=len(eq) for j in sel):
        return False
    mask=rhs=0
    for j in sel:mask^=eq[j][0];rhs^=eq[j][1]
    return (mask,rhs)==(0,1)

def pnp():
    # Exhaustive all nonempty local masks for 3 gates and a fixed two-row
    # coupling with independently enumerated local assignments.
    pairs=list(product((0,1),repeat=2))
    masks=[tuple(p for j,p in enumerate(pairs) if s>>j&1) for s in range(1,16)]
    checked=sat=unsat=0
    for blocks in product(masks,repeat=3):
        rows=[(3,0),(6,1)]
        expected=any(all((mask&sum((a*b)<<j for j,(a,b) in enumerate(xs))).bit_count()%2==rhs
                         for mask,rhs in rows) for xs in product(*blocks))
        result=solve_blocks(blocks,rows)
        assert result["sat"]==expected and verify_result(blocks,rows,result)
        checked+=1;sat+=expected;unsat+=not expected
    assert verify_result([()],[],solve_blocks([()],[]))
    assert not verify_result([pairs],[(1,1)],{"sat":True,"witness":[(0,0)]})
    assert not verify_result([pairs],[(1,0),(1,1)],{"sat":False,"xor_certificate":[0]})
    large=[]
    for n in (16,64,256,1024):
        blocks=[pairs]*n;mask=(1<<n)-1
        yes=solve_blocks(blocks,[(mask,0)])
        no=solve_blocks(blocks,[(mask,0),(mask,1)])
        assert yes["sat"] and not no["sat"]
        assert verify_result(blocks,[(mask,0)],yes)
        assert verify_result(blocks,[(mask,0),(mask,1)],no)
        large.append({"blocks":n,"sat_row_xors":yes["row_xors"],"unsat_row_xors":no["row_xors"]})
    return {"exhaustive_cases":checked,"sat":sat,"unsat":unsat,"large":large,
            "empty_block_control":True,"tampered_certificates_rejected":2,"use_case_completed":True,
            "general_sat_runtime_proved":False}


def bsd():
    r=rank_baseline()
    assert r["analytic_rank"]==r["mordell_weil_rank"]==2
    cert=hecke_certificate()
    assert r["sha_2_primary_trivial"] and cert["valuation_at_5"]==2
    return {"curve":"E_41","analytic_rank":2,"mordell_weil_rank":2,
            "ordinary_prime":5,"good_reduction_order":8,
            "certificate":cert,"sha_5_primary_trivial_under_CLS_theorem":True,
            "selmer_5_infty_corank":2,"all_prime_sha_finiteness_proved":False}


def run():
    q=build_queue(load("docs/research/BREAKTHROUGH_FOCUS.v2.json"),
                  load("docs/proof-analysis/OBLIGATIONS.v1.json"),
                  load("docs/research/CLAY_PROOF_ROUTES.v1.json"))
    return dict(status="RESEARCH_ONLY",promotion="NONE",cycle=6,open_obligations=14,
                results={short:{"intake":intake(load(f"docs/research/breakthrough/{short}.candidate.json"),q),
                                "controls":fn()} for short,fn in (("PNP-B006",pnp),( "BSD-B006",bsd))})


if __name__=="__main__":print(json.dumps(run(),indent=2))
