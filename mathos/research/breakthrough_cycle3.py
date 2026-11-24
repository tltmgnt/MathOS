"""Cycle 3: momentum moment obstruction and Weil coupling obstruction."""
from fractions import Fraction as F
import json
from mathos.research.breakthrough_focus import build_queue, intake, load


def ns():
    # If a compact self-similar profile solves the projected momentum equation,
    # its vorticity obeys an elliptic equation with analytic coefficients.
    # This replay checks scaling and the exterior potential constraint only.
    rows=[]
    for n in range(1,9):
        # lambda'=a lambda^3: time derivative of lambda^n has power n+2.
        rows.append({"profile_power":n,"time_derivative_power":n+2})
    # A divergence-free compact F solving the profile equation has pressure
    # gradient zero outside support. Then integral of F_i F_j is isotropic.
    # Example trace-free quadratic harmonic tests of a symmetric matrix.
    cases=[]
    for diag in ((1,1,1),(2,1,1),(2,3,4),(7,7,7)):
        a,b,c=diag
        moments=(a-b,b-c)
        assert (moments==(0,0))==(a==b==c)
        cases.append({"diagonal":diag,"harmonic_moments":moments})
    return {"scaling_checks":len(rows),"moment_checks":len(cases),
            "moment_examples":cases,"pde_solution_established":False,
            "compact_profile_exclusion":"analytic unique continuation (external theorem)"}


def rh():
    # Two exact rational bounding certificates for prime-power coupling.
    # c1=log(2)/sqrt(2)> 2/5 (log2> 2/3; sqrt2<3/2).
    # c2=log(2)/2>1/3. c3=log(2)/(2sqrt2)>2/9.
    # For 4 equally spaced windows the row-sum of absolute prime couplings
    # already exceeds the cycle-2 guaranteed local lower bound.
    L=F(1,1024)
    # all separations r >= log2-L >1/2, <=3log2+L< 3.
    # arch kernel <2, pole kernel <6 (2cosh(3/2)<6).
    err=8*L
    bounds=[F(2,5)-err,F(1,3)-err,F(2,9)-err]
    assert all(x>0 for x in bounds)
    row_lower=2*bounds[0]+bounds[1]
    assert row_lower>F(317,768)
    # Constant-vector Rayleigh lower bound on magnitude of off-diagonal
    # matrix for four translates, normalized by 4.
    rayleigh=F(2,4)*sum((4-j)*b for j,b in enumerate(bounds,1))
    assert rayleigh>F(317,768)
    # Prime-shift isolation: interval around 2^j, j<=3, nearest integer
    # log-distance >= log(1+1/8)>1/9>L.
    assert F(1,9)>L
    return {"window_count":4,"support_length":str(L),
            "cross_abs_lower_bounds":[str(x) for x in bounds],
            "interior_row_lower":str(row_lower),
            "constant_vector_rayleigh_lower":str(rayleigh),
            "prior_local_floor":"317/768",
            "global_positivity_proved":False,
            "scope":"obstruction to fixed-floor triangle-inequality certificate, not to actual normalized block positivity"}


def run():
    q=build_queue(load("docs/research/BREAKTHROUGH_FOCUS.v1.json"),
                  load("docs/proof-analysis/OBLIGATIONS.v1.json"),
                  load("docs/research/CLAY_PROOF_ROUTES.v1.json"))
    return {"status":"RESEARCH_ONLY","promotion":"NONE","cycle":3,"open_obligations":14,
            "results":{short:{"intake":intake(load(f"docs/research/breakthrough/{short}.candidate.json"),q),
                              "controls":fn()} for short,fn in (("NS-B003",ns),("RH-B003",rh))}}


if __name__=="__main__": print(json.dumps(run(),indent=2))
