"""TGA of derived implications; no canonical proof promotion."""
from itertools import combinations,product
from fractions import Fraction as F
import json
from mathos.proof_analysis.gap_analysis import Claim,analyze

def graph():
    g={}
    def leaf(k,label):g[k]=Claim(label,"open")
    def node(k,label,*routes):g[k]=Claim(label,"derived",tuple(tuple(r) for r in routes))
    for k,label in {
        "RH.all_hankel":"For every d both xi-log-derivative Hankel matrices are PSD",
        "PNP.poly_sat":"One correct uniform deterministic polynomial-bit-time 3-SAT algorithm",
        "PNP.separation":"An unrestricted lower bound for every polynomial-time algorithm for a language in NP",
        "NS.A.critical":"Universal critical L4 L6 bound for official R3 data",
        "NS.B.critical":"Universal critical L4 L6 bound for official periodic data",
        "NS.C.breakdown":"Official forced R3 breakdown",
        "NS.D.breakdown":"Official forced periodic breakdown",
        "HODGE.primitive":"All primitive rational Hodge classes on every smooth projective variety algebraic",
        "YM.continuum":"Nontrivial continuum construction for each required group",
        "YM.os":"Axioms, positive reconstruction and dense physical family for each group",
        "YM.uniform_dense_decay":"Uniform physical-rate correlation estimates on that dense family and convergence",
        "BSD.p5_comparison":"Analytic order equals 5-power Selmer corank for every E/Q",
        "BSD.p5_finite":"5-primary Sha finite for every E/Q",
        "BSD.full_annihilator":"For every E some nonzero integer annihilates full Sha",
        "BSD.leading_formula":"Refined leading-term formula with specified normalizations",
        "POINCARE.reconstruction":"Complete project proof reconstruction",
    }.items():leaf(k,label)
    node("RH","RH via Stieltjes criterion",("RH.all_hankel",))
    node("PNP","P vs NP",("PNP.poly_sat",),("PNP.separation",))
    node("NS","Official alternative",("NS.A.critical",),("NS.B.critical",),("NS.C.breakdown",),("NS.D.breakdown",))
    node("HODGE","Rational Hodge via primitive decomposition",("HODGE.primitive",))
    node("YM","Continuum and mass gap",("YM.continuum","YM.os","YM.uniform_dense_decay"))
    node("BSD.core","Rank equality via 5-primary route",("BSD.p5_comparison","BSD.p5_finite"))
    node("BSD.refined","Stronger full formula",("BSD.core","BSD.full_annihilator","BSD.leading_formula"))
    g["POINCARE.external"]=Claim("Published theorem, external","established_external")
    node("POINCARE.project","MathOS reconstruction",("POINCARE.reconstruction",))
    return g

TARGETS=("RH","PNP","NS","HODGE","YM","BSD.core","BSD.refined","POINCARE.external","POINCARE.project")

def subsets(xs):
    for k in range(len(xs)+1):
        yield from map(frozenset,combinations(xs,k))

def brute(g,target):
    def reachable(k):
        c=g[k]
        return {k} if c.state=="open" else set().union(*(reachable(d) for r in c.routes for d in r))
    leaves=sorted(reachable(target));out=[]
    def value(k,s):
        c=g[k]
        if c.state=="open":return k in s
        if c.state=="established_external":return True
        return any(all(value(d,s) for d in r) for r in c.routes)
    for s in subsets(leaves):
        if not any(t<=s for t in out) and value(target,s):out.append(s)
    return {tuple(sorted(s)) for s in out}

def transversals(sets):
    if not sets:return []
    all_leaves=sorted(set().union(*sets));out=[]
    for s in subsets(all_leaves):
        if not any(t<=s for t in out) and all(s&t for t in sets):out.append(s)
    return [sorted(s) for s in out]

def det(a):
    a=[list(map(F,r)) for r in a];v=F(1)
    for j in range(len(a)):
        k=next((k for k in range(j,len(a)) if a[k][j]),None)
        if k is None:return F(0)
        if k!=j:a[j],a[k]=a[k],a[j];v=-v
        p=a[j][j];v*=p
        for k in range(j+1,len(a)):
            f=a[k][j]/p
            for l in range(j+1,len(a)):a[k][l]-=f*a[j][l]
            a[k][j]=F(0)
    return v

def hankel_counterexample(d):
    t=[F(1,j) for j in range(1,d+2)]
    e=F(1,2)
    def m(n):return sum(x**(n+1) for x in t)+(-e)**(n+1)
    while not all(det([[m(i+j+s) for j in range(k)] for i in range(k)])>0
                  for s in (0,1) for k in range(1,d+2)):
        e/=2
    q=[F(1)]
    for x in t:
        v=[F(0)]*(len(q)+1)
        for i,c in enumerate(q):v[i]-=x*c;v[i+1]+=c
        q=v
    v=sum(a*b*m(i+j) for i,a in enumerate(q) for j,b in enumerate(q))
    assert v==-e*product_value([(-e-x)**2 for x in t])<0
    return {"largest_tested_order":d,"epsilon":str(e),"negative_root":str(-1/e),
            "witness_degree":len(q)-1,"negative_quadratic_form":str(v)}

def product_value(xs):
    v=F(1)
    for x in xs:v*=x
    return v

def run():
    g=graph();targets={}
    for k in TARGETS:
        r=analyze(g,k);sets=[set(s) for s in r["minimal_completion_sets"]]
        assert {tuple(s) for s in r["minimal_completion_sets"]}==brute(g,k)
        targets[k]={"status":r["status"],"minimal_completion_sets":r["minimal_completion_sets"],
                    "minimal_blocking_sets":transversals(sets)}
    return {"status":"RESEARCH_ONLY","canonical_open_obligations":14,"promotion":"NONE",
            "universal_solutions_claimed":False,"derived_routes":targets,
            "finite_hankel_counterexamples":[hankel_counterexample(d) for d in range(6)]}

if __name__=="__main__":print(json.dumps(run(),indent=2))
