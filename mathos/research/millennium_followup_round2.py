"""Second seven-track research round: bounded derivations, not prize proofs."""
from fractions import Fraction as F
from itertools import combinations, product
from math import comb, exp, log, ceil
import json
from mathos.research.millennium_followup_20261124 import rank, require


def rh():
    # q(t)=t p(t²). For real nodes j=1..m, interpolate p at j².
    # Negative imaginary contribution is controlled by exact weighted Cauchy-Schwarz.
    rows=[]
    for m in range(1,7):
        eps=F(1,2)
        while True:
            ell=[]
            for j in range(1,m+1):
                v=F(1)
                for k in range(1,m+1):
                    if k!=j:
                        v*=(-eps*eps-k*k)/F(j*j-k*k)
                ell.append(v)
            bound=eps*eps*sum(v*v/F(j*j) for j,v in enumerate(ell,1))
            if bound<1:
                break
            eps/=2
        # q=t*product(t²-j²), square sum at ±i eps only
        neg=-2*eps*eps
        for j in range(1,m+1):
            neg*=(-eps*eps-j*j)**2
        require(neg<0 and bound<1,'spectral certificate')
        rows.append({'real_pairs':m,'epsilon':str(eps),'interpolation_bound':str(bound),
                     'minimum_degree':2*m+1,'negative_witness':str(neg)})
    return rows


def pnp():
    # Delay the two edges incident to the initially assigned vertex to the end.
    # Compare with a deliberately non-adjacent fixed permutation.
    rows=[]
    for n in (5,7,9,11,21):
        edges=[(i,(i+1)%n) for i in range(n)]
        order=list(range(1,n-1,2))+list(range(2,n-1,2))+[0,n-1]
        require(sorted(order)==list(range(n)),'edge order')
        scans=reads=0
        for bit in (0,1):
            values={0:bit}
            while True:
                scans+=1
                before=len(values)
                conflict=False
                for i in order:
                    a,b=edges[i]
                    for sign in (1,0):
                        reads+=2
                        if sign in (values.get(a),values.get(b)):
                            continue
                        missing=[v for v in (a,b) if v not in values]
                        if len(missing)==1:
                            values[missing[0]]=sign
                        elif not missing:
                            conflict=True
                            break
                    if conflict:
                        break
                if conflict:
                    break
                require(len(values)>before,'unexpected stall')
        require(scans>2 and reads>8*n-2,'expected delayed propagation')
        rows.append({'n':n,'baseline_reads':8*n-2,'permuted_reads':reads,'total_scans':scans})
    return rows


def ns():
    # u from NS-001, negated and multiplied by A. Fourier modes are orthogonal.
    # mean stretching scales cubically, palinstrophy quadratically.
    from mathos.research.millennium_followup_20261124 import ns as prior
    require(prior()['mean_vorticity_stretching']=='-1/4','prior identity')
    # sin y, sin z, sin 2x, sin x, sin(x+y), each solenoidal component
    wave_squared=(1,1,4,1,2)
    palinstrophy=sum(F(k*k,2) for k in wave_squared)
    require(palinstrophy==F(23,2),'palinstrophy')
    rows=[]
    for A in (1,45,46,47,100):
        value=F(A**3,4)-palinstrophy*A*A # nu=1
        require((value>0)==(A>46),'threshold')
        rows.append({'A':A,'half_enstrophy_derivative_mean':str(value)})
    return {'viscosity':1,'positive_threshold':'A > 46 nu',
            'base_palinstrophy':str(palinstrophy),'cases':rows}


def ym():
    # For two exponentials, visibility of slow relative to fast depends on
    # log((1-w)/w)/(fast-slow), not gap alone.
    rows=[]
    for k in (4,8,16,32):
        a=1/k; slow=a; fast=1
        for p in (0,1,2):
            w=0.25*a**p
            t=log((1-w)/w)/(fast-slow)
            require(t>0,'crossing')
            require(abs(w*exp(-slow*t)-(1-w)*exp(-fast*t))<1e-12,'cross equality')
            rows.append({'inverse_spacing':k,'overlap_power':p,'crossover_time':round(t,9)})
    return rows


