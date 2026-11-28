"""Audit proof simulation and a representation-dependent obstruction escape."""
import argparse
import json
from pathlib import Path
from .pnp_proof_simulation import pad,verify_padding,simulation,verify_simulation,actual_width
from .pnp_expander_size import family,certify,verify as verify_expander
from .pnp_inference_obstructions import chain,balanced_proof
from .pnp_inference_complexity import budget
from .pnp_structural_kernel import Exhausted,normalize
from .pnp_outcome_engine import checkpoint
from .pnp_outcome_registry import decompose
from .pnp_unified_portfolio import fingerprint
from .pnp_evidence_benchmark import digest

SCHEMA="mathos-pnp-proof-simulation-frontier/1"
SIZES=(2,3,4,6,8)
CHAINS=(1,3,7,15,31,63)


def semantic_escape(s,odd):
    """The parity certificate justifies a constant decision, not a resolution step."""
    n,f,_=family(s,odd=odd)
    m,g=pad(n,f)
    verify_padding(n,f,g,budget())
    p=certify(s,odd=odd,b=budget())
    verify_expander(s,n,f,p,budget())
    return {"side":s,"odd":odd,"source_sha256":fingerprint(n,f),
            "padded_sha256":fingerprint(m,g),"source_variables":n,
            "padded_variables":m,"source_clauses":len(f),"padded_clauses":len(g),
            "parity_certificate":p,"constant_cnf":[[]] if odd else [],
            "inherited_width_lower":p["parameters"]["width_lower"],
            "inherited_size_exponent_ratio":p["parameters"]["size_exponent_ratio"],
            "scope":"padding restriction transfers ordinary resolution bounds; parity reduction is not resolution simulation"}


def verify_escape(r):
    s,o=r["side"],r["odd"]
    if type(o) is not bool:
        raise ValueError("invalid parity variant")
    n,f,_=family(s,odd=o)
    m,g=pad(n,f)
    verify_padding(n,f,g,budget())
    p=r["parity_certificate"]
    verify_expander(s,n,f,p,budget())
    if (p["odd"] is not o or r["source_sha256"]!=fingerprint(n,f) or
            r["padded_sha256"]!=fingerprint(m,g) or
            (r["source_variables"],r["padded_variables"],r["source_clauses"],r["padded_clauses"])!=(n,m,len(f),len(g)) or
            r["constant_cnf"]!=([[]] if o else []) or
            r["inherited_width_lower"]!=p["parameters"]["width_lower"] or
            r["inherited_size_exponent_ratio"]!=p["parameters"]["size_exponent_ratio"] or
            r["scope"]!="padding restriction transfers ordinary resolution bounds; parity reduction is not resolution simulation"):
        raise ValueError("escape provenance or decision mismatch")
    return True


def metrics(r):
    controls=r["controls"]
    return {"simulation_controls":len(controls),
            "source_inferences":sum(len(x["simulation"]["source_proof"]["steps"]) for x in controls),
            "lifted_inferences":sum(len(x["simulation"]["lifted"]["steps"]) for x in controls),
            "projection_inferences":sum(len(a["proof"]["steps"]) for x in controls for a in x["simulation"]["projections"]),
            "restriction_branches":2*len(controls),
            "parity_escapes":len(r["escapes"]),
            "inherited_odd_bounds":sum(x["odd"] for x in r["escapes"]),
            "positive_exponent_parameters":sum(x["odd"] and x["inherited_size_exponent_ratio"][0]>0 for x in r["escapes"]),
            "max_padded_variables":max((x["padded_variables"] for x in r["escapes"]),default=0)}


def run(*,checkpoint_path=None):
    r={"schema":SCHEMA,"controls":[],"escapes":[],"completion":"running",
       "objectives":[decompose(x) for x in ("E01","E02","E08","E09","E15")],
       "universal_obligation":"unresolved","p_equals_np_established":False,
       "p_not_equals_np_established":False,"novel_theorem_verified":False,
       "formal_verification":"abstract restriction and padding lemmas only; simulation and imported asymptotic proofs not fully formalized"}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        save()
        for n in CHAINS:
            f=chain(n)
            p=balanced_proof(n,budget())
            a=simulation(n,f,p,budget())
            verify_simulation(n,f,a,budget())
            r["controls"].append({"n":n,"simulation":a})
            save()
        for s in SIZES:
            for odd in (True,False):
                a=semantic_escape(s,odd)
                verify_escape(a)
                r["escapes"].append(a)
                save()
        r["completion"]="completed"
    except Exhausted as e:
        r["completion"],r["reason"]="resource_exhausted",str(e)
    except (ValueError,AssertionError) as e:
        r["completion"],r["reason"]="diagnostic_required",str(e)
    r["summary"]=metrics(r)
    save()
    return r


def audit(r):
    if (r["schema"]!=SCHEMA or r["completion"]!="completed" or
            digest(r["objectives"])!=digest([decompose(x) for x in ("E01","E02","E08","E09","E15")]) or
            r["universal_obligation"]!="unresolved" or
            any(r[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified")) or
            r["formal_verification"]!="abstract restriction and padding lemmas only; simulation and imported asymptotic proofs not fully formalized"):
        raise ValueError("report governance mismatch")
    if [x["n"] for x in r["controls"]]!=list(CHAINS) or [(x["side"],x["odd"]) for x in r["escapes"]]!=[(s,o) for s in SIZES for o in (True,False)]:
        raise ValueError("incomplete evaluation")
    for x in r["controls"]:
        n=x["n"]
        a=x["simulation"]
        verify_simulation(n,chain(n),a,budget())
        if digest(a["source_proof"])!=digest(balanced_proof(n,budget())):
            raise ValueError("source proof mismatch")
    for x in r["escapes"]:
        verify_escape(x)
    if r["summary"]!=metrics(r):
        raise ValueError("aggregate mismatch")
    return True


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--audit",type=Path)
    a=p.parse_args(argv)
    try:
        if a.audit:
            if a.audit.stat().st_size>32_000_000:
                raise ValueError("JSON exceeds 32 MB")
            audit(json.loads(a.audit.read_text(encoding="utf-8")))
            print(json.dumps({"status":"replayed","universal_obligation":"unresolved"}))
            return 0
        r=run(checkpoint_path=a.checkpoint)
        print(json.dumps(r,indent=2,sort_keys=True))
        return int(r["completion"]!="completed")
    except (OSError,ValueError,KeyError,TypeError,Exhausted) as e:
        p.error(str(e))


if __name__=="__main__":
    raise SystemExit(main())
