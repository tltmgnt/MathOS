import argparse
import json
from itertools import product
from pathlib import Path
import re
import subprocess
from mathos.research.tga_proctor_gf2_codec import NAMES as CODEC_NAMES
from mathos.research.tga_proctor_pnp_encoding import ROOT,NAMES as MASK_NAMES,DOMAIN_NAMES
from mathos.research.tga_proctor_gf2_checker import NAMES as CHECK_NAMES
from mathos.research.tga_proctor_gf2_certificate import NAMES as CERT_NAMES
from mathos.research.tga_proctor_gf2_solver import NAMES as SOLVER_NAMES,certificate_solver,verify_result
from mathos.research.tga_proctor_gf2 import NAMES as GF_NAMES,digest,check
from mathos.research.tga_proctor_pnp import NAMES as PNP_NAMES
from scripts.millennium_docx import make_docx,verify
from mathos.research.tga_proctor_gf2_highest import NAMES as HIGHEST_NAMES,trace,controls as prior_controls
from mathos.research.tga_proctor_gf2_global import NAMES as GLOBAL_NAMES,fixtures
NAMES=("xor_width","insertCount","feedCount","backCount","costSolve","occupied_bound","payload_bound","bitCharge_bound","costSolve_bound","costOutput_spec")
def mirror(n,rows):
    # Dense slot count, same branch schedule as costSolve.
    slots={};v=c=k=0
    for j,(a,b) in enumerate(rows):
        k+=1;w=1<<j
        for p in range(n-1,-1,-1):
            v+=1
            if a<1<<p:continue
            if p not in slots:
                slots[p]=(a,b,w);break
            u,z,t=slots[p];a,b,w=a^u,b^z,w^t;c+=1
        else:
            v+=1
            assert a==0
            if b:return (False,w),(v,c,k,0,0)
    x=0
    for p,(a,b,_) in sorted(slots.items()):
        if (a&x).bit_count()%2!=b:x^=1<<p
    return (True,x),(v,c,k,n,len(slots))
def charge(n,m,counts):
    v,c,k,b,d=counts
    return (4*v+2*c+4*k+2*b+6*d+2*n+2*m+1)*(n+m+1)
def polynomial(n,m):
    return charge(n,m,(m*(n+1),m*n,m,n,n))
def controls():
    d=fixtures();max_charge=0;visits=collisions=0
    for n,rs,yes,value in d:
        ans,ct=mirror(n,rs)
        assert ans==(yes,value)
        v,c,k,b,e=ct;m=len(rs)
        assert v<=m*(n+1) and c<=m*n and k<=m and b<=n and e<=n
        assert value<1<<(n if yes else m)
        assert charge(n,m,ct)<=polynomial(n,m)
        visits+=v;collisions+=c;max_charge=max(max_charge,charge(n,m,ct))
    return {"systems":len(d),"slot_visits":visits,"collisions":collisions,"maximum_model_charge":max_charge,
        "scope":"finite exact mirror counts; no measured runtime"}
def eval_source(data):
    def expr(d):
        n,rows,yes,value=d
        rs="["+",".join("("+str(a)+","+("true" if b else "false")+")" for a,b in rows)+"]"
        proof="True.intro"
        for _ in rows:proof="⟨by decide,"+proof+"⟩"
        _,ct=mirror(n,rows)
        counts="("+",".join(map(str,ct))+")"
        return "(ProctorGF2.costOutput "+str(n)+" "+rs+" ("+proof+") == (("+("true" if yes else "false")+","+str(value)+"),"+counts+"))"
    return "\n".join("#eval (["+ ",\n".join(expr(d) for d in data[i:i+32])+"].all id)" for i in range(0,len(data),32))+"\n"
