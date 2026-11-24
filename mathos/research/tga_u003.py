"""U003: persistent shifted Hankel witnesses and explicit Kummer orientation."""
from fractions import Fraction as F
from itertools import permutations
import json

# Gaussian rational arithmetic.
def add(z,w):return z[0]+w[0],z[1]+w[1]
def neg(z):return -z[0],-z[1]
def mul(z,w):return z[0]*w[0]-z[1]*w[1],z[0]*w[1]+z[1]*w[0]
def conj(z):return z[0],-z[1]
def inv(z):
    a,b=z;d=a*a+b*b
    return a/d,-b/d
def power(z,n):
    if n<0:z=inv(z);n=-n
    r=(F(1),F(0))
    while n:
        if n&1:r=mul(r,z)
        z=mul(z,z);n//=2
    return r
def real(x):return F(x),F(0)
def evaluate(p,z):
    s=real(0)
    for a in reversed(p):s=add(mul(s,z),real(a))
    return s

def shifted_witness():
    # Finite synthetic inverse roots; not zeta zeros.
    t=F(3,5),F(4,5)
    nodes=[real(2),real(1),t,conj(t),real(F(1,4))]
    rows=[]
    # q_n=(x-2)(x-1)(A+B*x), with q_n(t)=i*t^(-n).
    for n in range(2,33):
        z=mul(mul(add(t,real(-2)),add(t,real(-1))),real(1))
        u=mul(mul((F(0),F(1)),power(t,-n)),inv(z))
        B=u[1]/t[1];A=u[0]-B*t[0]
        q=[2*A,2*B-3*A,A-3*B,B]
        assert evaluate(q,t)==mul((F(0),F(1)),power(t,-n))
        assert evaluate(q,conj(t))==conj(evaluate(q,t))
        assert evaluate(q,real(2))==evaluate(q,real(1))==real(0)
        assert abs(A)<=F(7,4) and abs(B)<=F(5,4)
        assert abs(evaluate(q,nodes[-1])[0])<5
        def m(j):
            s=real(0)
            for x in nodes:s=add(s,power(x,j+1))
            assert s[1]==0
            return s[0]
        h=sum(a*b*m(2*n+i+j) for i,a in enumerate(q) for j,b in enumerate(q))
        tail=F(1,4)**(2*n+1)*evaluate(q,nodes[-1])[0]**2
        assert h== -F(6,5)+tail
        assert h< -1
        rows.append({"shift":2*n,"degree":3,"negative_form_lt":"-1"})
    # All-positive control: same formula gives nonnegative forms.
    p=[F(1),F(-2),F(1)]
    for n in range(10):
        assert sum(x**(2*n+1)*evaluate(p,real(x))[0]**2 for x in (F(2),F(1),F(1,4)))>=0
    return {"synthetic_shift_controls":rows,"positive_controls":10,
            "actual_zeta_zero_locations_used":False,"RH_proved":False}

def orientation():
    # Index of basis u_i tensor v_j is 2*i+j.
    # Ordinary tensor coefficients of eps_U12 eps_U34 eps_V13 eps_V24.
    def coeff(p,matching):
        a=[x//2 for x in p];b=[x%2 for x in p]
        return (a[1]-a[0])*(a[3]-a[2])*(b[matching[1]]-b[matching[0]])*(b[matching[3]]-b[matching[2]])
    def sign(p):return (-1)**sum(p[i]>p[j] for i in range(4) for j in range(i+1,4))
    values=[sign(p)*coeff(p,(0,2,1,3)) for p in permutations(range(4))]
    assert values.count(-1)==12 and values.count(0)==12
    assert sum(values)==-12
    assert sum(sign(p)*coeff(p,(0,1,2,3)) for p in permutations(range(4)))==0
    # Basis permutations yield corresponding sign of the antisymmetrized tensor.
    for p in permutations(range(4)):
        s=sum(sign(q)*coeff(tuple(p[i] for i in q),(0,2,1,3)) for q in permutations(range(4)))
        assert F(s,24)==-F(sign(p),2)
    return {"alternating_coefficient":"-1/2","permutation_checks":24*24,
            "nonzero_terms":12,"same_pairing_negative_control":True,
            "scope":"Kummer of product of two nonisogenous non-CM elliptic curves; proof in paper",
            "universal_hodge_proved":False}

def joint_gap():
    """All seven official targets, not the optional stronger BSD/reconstruction."""
    from mathos.research.tga_universal_bridges import graph, brute, transversals
    from mathos.proof_analysis.gap_analysis import Claim, analyze
    g=graph()
    g["RH.sparse_shift"]=Claim("For each fixed d, unbounded even shifts with PSD Hankel matrix","open")
    g["RH"]=Claim("RH by U003 persistent obstruction theorem","derived",(("RH.sparse_shift",),))
    g["ALL_CORE"]=Claim("All seven official targets","derived",
        (("RH","PNP","NS","HODGE","YM","BSD.core","POINCARE.external"),))
    r=analyze(g,"ALL_CORE")
    sets=[set(s) for s in r["minimal_completion_sets"]]
    assert {tuple(s) for s in r["minimal_completion_sets"]}==brute(g,"ALL_CORE")
    return {"status":r["status"],"completion_sets":r["minimal_completion_sets"],
            "minimal_blocking_sets":transversals(sets),
            "common_gaps":r["common_to_all_modeled_routes"],
            "model_only":True}

def run():
    return {"status":"RESEARCH_ONLY","promotion":"NONE","canonical_open_obligations":14,
            "rh":shifted_witness(),"hodge":orientation(),"all_core":joint_gap()}

if __name__=="__main__":print(json.dumps(run(),indent=2))
