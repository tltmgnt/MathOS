"""Third-round bounded mathematical obligations. No global theorem certification."""
from fractions import Fraction as F
from itertools import combinations, combinations_with_replacement
from math import comb, factorial, isqrt, exp, log
import json
from mathos.research.millennium_followup_20261124 import rank, require


def rh():
    e=F(1,4); upper=F(32,49); rows=[]
    for m in range(1,33):
        ell=[]
        for j in range(1,m+1):
            v=F(2*factorial(m)**2,factorial(m-j)*factorial(m+j))
            for k in range(1,m+1):
                if k!=j: v*=1+e*e/(k*k)
            require(v<=F(16,7),'uniform Lagrange bound')
            ell.append(v)
        b=e*e*sum(v*v/F(j*j) for j,v in enumerate(ell,1))
        require(b<=upper<1,'uniform positivity')
        rows.append({'m':m,'minimum_degree':2*m+1,'bound_below_uniform_ceiling':True})
    return {'epsilon':'1/4','uniform_ceiling':str(upper),'cases':len(rows),'max_minimum_degree':rows[-1]['minimum_degree']}


def pnp():
    rows=[]
    for n in range(5,102,2):
        edges=[(i,(i+1)%n) for i in range(n)]
        order=list(range(1,n-1,2))+list(range(2,n-1,2))+[0,n-1]
        reads=0; traces=[]
        for bit in (0,1):
            values={0:bit}; full=0
            while True:
                conflict=False
                for edge in order:
                    a,b=edges[edge]
                    for sign in (1,0):
                        reads+=2
                        if sign in (values.get(a),values.get(b)): continue
                        missing=[v for v in (a,b) if v not in values]
                        if len(missing)==1: values[missing[0]]=sign
                        elif not missing:
                            conflict=True;break
                    if conflict: break
                if conflict:
                    traces.append((full,edge));break
                full+=1
                require(full<=n,'propagation did not terminate')
        k=n//4
        if n%4==1:
            expected=8*n*k+24*k-2; trace=(k,2*k)
        else:
            expected=8*n*(k+1)+8*k+6; trace=(k+1,2*k+1)
        require(reads==expected and traces==[trace,trace],'cost formula')
        rows.append({'n':n,'reads':reads,'full_scans_per_branch':trace[0],
                     'conflict_edge':trace[1],'queue_edge_visits_upper_bound':4*n})
    return {'cases':len(rows),'largest':rows[-1],'formula_4k_plus_1':'8*n*k+24*k-2','formula_4k_plus_3':'8*n*(k+1)+8*k+6'}


def ns():
    # E' <= 2*(C² E^(3/4) D^(3/4)-nu D) <= K E³.
    # Rational check of weighted Young inequality with x=(D/E³)^(1/4).
    # 27/256 - x³ + x⁴ = (x-3/4)²*(x²+x/2+3/16).
    for x in (F(0),F(1,4),F(1,2),F(3,4),F(1),F(2),F(10)):
        require(F(27,256)-x**3+x**4==(x-F(3,4))**2*(x*x+x/2+F(3,16))>=0,'Young certificate')
    # E0 at A=47 using normalized volume; K assumes C=nu=1 for illustration only.
    E0=F(9,2)*47**2
    K=F(27,128)
    horizon=1/(2*K*E0**2)
    return {'initial_enstrophy_A47':str(E0),'K':'27*C^8/(128*nu^3)',
            'conditional_bound':'E(t)<=E0/sqrt(1-2*K*E0^2*t)',
            'illustrative_horizon_C1_nu1':str(horizon),'young_controls':7}


def ym():
    # Low window [0,s], high sector [f,infinity), total low weight w.
    # Check the sharp bound on a family of finite positive discrete measures.
    rows=[]
    for w in (F(1,10),F(1,4),F(2,5)):
        for s,f in ((0.1,0.8),(0.25,1.0),(0.5,2.0)):
            t=log(float((1-w)/w))/(f-s)
            for factor in (0,0.5,1,2):
                x=t*factor
                lo=float(w)*(exp(-s*x)+exp(-s*x/2))/2
                hi=float(1-w)*(exp(-f*x)+exp(-2*f*x))/2
                bound=float((1-w)/w)*exp(-(f-s)*x)
                require(hi/lo<=bound+1e-12,'spectral measure bound')
            require(abs(float(1-w)*exp(-f*t)-float(w)*exp(-s*t))<1e-12,'sharp endpoint')
            rows.append({'w':str(w),'s':s,'f':f,'crossover_upper':round(t,9)})
    return {'cases':len(rows),'inequality_checks':36,'sharp_endpoints':9,'examples':rows}


