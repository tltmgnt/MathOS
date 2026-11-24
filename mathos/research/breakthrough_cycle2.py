"""Cycle 2: scalar-balance obstruction and localized Weil coercivity.

Exact rational arithmetic checks selected algebraic steps; not a PDE simulation,
formal proof checker, zeta-zero computation, or global proof.
"""
from fractions import Fraction as F
import json
from mathos.research.breakthrough_focus import build_queue, intake, load


def ns():
    # Symbolic scaling constants are instantiated with positive rational
    # examples. These are not measurements of the localized seed.
    rows=[]
    for K,E,D,S,nu in [(2,3,5,7,1),(3,4,8,2,2),(1,5,9,3,F(1,2))]:
        K,E,D,S,nu=map(F,(K,E,D,S,nu))
        b=nu*(D+E*E/K)/S
        K,E,D,S=b*b*K,b*b*E,b*b*D,b**3*S
        a=2*nu*E/K
        assert S-nu*D==nu*E*E/K
        T=1/(2*a)
        for lam in (F(1),F(2),F(4),F(8),F(16)):
            t=T*(1-1/(lam*lam))
            lp=a*lam**3
            energy=K/lam
            enstrophy=E*lam
            int_E=E/a*(1-1/lam)
            assert -K*lp/lam**2==-2*nu*enstrophy
            assert E*lp==2*(S-nu*D)*lam**3
            assert energy+2*nu*int_E==K
            assert (T-t)*lam*lam==T
            rows.append(dict(scale=int(lam),t_over_T=str(t/T),
                             energy_over_K=str(energy/K),enstrophy_over_E=str(enstrophy/E)))
    return dict(balance_cases=len(rows),rows=rows,
                critical_integral="constant * log(lambda/lambda0), diverges",
                exact_scalar_balance_path=True,navier_stokes_solution_established=False)


def rh():
    # Re psi(1/4+128i) - psi(1/4) > 7, via a positive finite partial sum.
    y=F(128); x=[F(n)+F(1,4) for n in range(64)]
    partial=sum(y*y/(z*(z*z+y*y)) for z in x)
    assert partial>7
    L=F(1,1024); T=256
    # w(t)>-6 everywhere and >1 for |t|>=256.
    # Fraction in low band <= T*L/pi < T*L/3.
    # Pole magnitude <=4L ||f||^2.
    lower=1-7*T*L/3-4*L
    assert lower>F(2,5)
    # A copy translated by log 2 has one prime-shift coupling;
    # smooth off-diagonal remainder <=6L ||f||^2.
    cross_upper=-F(1,4)+6*L
    assert cross_upper<0
    # Exact 2x2 Schur controls: positive diagonals not enough.
    controls=[]
    for a,b,c in [(1,1,0),(1,1,1),(1,1,2),(2,8,4),(2,8,5)]:
        det=a*b-c*c
        assert (det>=0)==(c*c<=a*b)
        controls.append(dict(a=a,b=b,c=c,determinant=det,psd=det>=0))
    return dict(digamma_partial_terms=64,partial_gt_7=True,
                local_length=str(L),coercivity_lower=str(lower),
                reported_floor="2/5",cross_upper=str(cross_upper),
                schur_controls=controls,global_weil_positivity_proved=False)


def run():
    q=build_queue(load("docs/research/BREAKTHROUGH_FOCUS.v1.json"),
                  load("docs/proof-analysis/OBLIGATIONS.v1.json"),
                  load("docs/research/CLAY_PROOF_ROUTES.v1.json"))
    results={}
    for short,fn in (("NS-B002",ns),("RH-B002",rh)):
        results[short]={"intake":intake(load(f"docs/research/breakthrough/{short}.candidate.json"),q),
                        "controls":fn()}
    return dict(status="RESEARCH_ONLY",promotion="NONE",open_obligations=14,cycle=2,results=results)


if __name__=="__main__":
    print(json.dumps(run(),indent=2))