def hodge():
    # Products of m pair differences; use noncrossing perfect matchings.
    def matchings(indices):
        if not indices:
            yield ()
            return
        first=indices[0]
        for j in range(1,len(indices),2):
            for l in matchings(indices[1:j]):
                for r in matchings(indices[j+1:]):
                    yield ((first,indices[j]),)+l+r
    rows=[]
    for m in range(1,6):
        n=2*m
        subsets=list(combinations(range(n),m))
        index={s:i for i,s in enumerate(subsets)}
        vectors=[]
        for matching in matchings(tuple(range(n))):
            v=[0]*len(subsets)
            for bits in product((0,1),repeat=m):
                s=tuple(sorted(pair[b] for pair,b in zip(matching,bits)))
                v[index[s]]=(-1)**sum(bits)
            # U kills every product (Ai+Aj)(Ai-Aj)=0.
            for t in combinations(range(n),m+1):
                require(sum(v[index[s]] for s in combinations(t,m))==0,'not primitive')
            vectors.append(v)
        dim=comb(n,m)-comb(n,m+1)
        require(len(vectors)==dim and rank(vectors)==dim,'basis rank')
        rows.append({'m':m,'primitive_dimension':dim,'noncrossing_basis_size':len(vectors)})
    return rows


def bsd():
    # Direct field enumeration via irreducible monic moduli over F5.
    # x^3+x+1 has no F5 root; x^4+2 roots have order 16 and degree ord_16(5)=4.
    rows=[]
    for degree,mod in ((3,(1,1,0)),(4,(2,0,0,0))):
        elements=list(product(range(5),repeat=degree))
        def mul(a,b):
            c=[0]*(2*degree-1)
            for i,x in enumerate(a):
                for j,y in enumerate(b):
                    c[i+j]=(c[i+j]+x*y)%5
            for k in range(len(c)-1,degree-1,-1):
                for j,v in enumerate(mod):
                    c[k-degree+j]=(c[k-degree+j]-c[k]*v)%5
            return tuple(c[:degree])
        squares={}
        for y in elements:
            s=mul(y,y)
            squares[s]=squares.get(s,0)+1
        for d,t in ((1,-2),(2,2)):
            trace0,trace1=2,t
            for _ in range(2,degree+1):
                trace0,trace1=trace1,t*trace1-5*trace0
            count=1+sum(squares.get(tuple((z-d*d*w)%5 for z,w in zip(mul(mul(x,x),x),x)),0)
                        for x in elements)
            require(count==5**degree+1-trace1,'Frobenius mismatch')
            rows.append({'degree':degree,'d':d,'trace':trace1,'points':count})
    require(rows[0]['points']!=rows[1]['points'] and rows[2]['points']==rows[3]['points'],'twist parity')
    return rows


def poincare():
    # Normalized comparison variable r=(t+C)^(1/4); smooth slope <= -1.
    # Jumps double V at unit r steps. P=2^j; total forcing integral is 2.
    # With V(0)=3 the equality trajectory stays positive forever.
    v=F(3);P=F(1);forcing=F(0);rows=[]
    for j in range(1,13):
        v-=1;forcing+=1/P
        require(v/P==3-forcing and v>0,'comparison')
        P*=2;v*=2
        rows.append({'step':j,'product':str(P),'normalized_width':str(v/P),'forcing':str(forcing)})
    return {'conditional_only':True,'forcing_limit':'2','initial_width':'3','rows':rows}


def run():
    return {'status':'BOUNDED_RESEARCH_NOT_CERTIFIED','globally_proved':0,
            'rh':rh(),'p_vs_np':pnp(),'navier_stokes':ns(),'yang_mills':ym(),
            'hodge':hodge(),'bsd':bsd(),'poincare':poincare()}


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