def wedge(a,b):
    out={}
    for x,c in a.items():
        for y,d in b.items():
            if set(x)&set(y): continue
            z=tuple(sorted(x+y));sign=(-1)**sum(i>j for i in x for j in y)
            out[z]=out.get(z,0)+sign*c*d
    return {k:v for k,v in out.items() if v}


def hodge():
    # Exterior algebra on e0,f0,...,e3,f3. Diagonal SL2 invariants.
    n=4; B=[{(2*i,2*i+1):1} for i in range(n)]
    for i,j in combinations(range(n),2):
        B.append({(2*i,2*j+1):1,(2*i+1,2*j):-1})
    basis4=list(combinations(range(8),4));basis6=list(combinations(range(8),6))
    products=[wedge(a,b) for a,b in combinations_with_replacement(B,2)]
    vectors=[[p.get(x,0) for x in basis4] for p in products]
    H={(2*i,2*i+1):1 for i in range(n)}
    images=[wedge(H,p) for p in products]
    r=rank(vectors); lr=rank([[p.get(x,0) for x in basis6] for p in images])
    # Weight-zero dimension minus weight-two dimension in finite-dimensional sl2 module.
    invariant_dim=comb(4,2)**2-comb(4,3)*comb(4,1)
    require(rank([[p.get(x,0) for x in combinations(range(8),2)] for p in B])==10,'divisor rank')
    require(r==invariant_dim==20 and lr==10,'invariant/primitive rank')
    return {'divisor_classes':10,'products_tested':55,'degree4_invariant_dimension':20,'product_span_rank':r,'primitive_dimension':r-lr}


def bsd():
    # For p>=5, Hasse integer |a|<p. Nonzero a gives s_r == a^r mod p.
    def trace(p,a,r):
        x,y=2,a
        for _ in range(2,r+1): x,y=y,a*y-p*x
        return y
    rows=[]; cases=0
    for p in (5,7,11,13,17,19,23,29,31):
        vals=range(-isqrt(4*p),isqrt(4*p)+1)
        for r in (1,3,5,7,9):
            pairs={(trace(p,a,2),trace(p,a,r)) for a in vals}
            require(len(pairs)==len(vals),'recovery collision')
            for a in vals:
                require(trace(p,a,r)%p==pow(a,r,p),'trace congruence')
                if a: require(trace(p,a,r)!=0,'unexpected odd zero')
            cases+=len(vals)
        rows.append({'p':p,'candidate_traces':len(vals)})
    return {'prime_count':len(rows),'odd_degrees':[1,3,5,7,9],'trace_degree_cases':cases,'collisions':0}


def poincare():
    # Limit of almost nonexpanding comparison maps: Wplus <= xi² Wminus(t).
    # If Wminus(t) has finite liminf and xi->1, no upward jump.
    # Exact squeeze for toy Wminus(t_j)=3+1/j, xi=1+1/j.
    rows=[]
    for j in (2,4,8,16,32,64):
        upper=(1+F(1,j))**2*(3+F(1,j))
        error=F(7,j)+F(5,j*j)+F(1,j**3)
        require(upper==3+error and error<=F(13,j),'limit')
        rows.append({'j':j,'comparison_upper':str(upper),'error_bound':str(F(13,j))})
    return {'source':'Kleiner-Lott Remark 73.6; Colding-Minicozzi published Theorem 1.4 and Corollary 1.7',
            'conditional_jump_factor':1,'limit_controls':len(rows),'examples':rows}


def run():
    return {'status':'BOUNDED_RESEARCH_NOT_CERTIFIED','globally_proved':0,
            'rh':rh(),'p_vs_np':pnp(),'navier_stokes':ns(),'yang_mills':ym(),
            'hodge':hodge(),'bsd':bsd(),'poincare':poincare()}


if __name__=='__main__': print(json.dumps(run(),indent=2))
