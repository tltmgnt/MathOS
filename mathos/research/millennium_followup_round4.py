"""Seven scoped mathematical derivations and exact finite controls."""
from fractions import Fraction as F
from itertools import combinations, product
from math import comb, factorial, isqrt, prod
import json


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rh():
    # Signed moment model: positive weights 1 at x_i, negative weight -w at z.
    # At degree <= m-1, evaluation at z is Lagrange interpolation.
    # PSD iff w * sum(l_i(z)^2) <= 1. Degree m exposes the negative atom.
    rows = []
    for m in range(1, 9):
        xs = list(range(1, m+1))
        z = F(-1, 2)
        ell = [prod((z-y)/F(x-y) for y in xs if y != x) for x in xs]
        require(all(sum(l*x**k for l,x in zip(ell,xs)) == z**k for k in range(m)), "interpolation")
        norm = sum(l*l for l in ell)
        threshold = 1/norm
        # Choose polynomial values ell: sharpness of Cauchy-Schwarz.
        forms = [norm-w*norm**2 for w in (threshold/2, threshold, 2*threshold)]
        require(forms[0]>0 and forms[1]==0 and forms[2]<0, "sharp threshold")
        witness = -threshold*prod((z-x)**2 for x in xs)
        require(witness<0, "negative degree-m witness")
        rows.append({"positive_nodes":m,"critical_weight":str(threshold),
                     "negative_form_degree_m":str(witness)})
    return {"scope":"Synthetic signed real moment measure; not zeta zeros or an RH equivalence",
            "sharp_threshold":"1 / sum_i L_i(z)^2", "cases":rows}


def separator_count(n, clauses):
    """Exact model count for an explicit variable ordering 1..n.
    Clause tests occur at the last variable of each clause. States retain
    only processed variables that occur in a not-yet-tested clause.
    """
    if type(n) is not int or not 1<=n<=30:
        raise ValueError("n must be 1..30")
    if any(not c or any(type(l) is not int or not 1<=abs(l)<=n for l in c) for c in clauses):
        raise ValueError("nonempty clauses with valid signed variables required")
    ends=[max(map(abs,c)) for c in clauses]
    last={i:max((e for c,e in zip(clauses,ends) if any(abs(l)==i for l in c)),default=i)
          for i in range(1,n+1)}
    stages={i:[c for c,e in zip(clauses,ends) if e==i] for i in range(1,n+1)}
    active=()
    states={():1}
    peak=1
    width=0
    transitions=0
    for i in range(1,n+1):
        nxt=tuple(k for k in (*active,i) if last[k]>i)
        width=max(width,len(nxt))
        if width>12:
            raise ValueError("separator width cap exceeded")
        out={}
        for bits,count in states.items():
            for b in (0,1):
                transitions+=1
                assignment=dict(zip((*active,i),(*bits,b)))
                if all(any(assignment[abs(l)]==int(l>0) for l in c) for c in stages[i]):
                    key=tuple(assignment[k] for k in nxt)
                    out[key]=out.get(key,0)+count
        active,states=nxt,out
        peak=max(peak,len(states))
    require(not active,"final frontier")
    return {"count":states.get((),0),"separator_width":width,"peak_states":peak,"transitions":transitions}


def pnp():
    # A chain of implications has n+1 satisfying assignments.
    rows=[]
    for n in range(2,31):
        r=separator_count(n,[(-i,i+1) for i in range(1,n)])
        require(r["count"]==n+1 and r["separator_width"]==1 and r["peak_states"]<=2,"chain")
        rows.append(r)
    # Independent brute force for nonlocal clauses, including tautologies.
    clauses=[(1,-3),(2,3),(-1,-2,4),(-4,4),(-5,)]
    r=separator_count(6,clauses)
    brute=sum(all(any(bits[abs(l)-1]==int(l>0) for l in c) for c in clauses)
              for bits in product((0,1),repeat=6))
    require(r["count"]==brute,"brute-force comparison")
    return {"scope":"Exact restricted-width counting, not arbitrary polynomial SAT",
            "chain_cases":len(rows),"last_chain":rows[-1],"nonlocal":r,
            "bound":"At most 2^w states per layer; counts have at most n+1 bits."}


def ns():
    # u=(sin(k y) exp(-k²t),0,0), viscosity=1, normalized torus volume.
    # Nonlinearity and divergence vanish; exact heat solution.
    # E=mean |u|², Z=mean |grad u|². Integrate exponential exactly.
    rows=[]
    for k in (1,2,4,8,16,32,64):
        E0=F(1,2); Z0=F(k*k,2)
        integrated_Z=Z0/(2*k*k)
        integrated_Z2=Z0**2/(4*k*k)
        require(integrated_Z==F(1,4) and integrated_Z2==F(k*k,16),"energy identities")
        rows.append({"frequency":k,"initial_energy":str(E0),"initial_enstrophy":str(Z0),
                     "integral_enstrophy":str(integrated_Z),"integral_enstrophy_squared":str(integrated_Z2)})
    return {"scope":"Exact smooth periodic shear family, no blowup",
            "obstruction":"Initial L2 energy alone cannot bound peak enstrophy or its squared time integral uniformly.",
            "cases":rows}


