"""TGA-U002: arithmetic xi moments and actual algebraic determinant-square cycles.

The xi enclosures are rigorous integer interval calculations, not an all-order
positivity certificate. Tensor tests illustrate the cycle identity in small
abstract quadratic spaces, not computations of K3 periods or cycle classes.
"""
from fractions import Fraction as F
from math import factorial
from itertools import permutations,product
import json
from mathos.research.breakthrough_cycle6 import I,M,atan
from mathos.research.tga_universal_bridges import det


def exp_step(x):
    # x in [0,1/2]; positive Taylor sum, tail <= twice next term
    assert 0<=x<=F(1,2)
    s=sum((x**j/factorial(j) for j in range(21)),F(0))
    return I(I.rat(s).l,I.rat(s+2*x**21/factorial(21)).h)


def exp_negative(x):
    assert x.l>=0
    if x.l>=128*M:
        return I(0,I.rat(F(1,2**128)).h)
    # At the crossing the upper argument can slightly exceed 128;
    # reduce both endpoints by 256 and use alternating Taylor.
    z=x.scaled(F(1,256))
    assert z.h<=M
    a=I.rat(1);s=a
    for j in range(1,27):
        a=(a*z).scaled(F(1,j))
        s=s-a if j%2 else s+a
        if j==25:lo=s.l
    r=I(lo,s.h)
    assert r.l>=0
    for _ in range(8):r=r*r
    return r


def xi_moments(steps=65536):
    # Integrate t in [0,2], with steps intervals and n=1,...,5.
    # The common factor 2 in the xi cosine kernel cancels on normalization.
    pi=atan(5).scaled(16)-atan(239).scaled(4)
    h=F(2,steps);inc=exp_step(h/2);half=I.rat(1)
    acc=[I.rat(0) for _ in range(5)]
    def endpoint(half):
        e2=half.pow(4);v=[]
        for n in range(1,6):
            u=(pi*e2).scaled(n*n)
            a=(u*u).scaled(4)-u.scaled(6)
            a=a*half
            v.append((a,exp_negative(u)))
        return v
    prev=endpoint(half)
    for j in range(1,steps+1):
        half=half*inc;cur=endpoint(half)
        # A(t) increasing and exp(-u(t)) decreasing; all nonnegative.
        lo=sum((I(a.l)*I(e.l)).l for (a,_),(_,e) in zip(prev,cur))
        hi=sum((I(a.h)*I(e.h)).h for (a,_),(_,e) in zip(cur,prev))
        assert 0<=lo<=hi
        for k in range(5):
            l=I(lo).scaled(h*((j-1)*h)**(2*k)/factorial(2*k)).l
            r=I(hi).scaled(h*(j*h)**(2*k)/factorial(2*k)).h
            acc[k]=acc[k]+I(l,r)
        prev=cur
    # For omitted t>=2: Phi t^(2k)/(2k)! <= 64 exp(3t/2) exp(-u/2)
    # u>=150 n^2 (1+2(t-2)); e^3<27. For omitted n>=6:
    # u>=3 n^2(1+2t), exp(-1.5 n^2)<4^(-n^2).
    t_tail=F(1728,148)*F(1,2**75)/(1-F(1,2**75))
    n_tail=F(64,1)*F(1,4**36)/(1-F(1,4))
    assert t_tail+n_tail<F(1,10**17)
    acc=[I(a.l,a.h+I.rat(t_tail+n_tail).h) for a in acc]
    g=[I.rat(1)]+[(acc[k]/acc[0]).scaled((-1)**k) for k in range(1,5)]
    m=[]
    for n in range(4):
        v=g[n+1].scaled(-(n+1))
        for j in range(1,n+1):v=v-g[j]*m[n-j]
        m.append(v)
    d0=m[0]*m[2]-m[1]*m[1]
    d1=m[1]*m[3]-m[2]*m[2]
    def bounds(a):return [str(a.l),str(a.h)]
    return {"steps":steps,"terms":5,"scale":str(M),
            "integral_bounds":[bounds(x) for x in acc],
            "moment_bounds":[bounds(x) for x in m],
            "hankel_2x2_determinant_bounds":[bounds(d0),bounds(d1)],
            "unshifted_2x2_positive":m[0].l>0 and d0.l>0,
            "shifted_2x2_positive":m[1].l>0 and d1.l>0,
            "all_order_positivity_proved":False}


def sign(p):
    return (-1)**sum(p[i]>p[j] for i in range(len(p)) for j in range(i+1,len(p)))


def determinant_tensor_controls():
    rows=[]
    # q diagonal with nontrivial signs and denominators. In the chosen basis
    # q^{-1} = diag(v). The tensor determinant of pairings equals
    # det(q^{-1}) times the alternating tensor squared.
    for r in range(2,6):
        v=[F((-1)**j,j+1) for j in range(r)]
        ps=list(permutations(range(r)))
        c=F(1)
        for a in v:c*=a
        checks=0
        for a in ps:
            for b in ps:
                matrix=[[v[x] if x==y else F(0) for y in b] for x in a]
                assert det(matrix)==c*sign(a)*sign(b)
                checks+=1
        # Repeated indices give zero determinant and zero alternating tensor.
        bad=(0,)*(r)
        assert det([[v[x] if x==y else 0 for y in ps[0]] for x in bad])==0
        rows.append({"rank":r,"permutation_pairs_checked":checks,
                     "normalization":str(c),"repeated_index_zero":True})
    return {"cases":rows,"determinant_square_identity_checked":True,
            "determinant_class_algebraicity_proved":False}


def run():
    return {"status":"RESEARCH_ONLY","promotion":"NONE","canonical_open_obligations":14,
            "rh":xi_moments(),"hodge":determinant_tensor_controls()}

if __name__=="__main__":print(json.dumps(run(),indent=2))
