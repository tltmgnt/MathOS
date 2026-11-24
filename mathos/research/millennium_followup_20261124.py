"""Seven follow-up probes to the 2026-11-23 notebook; no prize claim."""
from fractions import Fraction as F
from itertools import combinations
from math import ceil, exp, log1p, isqrt
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rh():
    def m(k):
        return F(0) if k % 2 else 2*(1+2**k+F(-1,16)**(k//2))
    # Even polynomials have real values at all six points, so their square sum is nonnegative.
    # Odd polynomials up to degree 3 have the following positive definite Gram block.
    det=m(2)*m(6)-m(4)**2
    require(m(2)>0 and det>0,'odd block not positive')
    # t(t²-1)(t²-4) = 4t-5t³+t⁵, vanishes at all four real points.
    q={1:4,3:-5,5:1}
    negative=sum(a*b*m(i+j) for i,a in q.items() for j,b in q.items())
    require(negative<0,'degree five witness failed')
    return {'minimal_degree':5,'odd_block_determinant':str(det),'negative_square_sum':str(negative)}


def cycle(n, reverse):
    edges=[(i,(i+1)%n) for i in range(n)]
    if reverse:
        edges.reverse()
    reads=scans=0
    for first in (0,1):
        values={0:first}
        conflict=False
        while not conflict:
            scans+=1
            before=len(values)
            for i,j in edges:
                for sign in (1,0):
                    pair=[values.get(i),values.get(j)]
                    reads+=2
                    if sign in pair:
                        continue
                    missing=[v for v in (i,j) if v not in values]
                    if len(missing)==1:
                        values[missing[0]]=sign
                    elif not missing:
                        conflict=True
                        break
                if conflict:
                    break
            require(conflict or len(values)>before,'propagation stalled')
    return reads,scans


def pnp():
    rows=[]
    for n in (3,5,7,9,11):
        f,fs=cycle(n,False)
        r,rs=cycle(n,True)
        require(f==8*n-2 and r==f and fs==rs==2,'scan policy symmetry failed')
        rows.append({'n':n,'forward_reads':f,'reverse_reads':r,'forward_scans':fs,'reverse_scans':rs})
    # Reversing the cycle still starts adjacent to x0, so no repeated scan is needed.
    return rows


def ns():
    # Exact Gaussian-dyadic Fourier arithmetic. Small coefficients are exactly
    # representable as binary complex numbers, including all intermediate sums.
    from collections import defaultdict
    def trig(k, cosine=False):
        return {k:0.5 if cosine else -0.5j,tuple(-i for i in k):0.5 if cosine else 0.5j}
    def add(*polys):
        result=defaultdict(complex)
        for p in polys:
            for k,v in p.items():
                result[k]+=v
        return {k:v for k,v in result.items() if v}
    def scale(p,a):
        return {k:a*v for k,v in p.items()}
    def mul(p,q):
        r=defaultdict(complex)
        for k,v in p.items():
            for l,w in q.items():
                r[tuple(a+b for a,b in zip(k,l))]+=v*w
        return {k:v for k,v in r.items() if v}
    def derivative(p,i):
        return {k:1j*k[i]*v for k,v in p.items() if k[i]}
    u=[add(trig((0,1,0)),trig((0,0,1))),trig((2,0,0)),
       add(trig((1,0,0)),trig((1,1,0)))]
    j=[[derivative(p,i) for i in range(3)] for p in u]
    require(not add(*(j[i][i] for i in range(3))),'divergence')
    o=[add(j[2][1],scale(j[1][2],-1)),add(j[0][2],scale(j[2][0],-1)),
       add(j[1][0],scale(j[0][1],-1))]
    stretch=add(*(mul(o[i],mul(j[i][k],o[k])) for i in range(3) for k in range(3)))
    mean=stretch.get((0,0,0),0)
    require(mean==-.25,'stretching mean')
    return {'mean_vorticity_stretching':'-1/4','nonzero_integrated_stretching':True,'initial_time_only':True}


def ym():
    rows=[]
    for k in (2,4,8,16,32,64):
        a=1/k
        # Squared overlaps exp(-1/a), 1-exp(-1/a). Stable log-ratio.
        log_ratio=k+log1p(-exp(-k))
        threshold=log_ratio/(a-a*a)
        n=ceil(threshold)
        require(n-1<threshold<=n,'crossing')
        require(a*n>=k-1,'lower bound')
        rows.append({'inverse_spacing':k,'crossover_step':n,'physical_crossover_time':n/k})
    return rows


def rank(a):
    a=[list(map(F,row)) for row in a]
    i=0
    for k in range(len(a[0])):
        p=next((p for p in range(i,len(a)) if a[p][k]),None)
        if p is None:
            continue
        a[i],a[p]=a[p],a[i]
        a[i]=[v/a[i][k] for v in a[i]]
        for p in range(len(a)):
            if p!=i:
                c=a[p][k]
                a[p]=[v-c*w for v,w in zip(a[p],a[i])]
        i+=1
        if i==len(a):
            break
    return i


def hodge():
    pairs=list(combinations(range(4),2))
    triples=list(combinations(range(4),3))
    A=[[int(set(p)<=set(t)) for p in pairs] for t in triples]
    def d(i,j,k,l):
        coeff={tuple(sorted((i,k))):1,tuple(sorted((i,l))):-1,
               tuple(sorted((j,k))):-1,tuple(sorted((j,l))):1}
        return [coeff.get(p,0) for p in pairs]
    ds=[d(0,1,2,3),d(0,2,1,3),d(0,3,1,2)]
    require(all(sum(a*b for a,b in zip(row,v))==0 for row in A for v in ds),'nonprimitive')
    require(rank(A)==4 and rank(ds)==2,'rank')
    require(all(a-b+c==0 for a,b,c in zip(*ds)),'relation')
    return {'multiplication_rank':4,'primitive_dimension':2,'pairing_span_rank':2,'relation':'D12|34 - D13|24 + D14|23 = 0'}


def bsd():
    # GF(25) = GF(5)[u]/(u²-2); 2 is a nonsquare modulo 5.
    elements=[(a,b) for a in range(5) for b in range(5)]
    def mul(x,y):
        a,b=x;c,d=y
        return ((a*c+2*b*d)%5,(a*d+b*c)%5)
    rows=[]
    for d in (1,2):
        p=5
        count=1+sum((y*y-x**3+d*d*x)%p==0 for x in range(p) for y in range(p))
        a=p+1-count
        count2=1
        for x in elements:
            cube=mul(mul(x,x),x)
            rhs=tuple((z-d*d*w)%5 for z,w in zip(cube,x))
            count2+=sum(mul(y,y)==rhs for y in elements)
        require(count2==p*p+1-(a*a-2*p),'extension count')
        rows.append({'d':d,'a5':a,'euler_polynomial':[1,-a,p],'a25':a*a-p,'points_F25':count2})
    require([r['a5'] for r in rows]==[-2,2],'base counts')
    return rows


def poincare():
    # Exact rational toy replay in r=(t+C)^(1/4), normalized width V/(16π).
    # Each step has dr=1, smooth slope <= -1, jump multiplier (1+xi)^2.
    v=F(5);P=F(1);weighted=F(5);rows=[]
    for j in range(1,20):
        v-=1
        weighted-=1/P
        require(v/P==weighted,'integrating-factor identity')
        if v<0:
            rows.append({'step':j,'rescaled_width':str(v),'product':str(P)})
            break
        factor=(1+F(1,2**j))**2
        P*=factor;v*=factor
        rows.append({'step':j,'rescaled_width':str(v),'product':str(P)})
    require(v<0,'toy extinction contradiction not reached')
    return {'conditional_only':True,'toy_first_negative_step':j,'rows':rows}


def run():
    return {'status':'BOUNDED_RESEARCH_NOT_CERTIFIED','globally_proved':0,
            'rh':rh(),'p_vs_np':pnp(),'navier_stokes':ns(),'yang_mills':ym(),
            'hodge':hodge(),'bsd':bsd(),'poincare':poincare()}


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
