"""Cycle 4: explicit CNF projection barrier and independent rank-two certificate."""
from fractions import Fraction as F
from math import isqrt
from itertools import product
import json
from mathos.research.breakthrough_focus import build_queue, intake, load


def parity_gate(vs, target):
    return {frozenset(-v if bit else v for v,bit in zip(vs,bits))
            for bits in product((0,1),repeat=len(vs)) if sum(bits)%2!=target}


def chain(n,start,target):
    aux=list(range(start,start+n-2))
    clauses=parity_gate([1,2,aux[0]],0)
    for i in range(1,len(aux)):
        clauses |= parity_gate([aux[i-1],i+2,aux[i]],0)
    clauses |= parity_gate([aux[-1],n],target)
    return clauses,aux


def eliminate(clauses,v):
    pos=[c-{v} for c in clauses if v in c]
    neg=[c-{-v} for c in clauses if -v in c]
    out={c for c in clauses if v not in c and -v not in c}
    for a in pos:
        for b in neg:
            c=a|b
            if not any(-l in c for l in c): out.add(frozenset(c))
    return out


def pnp():
    rows=[]
    for n in range(3,13):
        a,va=chain(n,n+1,0)
        b,vb=chain(n,2*n-1,1)
        clauses=a|b
        initial=len(clauses)
        for v in va: clauses=eliminate(clauses,v)
        projected={c for c in clauses if all(abs(l)<=n for l in c)}
        assert projected==parity_gate(list(range(1,n+1)),0)
        assert len(projected)==2**(n-1)
        assert len(clauses)==len(projected)+len(b)
        rows.append(dict(n=n,input_clauses=initial,projected_clauses=len(projected),
                         projected_literal_occurrences=sum(map(len,projected))))
    return dict(cases=rows,representation="explicit CNF, first chain auxiliaries first",
                xor_certificate="sum both chains over GF(2): 0=1",
                general_sat_lower_bound_proved=False)


