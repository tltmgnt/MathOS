"""Unified Proctor 601 theorem laboratory (bounded Boolean language, no global promotion)."""
import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import re
import subprocess
from mathos.research import tga_agent as agent
from mathos.research import tga_proctor as proctor
from mathos.research.tga_proctor_advanced import canonical

def digest(data):
    return hashlib.sha256(data).hexdigest()

def validate(formula,n):
    count=0
    def visit(x,depth):
        nonlocal count
        count+=1
        if count>64 or depth>16:raise ValueError("formula bound")
        if type(x) is bool:return
        if type(x) is int and 0<=x<n:return
        if type(x) is not list or not x:raise ValueError("formula syntax")
        if x[0]=="not" and len(x)==2:visit(x[1],depth+1)
        elif x[0] in ("and","or") and len(x)==3:
            visit(x[1],depth+1);visit(x[2],depth+1)
        else:raise ValueError("operator")
    visit(formula,0)

def evaluate(x,bits):
    if type(x) is bool:return x
    if type(x) is int:return bits[x]
    if x[0]=="not":return not evaluate(x[1],bits)
    if x[0]=="and":return evaluate(x[1],bits) and evaluate(x[2],bits)
    return evaluate(x[1],bits) or evaluate(x[2],bits)

def render(x):
    if type(x) is bool:return "true" if x else "false"
    if type(x) is int:return "v"+str(x)
    if x[0]=="not":return "(!"+render(x[1])+")"
    return "("+render(x[1])+(" && " if x[0]=="and" else " || ")+render(x[2])+")"

def analyze_candidate(p):
    if type(p) is not dict or set(p)!={"attempt_id","variables","left","right"}:
        raise ValueError("candidate fields")
    n=p["variables"]
    if type(n) is not int or not 1<=n<=4 or type(p["attempt_id"]) is not int or p["attempt_id"]<1:
        raise ValueError("candidate bounds")
    for x in (p["left"],p["right"]):validate(x,n)
    rows=[]
    for bits in product((False,True),repeat=n):
        l,r=evaluate(p["left"],bits),evaluate(p["right"],bits)
        rows.append({"assignment":list(bits),"left":l,"right":r})
    counter=next((row for row in rows if row["left"]!=row["right"]),None)
    return {"equivalent":counter is None,"assignments_checked":len(rows),
            "counterexample":counter,"rows":rows}

def source(p):
    analyze_candidate(p) # validates grammar, not a trust claim
    vs=["v"+str(i) for i in range(p["variables"])]
    return ("namespace Proctor601Unified\n"
        "theorem candidate ("+" ".join(vs)+" : Bool) :\n    "+
        render(p["left"])+" = "+render(p["right"])+" := by\n  "+
        " <;> ".join(["cases "+v for v in vs]+["rfl"])+
        "\nend Proctor601Unified\n#print axioms Proctor601Unified.candidate\n")

def kernel(p,lean,out):
    """Only internally generated source from the validated grammar reaches Lean."""
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    src=out/"Candidate.lean";src.write_text(source(p),encoding="utf-8")
    # A trusted, operator-selected executable; never model-selected.
    v=subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if v.returncode or not re.search(r"\bversion 4\.14\.0\b",v.stdout):
        raise RuntimeError("pinned Lean 4.14.0 required")
    run=subprocess.run([lean,"-DwarningAsError=true",str(src.resolve())],
                       capture_output=True,text=True,timeout=60)
    log=run.stdout+run.stderr
    (out/"kernel.txt").write_text(log,encoding="utf-8")
    (out/"version.txt").write_text(v.stdout,encoding="utf-8")
    verified=run.returncode==0 and "'Proctor601Unified.candidate' does not depend on any axioms" in log
    return {"verified":verified,"exit_code":run.returncode,"source_sha256":digest(src.read_bytes()),
            "log_sha256":digest(log.encode()),"version":v.stdout.strip(),
            "scope":"universal equality of supplied Boolean expressions, at most four variables"}

DEMO={"attempt_id":1,"variables":3,
      "left":["or",["and",0,1],2],
      "right":["and",["or",0,2],["or",1,2]]}

def run(checkpoint,p,out,lean=None):
    out=Path(out).resolve()
    if out.is_relative_to(agent.ROOT) and not out.is_relative_to(agent.ROOT/"artifacts"):
        raise ValueError("output in repository must be under artifacts")
    out.mkdir(parents=True,exist_ok=True)
    # Proctor validates checkpoint before any candidate evaluation.
    state=json.loads(Path(checkpoint).read_text(encoding="utf-8"))
    audit=proctor.audit(state)
    check=analyze_candidate(p)
    i=p["attempt_id"]
    if i>len(state["attempts"]) or state["attempts"][i-1]["status"]!="ATTEMPT_RECORDED":
        raise ValueError("candidate needs a recorded attempt reference")
    record=state["attempts"][i-1]
    report={"course":"TGA-PROCTOR-601","status":"COUNTEREXAMPLE" if not check["equivalent"] else "FINITE_CHECK_ONLY",
            "candidate":p,"candidate_sha256":digest(canonical(p)),
            "checkpoint_sha256":digest(canonical(state)),
            "referenced_attempt":i,"attempt_sha256":digest(canonical(record)),
            "origin":"OPERATOR_SUPPLIED_TRAINING_CANDIDATE_NOT_MODEL_GENERATED",
            "proctor_audit":audit,"exact_evidence":check,
            "formal":None,"scope":"Boolean identity training only; attempt link is provenance, not proof of its research claim",
            "global_promotion":"NONE","learner_completion_awarded":False}
    if check["equivalent"] and lean is not None:
        report["formal"]=kernel(p,lean,out)
        report["status"]="KERNEL_VERIFIED_SCOPED_THEOREM" if report["formal"]["verified"] else "KERNEL_REJECTED_OR_UNVERIFIED"
    (out/"theorem-report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checkpoint",type=Path,required=True)
    p.add_argument("--candidate",type=Path,help="bounded Boolean JSON; omit for training identity")
    p.add_argument("--output-dir",type=Path,default=agent.ROOT/"artifacts/proctor601-unified")
    p.add_argument("--lean",help="operator-selected Lean 4.14.0 executable; omitted means no kernel run")
    a=p.parse_args()
    if a.candidate and a.candidate.stat().st_size>10000:raise ValueError("candidate size")
    c=json.loads(a.candidate.read_text()) if a.candidate else DEMO
    r=run(a.checkpoint,c,a.output_dir,a.lean)
    print(json.dumps(r,indent=2))
    if r["status"]=="KERNEL_REJECTED_OR_UNVERIFIED":raise SystemExit(1)

if __name__=="__main__":main()
