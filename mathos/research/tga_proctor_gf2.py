"""PNP-F002 exact GF(2) finite controls and specialist formal replay."""
import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import re
import subprocess
from mathos.research.tga_agent import ROOT
from mathos.proof_analysis.gap_analysis import Claim,analyze
from scripts.millennium_docx import make_docx,verify

NAMES=("dot_add","row_replace","certificate_sound","elimination_step")
def digest(b):return hashlib.sha256(b).hexdigest()
def dot(a,x):return sum(v*w for v,w in zip(a,x))%2
def add(a,b):
    n=max(len(a),len(b))
    return tuple((a[i] if i<len(a) else 0)^(b[i] if i<len(b) else 0) for i in range(n))
def addrow(p,r):return add(p[0],r[0]),p[1]^r[1]
def sat(r,x):return dot(r[0],x)==r[1]
def head(a):return a[0] if a else 0
def reduced(p,rs):
    cleared=[addrow(p,r) if head(r[0]) else r for r in rs]
    assert all(not head(r[0]) for r in cleared)
    return [(a[1:],b) for a,b in cleared]
def controls():
    vectors=[v for n in range(5) for v in product((0,1),repeat=n)]
    linear=0
    for a,b,x in product(vectors,repeat=3):
        assert dot(add(a,b),x)==(dot(a,x)^dot(b,x));linear+=1
    rows=[(v,b) for v in product((0,1),repeat=3) for b in (0,1)]
    pivots=[r for r in rows if head(r[0])]
    tails=list(product((0,1),repeat=2))
    elim=cert=0
    for p,r,s,x in product(pivots,rows,rows,tails):
        rs=[r,s]
        old=any(all(sat(q,(b,)+x) for q in [p,*rs]) for b in (0,1))
        new=all(sat(q,x) for q in reduced(p,rs))
        assert old==new
        if new:
            b=p[1]^dot(p[0][1:],x)
            assert all(sat(q,(b,)+x) for q in [p,*rs])
        elim+=1
    for rs in product(rows,repeat=3):
        a,b=(0,0,0),0
        for row in rs:a,b=addrow((a,b),row)
        if not any(a) and b:
            assert not any(all(sat(r,x) for r in rs) for x in product((0,1),repeat=3))
            cert+=1
    return {"linearity_checks":linear,"pivot_tail_checks":elim,
            "contradictory_three_row_certificates":cert,
            "scope":"finite regression; formal proof is separate"}
def graph(projection,accepted):
    g={k:Claim(v,"established_external" if done else "open") for k,v,done in (
        ("projection","Kernel-checked disjoint projection",projection),
        ("row_calculus","Padded coefficient-list GF(2) semantics and row replacement",accepted),
        ("certificate_soundness","Soundness of row-subset contradiction",accepted),
        ("pivot_step","Constructive one-column elimination and back substitution",accepted),
        ("solver_iteration","Full pivot iteration, termination and certificate generation",False),
        ("implementation_refinement","Python bitmask and provenance correspondence",False),
        ("bit_cost","Formal polynomial total bit complexity",False))}
    g["scoped_solver"]=Claim("Formal B006 scoped solver","derived",(tuple(g),))
    r=analyze(g,"scoped_solver")
    return {"status":r["status"],"remaining":r["minimal_completion_sets"],
            "scope":"specialist formal reconstruction only"}
def check(src,out,lean,names,ns):
    out.mkdir()
    p=out/"Candidate.lean";p.write_text(src,encoding="utf-8")
    r=subprocess.run([lean,"-DwarningAsError=true",str(p)],capture_output=True,text=True,timeout=90)
    log=r.stdout+r.stderr
    (out/"kernel.txt").write_text(log,encoding="utf-8")
    audit={n:next((l for l in log.splitlines() if l.startswith("'"+ns+"."+n+"' ")),None) for n in names}
    ok=r.returncode==0 and all(audit[n]=="'"+ns+"."+n+"' does not depend on any axioms" for n in names)
    return {"accepted":ok,"exit_code":r.returncode,"source_sha256":digest(p.read_bytes()),
            "log_sha256":digest(log.encode()),"axioms":audit,"diagnostic":log[-6000:]}
def run(out,lean):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/"artifacts"):raise ValueError("output path")
    out.mkdir(parents=True,exist_ok=False)
    v=subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if v.returncode or not re.search(r"\bversion 4\.14\.0\b",v.stdout):raise RuntimeError("Lean 4.14.0 required")
    from mathos.research.tga_proctor_pnp import NAMES as prior_names
    prior=check((ROOT/"formal/ProctorPNPProjection.lean").read_text(),out/"projection",lean,prior_names,"ProctorPNP")
    src=(ROOT/"formal/ProctorGF2.lean").read_text()
    report={"status":"IN_PROGRESS","provider":"deterministic_specialist_replay","live_ai":False,
            "lean_version":v.stdout.strip(),"source_paper_sha256":digest((ROOT/"docs/research/breakthrough/PNP-B006.md").read_bytes()),
            "contract_source_sha256":digest(src.encode()),"projection":prior,
            "before":graph(prior["accepted"],False),"controls":controls(),
            "global_promotion":"NONE","canonical_open_obligations":14}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    r=check(src,out/"gf2",lean,NAMES,"ProctorGF2")
    report["formal"]=r
    accepted=prior["accepted"] and r["accepted"]
    report["status"]="KERNEL_VERIFIED_GF2_PIVOT_AND_CERTIFICATE" if accepted else "UNVERIFIED"
    report["after"]=graph(prior["accepted"],r["accepted"])
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    md=ROOT/"docs/research/tga-universal/PNP-F002.md"
    make_docx(md,out/"PNP-F002.docx");verify(md,out/"PNP-F002.docx")
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output-dir",required=True,type=Path);p.add_argument("--lean",default="lean")
    a=p.parse_args();r=run(a.output_dir,a.lean);print(json.dumps(r,indent=2))
    if r["status"]!="KERNEL_VERIFIED_GF2_PIVOT_AND_CERTIFICATE":raise SystemExit(1)