def count(p):
    return 1+sum(1 if (v:=(x*x*x-1681*x)%p)==0 else
                 2 if pow(v,(p-1)//2,p)==1 else 0 for x in range(p))


def coefficients(N):
    # Multiplicativity and local Euler polynomials.
    a=[0]*(N+1);a[1]=1
    for p in range(2,N+1):
        if any(p%d==0 for d in range(2,isqrt(p)+1)): continue
        ap=0 if p in (2,41) else p+1-count(p)
        pk=p;prev=1;cur=ap
        while pk<=N:
            for m in range(1,N//pk+1):
                if m%p: a[m*pk]=a[m]*cur
            prev,cur=cur,ap*cur-(0 if p in (2,41) else p*prev)
            pk*=p
    assert all(abs(a[n])<=2*n for n in range(1,N+1))
    return a


def squareclass(q):
    q=F(q);n=q.numerator*q.denominator
    result=-1 if n<0 else 1;n=abs(n);p=2
    while p*p<=n:
        parity=0
        while n%p==0:n//=p;parity^=1
        if parity:result*=p
        p+=1
    return result*n


def integral_certificate():
    # All interval operations use integer fixed point with outward rounding.
    # 27/1000 < c=2*pi/sqrt(53792) < 28/1000.
    N=512;M=10**18;a=coefficients(N)
    def down(x):return x.numerator*M//x.denominator
    def up(x):return -((-x.numerator*M)//x.denominator)
    x=F(14,1000);y=F(27,2000)
    ql=down(1-x+x*x/2-x**3/6)
    qh=up(1-y+y*y/2-y**3/6+y**4/24)
    def mullo(x,y):return x*y//M
    def mulhi(x,y):return (x*y+M-1)//M
    def components(l,h):
        pl=ph=M
        lp=hp=ln=hn=0
        for n in range(1,N+1):
            pl=mullo(pl,l);ph=mulhi(ph,h)
            if a[n]>=0:lp+=a[n]*pl;hp+=a[n]*ph
            else:ln+=a[n]*ph;hn+=a[n]*pl
        return lp,hp,ln,hn
    lo=hi=M
    last=None;total_lo=F(0);total_hi=F(0)
    # t=j/2, j=2,...,1024. 2*dt=1.
    for j in range(1,1025):
        lo=mullo(lo,ql);hi=mulhi(hi,qh)
        if j<2:continue
        cur=components(lo,hi)
        if last is not None:
            fl=F(cur[0]+last[2],M)
            fh=F(last[1]+cur[3],M)
            # floor(log2(t)) times lower bound for log 2,
            # and next integer times upper bound for log 2.
            wl=(F(2,3)*((j-1).bit_length()-2))**2
            wh=(F(7,10)*(j.bit_length()-1))**2
            vals=[fl*wl,fl*wh,fh*wl,fh*wh]
            total_lo+=min(vals);total_hi+=max(vals)
        last=cur
    # |a_n| <= 2n, log(t)<=t-1, c>1/40, e^-1/40<40/41.
    r=F(40,41)
    n_tail=8*40**3*41*r**513/F(513**2)
    # For t>=512, sum 2n exp(-nt/40) <=8 exp(-t/40);
    # log(t)^2<=t, including t>=1.
    assert r**512<F(1,2)
    t_tail=16*40*(512+40)*r**512
    assert n_tail<1 and t_tail<2
    lower=total_lo-n_tail-t_tail
    upper=total_hi+n_tail+t_tail
    assert lower>300 and upper<850
    return {"truncation":N,"mesh_intervals":1022,
            "completed_second_derivative_lower":300,
            "completed_second_derivative_upper":850,
            "quadrature_lower_floor":total_lo.numerator//total_lo.denominator,
            "quadrature_upper_ceiling":-(-total_hi.numerator//total_hi.denominator),
            "coefficient_tail_lt":1,"time_tail_lt":2,
            "arithmetic":"integer outward rounding and rational tail bounds"}


def bsd():
    pts=[(F(-9),F(120)),(F(-64,25),F(8184,125))]
    for x,y in pts:assert y*y==x*x*x-1681*x
    classes=[tuple(squareclass(z) for z in (x,x-41,x+41)) for x,y in pts]
    tors={(1,1,1),(-1,-41,41),(41,2,82),(-41,-82,2)}
    cross=tuple(squareclass(a*b) for a,b in zip(*classes))
    assert all(t not in tors for t in (*classes,cross))
    assert count(3)==4 and count(7)==8
    assert pow(2,20,41)==1 and pow(-2,20,41)==1
    # Monsky for odd prime 41: zero 2x2 matrix.
    counts=[sum(2*x*x+y*y+k*z*z==41 for x,y,z in product(range(-7,8),repeat=3))
            for k in (32,8)]
    assert counts==[16,32]
    return {"curve":"y^2=x^3-1681*x","points":[[str(x),str(y)] for x,y in pts],
            "kummer_classes":classes,"product_class":cross,
            "good_reduction_counts":{"3":4,"7":8},
            "monsky_nullity":2,"tunnell_counts":counts,
            "analytic_rank":2,"mordell_weil_rank":2,"selmer_2_infty_corank":2,
            "sha_2_primary_trivial":True,"all_prime_sha_finiteness_proved":False,
            "analytic_certificate":integral_certificate(),
            "scope":"one curve; uses classical descent, modularity, Tunnell and functional equation"}


def run():
    q=build_queue(load("docs/research/BREAKTHROUGH_FOCUS.v2.json"),
                  load("docs/proof-analysis/OBLIGATIONS.v1.json"),
                  load("docs/research/CLAY_PROOF_ROUTES.v1.json"))
    return dict(status="RESEARCH_ONLY",promotion="NONE",cycle=4,open_obligations=14,
                results={short:{"intake":intake(load(f"docs/research/breakthrough/{short}.candidate.json"),q),
                                "controls":fn()} for short,fn in (("PNP-B004",pnp),("BSD-B004",bsd))})


if __name__=="__main__":print(json.dumps(run(),indent=2))