def run(out,lean):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/"artifacts"):raise ValueError("output path")
    out.mkdir(parents=True,exist_ok=False)
    v=subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if v.returncode or not re.search(r"\bversion 4\.14\.0\b",v.stdout):raise RuntimeError("Lean 4.14.0 required")
    paths=[ROOT/"formal"/n for n in ("ProctorGF2.lean","ProctorGF2Solver.lean","ProctorGF2Certificate.lean","ProctorGF2Checker.lean","ProctorPNPProjection.lean","ProctorPNPEncoding.lean","ProctorGF2Codec.lean","ProctorGF2Highest.lean","ProctorGF2Global.lean","ProctorGF2Cost.lean")]
    src=[p.read_text() for p in paths]
    combined="import Init.Data.Nat.Bitwise.Lemmas\n"+"\n".join(s.removeprefix("import Init\n") for s in src)
    strict=GF_NAMES+SOLVER_NAMES+CERT_NAMES+CHECK_NAMES
    formal=check(combined,out/"cost",lean,strict+MASK_NAMES+CODEC_NAMES+HIGHEST_NAMES+GLOBAL_NAMES+NAMES,"ProctorGF2")
    log=(out/"cost/kernel.txt").read_text()
    domain={n:next((l for l in log.splitlines() if l.startswith("'ProctorPNP."+n+"' ")),None) for n in PNP_NAMES+DOMAIN_NAMES}
    def allowed(ns,n,line,strict=False):
        head="'"+ns+"."+n+"' "
        if line==head+"does not depend on any axioms":return True
        if strict or not isinstance(line,str) or not line.startswith(head+"depends on axioms: [") or not line.endswith("]"):return False
        names=set(line[len(head+"depends on axioms: ["):-1].split(", "))
        return bool(names) and names<={"propext","Quot.sound"}
    old_ok=all(allowed("ProctorGF2",n,formal["axioms"][n],True) for n in strict)
    domain_ok=all(allowed("ProctorPNP",n,line,True) for n,line in domain.items())
    library_ok=all(allowed("ProctorGF2",n,formal["axioms"][n]) for n in MASK_NAMES+CODEC_NAMES+HIGHEST_NAMES+GLOBAL_NAMES+NAMES)
    passed=formal["exit_code"]==0 and old_ok and domain_ok and library_ok
    report={"status":"KERNEL_VERIFIED_COST_MODEL" if passed else "UNVERIFIED",
            "formal":formal,"domain_audit":domain,"controls":controls(),"lean_version":v.stdout.strip(),
            "strict_prior_gate":old_ok,"strict_domain_gate":domain_ok,"library_gate":library_ok,
            "source_hashes":{p.name:digest(s.encode()) for p,s in zip(paths,src)},
            "provider":"deterministic_specialist_replay","live_ai":False,"global_promotion":"NONE",
            "python_program_refinement_verified":False,"formal_bit_cost_verified":False,"abstract_bit_charge_bound_verified":passed,
            "remaining":["full Python source-language refinement","real runtime/allocator cost refinement"]}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    if passed:
        data=fixtures()
        p=out/"CrossLanguage.lean";p.write_text(combined+"\n"+eval_source(data),encoding="utf-8")
        r=subprocess.run([lean,"-DwarningAsError=true",str(p)],capture_output=True,text=True,timeout=180)
        log=r.stdout+r.stderr;(out/"cross-language.txt").write_text(log)
        observed=[l for l in log.splitlines() if l in ("true","false")]
        ok=r.returncode==0 and observed==["true"]*((len(data)+31)//32)
        report["cross_language"]={"passed":ok,"cases":len(data),"batches":len(observed),"exit_code":r.returncode,"diagnostic":log[-3000:]}
        if not ok:report["status"]="FORMAL_SOLVER_VERIFIED_CROSS_LANGUAGE_FAILED"
        (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    md=ROOT/"docs/research/tga-universal/PNP-F010.md"
    make_docx(md,out/"PNP-F010.docx");verify(md,out/"PNP-F010.docx")
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--lean",default="lean")
    a=p.parse_args();r=run(a.output_dir,a.lean);print(json.dumps(r,indent=2))
    if r["status"]!="KERNEL_VERIFIED_COST_MODEL":raise SystemExit(1)
