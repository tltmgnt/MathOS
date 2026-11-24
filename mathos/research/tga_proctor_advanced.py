"""Proctor 601 advanced labs; scoped evidence, not certification or grading."""
import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path
from fractions import Fraction as F
from mathos.research import tga_agent as agent
from mathos.proof_analysis.gap_analysis import Claim,analyze

ROOT=agent.ROOT
MODULES=(
 ("M1","Scope and route graph","Rebuild (A AND B) OR C and explain the quantifiers."),
 ("M2","Proof and falsification","Find a negative Hankel direction and repair the universal inference."),
 ("M3","AI and computation","Recompute an exact determinant and challenge a role's unsupported claim."),
 ("M4","Provenance and operations","Replay a checkpoint, change a copy, and explain the trust boundary."),
 ("M5","Specialization and formal proof","Run the pinned Lean lab, inspect theorem statements and dependencies."),
 ("M6","Dossier and conduct","Produce an evidence manifest, disclose AI usage, and defend scope."),
)
CAP=("oral_scope","practical_replay","adversarial_mathematics","dossier_and_defense")
TRACKS=("RH","PNP","NS","YM","HODGE","BSD","POINCARE")

def remediation(scores,capstone,integrity):
    """Deterministic practice recommendations using manually supplied rubric points."""
    if set(scores)!={m[0] for m in MODULES} or set(capstone)!=set(CAP):
        raise ValueError("rubric keys")
    if any(type(x) is not int or not 0<=x<=10 for x in [*scores.values(),*capstone.values()]) or type(integrity) is not bool:
        raise ValueError("rubric range")
    total=sum(scores.values())+sum(capstone.values())
    work=[{"module":k,"score":scores[k],"topic":topic,"exercise":task}
          for k,topic,task in MODULES if scores[k]<7]
    work.sort(key=lambda x:(x["score"],x["module"]))
    capwork=[k for k in CAP if capstone[k]<8]
    if sum(capstone.values())<30:
        capwork=capwork or list(CAP)
    if total<80 and not work and not capwork:
        k=min(scores,key=scores.get)
        work=[{"module":k,"score":scores[k],"topic":"Overall threshold","exercise":next(m[2] for m in MODULES if m[0]==k)}]
    return {"status":"PRACTICE_GUIDANCE_ONLY","total":total,
            "capstone_total":sum(capstone.values()),"module_remediation":work,
            "capstone_review":capwork if total<80 or sum(capstone.values())<30 else [],
            "integrity_hold":not integrity,
            "threshold_met":integrity and total>=80 and min(scores.values())>=7 and sum(capstone.values())>=30,
            "completion_awarded":False,"requires_human_assessment":True}

def dynamic_graph():
    """Versioned hypothetical extension: no status writes to research graph."""
    g={"a":Claim("Assumption A","open"),"b":Claim("Assumption B","open"),
       "c":Claim("Alternative C","open"),"target":Claim("Toy target","derived",(("a","b"),("c",)))}
    before=analyze(g,"target")
    # Refine one leaf through a documented hypothetical sufficient route.
    v=dict(g);v["d"]=Claim("New lemma D","open");v["e"]=Claim("New lemma E","open")
    v["a"]=Claim("A, hypothetically reduced","derived",(("d","e"),))
    after=analyze(v,"target")
    bad=dict(v);bad["d"]=Claim("Circular D","derived",(("target",),))
    try:analyze(bad,"target")
    except ValueError:cycle_rejected=True
    else:raise AssertionError("cycle not rejected")
    assert before["minimal_completion_sets"]==[["c"],["a","b"]]
    assert after["minimal_completion_sets"]==[["c"],["b","d","e"]]
    return {"scope":"HYPOTHETICAL_TRAINING_GRAPH","version_1":before["minimal_completion_sets"],
            "version_2":after["minimal_completion_sets"],"cycle_rejected":cycle_rejected,
            "canonical_graph_modified":False}

