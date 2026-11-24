"""Read-only training proctor: structure, scheduling and finite evidence replay, not grading."""
import argparse
import json
from pathlib import Path
from mathos.research import tga_agent as a

ROOT=a.ROOT
PLAN=ROOT/"curriculum/academy/proctor/tga-proctor-v1.json"

def curriculum():
    p=json.loads(PLAN.read_text())
    if p["course_id"]!="TGA-PROCTOR-501" or p["status"]!="CURRICULUM_PLAN_ONLY":
        raise ValueError("course identity/status")
    if p["automatic_completion"] is not False or p["external_validation_established"] is not False:
        raise ValueError("unsupported educational certification")
    if [w["week"] for w in p["weeks"]]!=list(range(1,13)):
        raise ValueError("week coverage")
    if any(not all(isinstance(w.get(k),str) and w[k].strip() for k in
                   ("title","outcome","lab","deliverable","boundary")) for w in p["weeks"]):
        raise ValueError("missing outcome or evidence")
    if [m["weeks"] for m in p["modules"]]!=[[i,i+1] for i in range(1,13,2)]:
        raise ValueError("module coverage")
    if any(m["points"]!=10 for m in p["modules"]) or sum(p["capstone"]["dimensions"].values())!=40:
        raise ValueError("rubric arithmetic")
    if set(t["track"] for t in p["tracks"])!={"Riemann","P versus NP","Navier–Stokes","Yang–Mills","Hodge","BSD","Poincaré"}:
        raise ValueError("specialization coverage")
    d=p["decision"]
    if (d["minimum_total"],d["minimum_module"],d["minimum_capstone"])!=(80,7,30) or d["software_awards_completion"] is not False or len(d["critical_gates"])!=5:
        raise ValueError("assessment policy")
    return {"course":p["course_id"],"weeks":12,"modules":6,"tracks":7,
            "assessment_points":100,"status":"CURRICULUM_PLAN_ONLY","completion_awarded":False}

def audit(state):
    """Cross-check recorded packets against current source and deterministic finite replay."""
    if state["version"]!=1 or state["global_promotion"]!="NONE" or state["independent_review"]!="NOT_PERFORMED_NONBLOCKING":
        raise ValueError("proof/review status")
    if state["source_sha256"]!=a.snapshot():raise ValueError("source hash mismatch")
    ai=state["ai_generated"]
    if type(ai) is not bool or state["provider"]!=("openai_responses" if ai else "offline_fixture"):
        raise ValueError("provider label")
    if not isinstance(state["model"],str) or (not ai and state["model"]!="none") or (ai and not state["model"]):
        raise ValueError("model label")
    hist=state["attempts"]
    if type(hist) is not list or len(hist)>1000:raise ValueError("history bound")
    _,focus=a.targets()
    baseline=a.run_exploration()
    calls=recorded=directed=0
    for i,item in enumerate(hist,1):
        claim=item["claim_id"]
        if item["id"]!=i or claim!=a.select(hist[:i-1]) or item["statement"]!=focus[claim]["statement"]:
            raise ValueError("attempt identity or schedule")
        if item["pivot_requested"]!=(sum(p["claim_id"]==claim for p in hist[:i-1])>=3):
            raise ValueError("pivot flag")
        n=item["calls_reserved"];roles=item["roles"]
        if type(n) is not int or not 0<=n<=4 or type(roles) is not dict or not len(roles)<=n<=len(roles)+1:
            raise ValueError("call accounting")
        if set(roles)!=set(list(a.ROLES)[:len(roles)]):raise ValueError("role order")
        for role,r in roles.items():a.validate(role,r)
        calls+=n
        status=item["status"]
        if status not in ("IN_PROGRESS","ATTEMPT_RECORDED","FAILED","INTERRUPTED"):
            raise ValueError("attempt status")
        if status=="IN_PROGRESS" and i!=len(hist):raise ValueError("orphan active attempt")
        if status=="ATTEMPT_RECORDED":
            if n!=4 or len(roles)!=4:raise ValueError("incomplete recorded attempt")
            expected=roles["synthesizer"]["disposition"] if ai and roles["adversary"]["verdict"]=="NO_OBVIOUS_FLAW" else "UNRESOLVED"
            if item["candidate_status"]!=expected:raise ValueError("candidate status inconsistent")
            replay=a.probe(claim,baseline,roles["adversary"]["check_request"])
            if item["probe"]!=replay:raise ValueError("finite evidence replay mismatch")
            recorded+=1
            directed+=int(replay["directed_check"]["executed"])
        elif item["candidate_status"] not in ("UNRESOLVED","SCOPED_CANDIDATE","PROOF_CANDIDATE","COUNTEREXAMPLE_CANDIDATE"):
            raise ValueError("invalid candidate label")
    if type(state["calls_reserved"]) is not int or state["calls_reserved"]!=calls:
        raise ValueError("total call mismatch")
    return {"status":"STRUCTURAL_REPLAY_CONSISTENT","attempts":len(hist),"recorded_packets_replayed":recorded,
            "directed_checks_replayed":directed,"reserved_calls":calls,
            "model_identity_authenticated":False,"formal_proof_verified":False,
            "learner_completion_awarded":False,"global_promotion":"NONE"}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checkpoint",type=Path)
    args=p.parse_args()
    result=curriculum()
    if args.checkpoint:
        try:
            if args.checkpoint.stat().st_size>32_000_000:raise ValueError("checkpoint too large")
            result["checkpoint_audit"]=audit(json.loads(args.checkpoint.read_text()))
        except (KeyError,TypeError,ValueError,OSError,RecursionError,AttributeError):
            p.exit(2,"Checkpoint rejected: malformed or inconsistent with pinned source/replay.\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":main()