def ym():
    # Positive spectral measures on x=exp(-E) in (0,1].
    # Even and odd binomial masses on equally spaced nodes match moments < n,
    # by the nth finite difference identity. One includes x=1, the other not.
    rows=[]
    for n in range(2,13):
        xs=[F(j+1,n+1) for j in range(n+1)]
        same=[sum(F(comb(n,j),2**(n-1))*xs[j]**k for j in range(n+1) if j%2==0)
              for k in range(n+1)]
        other=[sum(F(comb(n,j),2**(n-1))*xs[j]**k for j in range(n+1) if j%2==1)
               for k in range(n+1)]
        require(same[0]==other[0]==1 and same[:-1]==other[:-1],"matched positive moments")
        require(same[-1]-other[-1]==F((-1)**n*factorial(n),2**(n-1)*(n+1)**n),"first difference")
        rows.append({"matching_moments":n,"first_difference":str(same[-1]-other[-1]),
                     "gapless_support_max":"1","gapped_support_max":str(F(n,n+1))})
    return {"scope":"Positive discrete transfer spectral measures; no gauge-theory construction",
            "obstruction":"Arbitrarily many exact finite correlators cannot alone certify a positive gap.",
            "cases":rows}


def hodge():
    # Middle degree of (P1)^(2m); L adds one factor, D deletes one.
    # [D,L] acts by n-2k on degree k. P=sum (-1)^j L^j D^j/(j!(j+1)!).
    def op(v,n,up):
        out={}
        for s,c in v.items():
            for i in (set(range(n))-s if up else s):
                t=s|{i} if up else s-{i}
                out[t]=out.get(t,F(0))+c
        return {s:c for s,c in out.items() if c}
    def project(v,n,m):
        out={}
        d=v
        for j in range(m+1):
            term=d
            for _ in range(j):
                term=op(term,n,True)
            a=F((-1)**j,factorial(j)*factorial(j+1))
            for s,c in term.items():
                out[s]=out.get(s,F(0))+a*c
            d=op(d,n,False)
        return {s:c for s,c in out.items() if c}
    rows=[]
    for m in range(1,5):
        n=2*m
        basis=[frozenset(s) for s in combinations(range(n),m)]
        trace=F(0)
        for s in basis:
            v=project({s:F(1)},n,m)
            require(not op(v,n,False) and not op(v,n,True),"primitive projection")
            require(project(v,n,m)==v,"idempotence")
            trace+=v.get(s,0)
        require(trace==comb(n,m)-comb(n,m-1),"primitive rank")
        rows.append({"factors":n,"basis_size":len(basis),"primitive_rank":int(trace)})
    return {"scope":"Known algebraic cohomology of products of projective lines; no universal Hodge proof",
            "projector":"sum (-1)^j L^j D^j / (j! (j+1)!)","cases":rows}


def bsd():
    # Quadratic twists E_d: y²=x³-d²x, d positive squarefree.
    # Choose d=1 mod 8*product(p), so local reductions agree at every selected p.
    def squarefree(d):
        return all(d%(p*p) for p in range(2,isqrt(d)+1))
    def count(d,p):
        return 1+sum(1 for x in range(p) for y in range(p)
                     if (y*y-x**3+d*d*x)%p==0)
    rows=[]
    for primes in ((3,5),(3,5,7),(3,5,7,11)):
        M=8*prod(primes)
        d=next(1+M*k for k in range(1,1000) if squarefree(1+M*k))
        values=[]
        for p in primes:
            a=count(1,p); b=count(d,p)
            require(a==b and d%p==1,"local factor mismatch")
            values.append({"prime":p,"trace":p+1-a})
        require(d>1 and squarefree(d),"nontrivial squareclass")
        rows.append({"d":d,"modulus":M,"local_traces":values})
    return {"scope":"Finite good-prime trace indistinguishability of distinct twist squareclasses",
            "limitation":"No rank difference, analytic order difference or BSD counterexample is inferred.",
            "cases":rows}


def poincare():
    # Normalized width v'<=-1 between unit-spaced jumps.
    # Product P_j=(j+1)^a for integer a=1,2; weighted forcing sum 1/P_j.
    # a=1 diverges by dyadic grouping; a=2 converges by comparison to telescoping.
    rows=[]
    for k in range(1,9):
        first=2**(k-1); last=2**k-1
        harmonic=sum(F(1,j) for j in range(first,last+1))
        require(harmonic>=F(1,2),"dyadic lower bound")
        rows.append({"block":k,"harmonic_increment":str(harmonic)})
    squares=sum(F(1,j*j) for j in range(2,257))
    require(squares<1 and all(F(1,j*j)<F(1,j*(j-1)) for j in range(2,257)),"telescoping comparison")
    return {"scope":"Conditional scalar comparison model for surgery; not independent Ricci-flow reconstruction",
            "criterion":"Divergent accumulated inverse jump product forces eventual contradiction with nonnegative width.",
            "linear_product":"divergent","quadratic_product":"convergent","dyadic_controls":rows,
            "quadratic_partial_sum":str(squares)}


def run():
    return {"status":"SCOPED_DERIVATIONS_NOT_CERTIFIED","globally_proved":0,
            "rh":rh(),"p_vs_np":pnp(),"navier_stokes":ns(),"yang_mills":ym(),
            "hodge":hodge(),"bsd":bsd(),"poincare":poincare()}


if __name__=="__main__":
    print(json.dumps(run(),indent=2))