def labs():
    # All data are intentionally small and independently checkable.
    r=agent.check_request('{"kind":"hankel_quadratic","moments":["1","0","-1"],"q":["0","1"]}')
    assert r["result"]["value"]=="-1"
    p=agent.check_request('{"kind":"cnf","variables":1,"clauses":[[1],[-1]]}')
    assert not p["result"]["satisfiable"]
    # Scaling NS: f(t)=A exp(-nu t); use exact ratio of squared amplitudes
    # at two selected samples only, no PDE calculation.
    ns=F(1,2)**2;assert ns==F(1,4)
    # Eigenvalues 1, (1-q)/(1+q); gap ratio difference tends to zero.
    ym=[str(1-(1-F(1,2**n))/(1+F(1,2**n))) for n in (1,2,3,4)]
    assert ym==["2/3","2/5","2/9","2/17"]
    h=agent.check_request('{"kind":"determinant","matrix":[["2","1"],["1","2"]]}')
    assert h["result"]["value"]=="3"
    # Abstract direct sum of Z/p: element supported at a prime not dividing N.
    bsd=[]
    for N,p0 in ((6,5),(30,7),(210,11)):
        assert N%p0
        bsd.append({"candidate_annihilator":N,"prime":p0,"nonzero_residue":N%p0})
    # Two abstract truth values are not a topology counterexample.
    assert True and not all([True,False])
    return {"RH":{"result":r["result"],"scope":"synthetic moments"},
            "PNP":{"result":p["result"],"scope":"one finite CNF"},
            "NS":{"squared_amplitude_ratio":str(ns),"scope":"scalar scaling, not PDE"},
            "YM":{"one_minus_ratio":ym,"scope":"toy regulated matrices"},
            "HODGE":{"result":h["result"],"scope":"abstract pairing matrix, not a cycle"},
            "BSD":{"controls":bsd,"scope":"abstract torsion group, not Sha of a curve"},
            "POINCARE":{"hypothesis_missing":True,"scope":"propositional control, not manifold classification"}}

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()

def seal(entries,key):
    """HMAC chain with external key; not independent identity or timestamp proof."""
    if not isinstance(key,bytes) or len(key)<32:raise ValueError("key must contain >=32 bytes")
    if not isinstance(entries,list) or len(entries)>1000:raise ValueError("entry bound")
    prev="0"*64;rows=[]
    for i,payload in enumerate(entries,1):
        if not isinstance(payload,dict) or len(canonical(payload))>100000:raise ValueError("payload bound")
        row={"sequence":i,"previous":prev,"payload":payload}
        tag=hmac.new(key,canonical(row),hashlib.sha256).hexdigest()
        row["tag"]=tag;rows.append(row);prev=tag
    return {"version":1,"entries":rows,"head":prev,"count":len(rows)}

def verify_ledger(ledger,key,expected_head,expected_count):
    """Expected head/count must be retained outside the ledger by its operator."""
    try:
        if type(expected_count) is not int or type(expected_head) is not str:return False
        if ledger["version"]!=1 or ledger["count"]!=expected_count or ledger["head"]!=expected_head:return False
        replay=seal([row["payload"] for row in ledger["entries"]],key)
        return hmac.compare_digest(canonical(ledger),canonical(replay)) and hmac.compare_digest(replay["head"],expected_head)
    except (KeyError,TypeError,ValueError,AttributeError):return False

def plan():
    return {"course":"TGA-PROCTOR-601","status":"IMPLEMENTATION_LABS_ONLY",
            "labs":labs(),"graph":dynamic_graph(),"formal_kernel_verified":False,
            "live_ai_validated":False,"learner_outcomes_measured":False,
            "external_validation_established":False,"global_promotion":"NONE",
            "quality_rating":"NOT_EXTERNALLY_ESTABLISHED"}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--assessment",type=Path,help="private rubric JSON: scores, capstone, integrity")
    args=p.parse_args()
    r=plan() if not args.assessment else remediation(**json.loads(args.assessment.read_text()))
    print(json.dumps(r,indent=2))

if __name__=="__main__":main()
