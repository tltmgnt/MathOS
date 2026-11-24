"""First breakthrough-focused cycle: scoped obstructions, not conjecture proofs."""
from fractions import Fraction as F
from cmath import exp, log
import json
from mathos.research.millennium_followup_20261124 import ns as base_ns
from mathos.research.breakthrough_focus import build_queue, intake, load


def ns():
    # Independent Fourier replay of the periodic seed; cutoff and concentration
    # are justified analytically in the note, not simulated here.
    seed = base_ns()
    if seed["mean_vorticity_stretching"] != "-1/4":
        raise ValueError("seed changed")
    # Unnormalized spatial integrals under u_lambda(x)=lambda*u(lambda*x):
    # energy, enstrophy, stretching and palinstrophy scale with these powers.
    powers = dict(energy=2-3,enstrophy=2*2-3,stretching=3*2-3,
                  palinstrophy=2*3-3)
    if powers != dict(energy=-1,enstrophy=1,stretching=3,palinstrophy=3):
        raise ValueError("scaling mismatch")
    # Normalize an abstract positive initial production to c=1 and E0=1;
    # algebraic controls only, not numerical PDE or actual cutoff integrals.
    cases=[]
    for l in (2,4,8,16,32):
        for alpha in (0,1,2):
            ratio=F(l**powers["stretching"],l**alpha)
            if ratio != l**(3-alpha):
                raise ValueError("ratio mismatch")
            cases.append(dict(scale=l,alpha=alpha,normalized_ratio=str(ratio)))
    return dict(seed_mean_stretching=seed["mean_vorticity_stretching"],
                scaling_powers=powers,algebraic_controls=len(cases),
                cases=cases,cutoff_integrals_numerically_measured=False,
                global_continuation_proved=False)


def primes(n):
    return [p for p in range(2,n+1) if all(p%d for d in range(2,int(p**.5)+1))]


def regularized_log(s,k,P):
    # Stable finite product: log det_k = -sum_p sum_{j>=k} p^(-j*s)/j.
    # 180 powers suffice for these particular bounded floating checks.
    return -sum(sum(p**(-j*s)/j for j in range(k,181)) for p in P)


def rh():
    P=primes(200)
    rows=[]
    for s,k in ((1.25+0.5j,1),(0.5+0.75j,3),(0.4+1j,4),(0.25+0.5j,5)):
        if k*s.real<=1:
            raise ValueError("outside proven Schatten domain")
        lk=regularized_log(s,k,P)
        lk1=regularized_log(s,k+1,P)
        correction=sum(p**(-k*s)/k for p in P)
        if abs(lk1-lk-correction)>1e-10:
            raise ValueError("telescoping correction mismatch")
        # Independent direct eigenvalue product.
        direct=1+0j
        for p in P:
            a=p**(-s)
            direct*=(1-a)*exp(sum(a**j/j for j in range(1,k)))
        if abs(direct-exp(lk))>1e-10:
            raise ValueError("product mismatch")
        # Compare log truncation from primes >50 to rigorous integer-tail bound.
        omitted=abs(lk-regularized_log(s,k,primes(50)))
        sigma=s.real
        bound=50**(1-k*sigma)/(k*(k*sigma-1)*(1-2**(-sigma)))
        if omitted>bound or abs(direct)==0:
            raise ValueError("finite tail/zero-free control")
        rows.append(dict(sigma=sigma,height=s.imag,order=k,finite_primes=len(P),
                         finite_determinant_abs=abs(direct),finite_tail_abs=omitted,
                         analytic_tail_upper=bound))
    return dict(cases=rows,finite_checks=3*len(rows),
                numerical_scope="finite float controls, not certified interval arithmetic",
                global_zero_identity_proved=False)


def run():
    q=build_queue(load("docs/research/BREAKTHROUGH_FOCUS.v1.json"),
                  load("docs/proof-analysis/OBLIGATIONS.v1.json"),
                  load("docs/research/CLAY_PROOF_ROUTES.v1.json"))
    results={}
    for cid,short,fn in (("NS.critical_bound","NS-B001",ns),("RH.zero_identity","RH-B001",rh)):
        path=f"docs/research/breakthrough/{short}.candidate.json"
        results[short]={"intake":intake(load(path),q),"controls":fn()}
    return {"status":"RESEARCH_ONLY","promotion":"NONE","open_obligations":14,
            "cycle":1,"results":results}


if __name__=="__main__":
    print(json.dumps(run(),indent=2))
