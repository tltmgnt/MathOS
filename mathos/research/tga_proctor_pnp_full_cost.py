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
from mathos.research.tga_proctor_gf2_cost import NAMES as COST_NAMES,mirror,charge,polynomial
from mathos.research.breakthrough_cycle6 import solve_blocks,verify_result as verify_blocks
from mathos.research.tga_proctor_pnp_end_to_end import NAMES as END_NAMES,fixtures as prior_fixtures
NAMES=("containsCount","buildLocal","buildDomains","pickCount","liftCount","extra_bound","solveFull","full_charge_bound","full_output_spec","full_unsat_complete")
def extra(n,m,q,s,p,g,l):
    return (8*s+4*p+(4*n+4)*g+8*l+8*n+4*m+4)*(n+m+q+1)
def bound(n,m,q):
    return polynomial(n,m+n)+extra(n,m,q,3*q,n*n,n,q)
def scan(d,y):
    for i,(a,b) in enumerate(d):
        if a*b==y:return i+1
    return len(d)
def stats(ds,rs,ok,result,affine):
    n,m,q=len(ds),len(rs),sum(map(len,ds))
    scans=sum(len(d)+scan(d,0)+scan(d,1) for d in ds)
    generated=[i for i,d in enumerate(ds) if len({a*b for a,b in d})<2]
    pads=sum(generated)
    g=len(generated)
    lifted=sum(scan(d,a*b) for d,(a,b) in zip(ds,result)) if ok else 0
    assert scans<=3*q and pads<=n*n and g<=n and lifted<=q
    total=affine+extra(n,m,q,scans,pads,g,lifted)
    assert total<=bound(n,m,q)
    return scans,pads,g,lifted,affine,total
def fixtures():
    data,counts=prior_fixtures()
    # Duplicate domain entries are allowed in the formal list semantics.
    # Exercise a long domain, a forced singleton, and an empty domain.
    from mathos.research.tga_proctor_pnp_end_to_end import cases
    more=[((((0,0),)*17+((1,1),),),((1,1),)),
          ((((1,1),)*9,),((1,0),)),
          (((),((1,1),)*5),())]
    for ds,rs in more:
        n=len(ds);eq=list(rs)
        for j,d in enumerate(ds):
            s={a*b for a,b in d}
            if not s:eq.append((0,1))
            elif len(s)==1:eq.append((1<<j,next(iter(s))))
        (ok,x),ct=mirror(n,eq)
        result=tuple(next(p for p in d if p[0]*p[1]==(x>>j&1)) for j,d in enumerate(ds)) if ok else x
        data.append((ds,rs,ok,result,charge(n,len(eq),ct)))
    counts={"systems":len(data),"sat":sum(d[2] for d in data),"unsat":sum(not d[2] for d in data),
            "empty_domains":sum(any(not d for d in ds) for ds,_,_,_,_ in data),"duplicate_domain_controls":len(more)}
    cs=[stats(*d) for d in data]
    counts.update(dict(zip(("pair_scan_visits","padding_events","generated_rows","lifting_visits","affine_charge_sum","total_charge_sum"),map(sum,zip(*cs)))))
    return data,counts
def eval_source(data):
    def bit(b):return "true" if b else "false"
    def pair(p):return "("+bit(p[0])+","+bit(p[1])+")"
    def expr(d):
        ds,rs,ok,result,c=d
        dom="["+",".join("["+",".join(map(pair,a))+"]" for a in ds)+"]"
        rows="["+",".join("("+str(a)+","+bit(b)+")" for a,b in rs)+"]"
        proof="True.intro"
        for _ in rs:proof="⟨by decide,"+proof+"⟩"
        out=(".sat ["+",".join(map(pair,result))+"]") if ok else ".unsat "+str(result)
        args=dom+" "+rows+" ("+proof+")"
        ct="("+",".join(map(str,stats(*d)))+")"
        return "((ProctorPNP.fullOutput "+args+" == "+out+") && (ProctorPNP.fullStats "+args+" == "+ct+"))"
    return "\n".join("#eval (["+ ",\n".join(expr(d) for d in data[i:i+24])+"].all id)" for i in range(0,len(data),24))+"\n"
def run(out,lean):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/"artifacts"):raise ValueError("output path")
    out.mkdir(parents=True,exist_ok=False)
    v=subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if v.returncode or not re.search(r"\bversion 4\.14\.0\b",v.stdout):raise RuntimeError("Lean 4.14.0 required")
    paths=[ROOT/"formal"/n for n in ("ProctorGF2.lean","ProctorGF2Solver.lean","ProctorGF2Certificate.lean","ProctorGF2Checker.lean","ProctorPNPProjection.lean","ProctorPNPEncoding.lean","ProctorGF2Codec.lean","ProctorGF2Highest.lean","ProctorGF2Global.lean","ProctorGF2Cost.lean","ProctorPNPEndToEnd.lean","ProctorPNPFullCost.lean")]
    src=[p.read_text() for p in paths]
    combined="import Init.Data.Nat.Bitwise.Lemmas\n"+"\n".join(s.removeprefix("import Init\n") for s in src)
    strict=GF_NAMES+SOLVER_NAMES+CERT_NAMES+CHECK_NAMES
    formal=check(combined,out/"full-cost",lean,strict+MASK_NAMES+CODEC_NAMES+HIGHEST_NAMES+GLOBAL_NAMES+COST_NAMES,"ProctorGF2")
    log=(out/"full-cost/kernel.txt").read_text()
    domain={n:next((l for l in log.splitlines() if l.startswith("'ProctorPNP."+n+"' ")),None) for n in PNP_NAMES+DOMAIN_NAMES}
    def allowed(ns,n,line,strict=False):
        head="'"+ns+"."+n+"' "
        if line==head+"does not depend on any axioms":return True
        if strict or not isinstance(line,str) or not line.startswith(head+"depends on axioms: [") or not line.endswith("]"):return False
        names=set(line[len(head+"depends on axioms: ["):-1].split(", "))
        return bool(names) and names<={"propext","Quot.sound"}
    old_ok=all(allowed("ProctorGF2",n,formal["axioms"][n],True) for n in strict)
    domain_ok=all(allowed("ProctorPNP",n,line,True) for n,line in domain.items())
    library_ok=all(allowed("ProctorGF2",n,formal["axioms"][n]) for n in MASK_NAMES+CODEC_NAMES+HIGHEST_NAMES+GLOBAL_NAMES+COST_NAMES)
    new={n:next((l for l in log.splitlines() if l.startswith("'ProctorPNP."+n+"' ")),None) for n in END_NAMES+NAMES}
    new_ok=all(allowed("ProctorPNP",n,line) for n,line in new.items())
    passed=formal["exit_code"]==0 and old_ok and domain_ok and library_ok and new_ok
    data,counts=fixtures()
    report={"status":"KERNEL_VERIFIED_FULL_ABSTRACT_COST" if passed else "UNVERIFIED",
            "formal":formal,"domain_audit":domain,"controls":counts,"new_audit":new,"new_gate":new_ok,"lean_version":v.stdout.strip(),
            "strict_prior_gate":old_ok,"strict_domain_gate":domain_ok,"library_gate":library_ok,
            "source_hashes":{p.name:digest(s.encode()) for p,s in zip(paths,src)},
            "provider":"deterministic_specialist_replay","live_ai":False,"global_promotion":"NONE",
            "python_program_refinement_verified":False,"formal_bit_cost_verified":False,"abstract_bit_charge_bound_verified":passed,
            "remaining":["full Python source-language refinement","concrete machine cost refinement and peak allocator storage"]}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    if passed:
        p=out/"CrossLanguage.lean";p.write_text(combined+"\n"+eval_source(data),encoding="utf-8")
        r=subprocess.run([lean,"-DwarningAsError=true",str(p)],capture_output=True,text=True,timeout=180)
        log=r.stdout+r.stderr;(out/"cross-language.txt").write_text(log)
        observed=[l for l in log.splitlines() if l in ("true","false")]
        ok=r.returncode==0 and observed==["true"]*((len(data)+23)//24)
        report["cross_language"]={"passed":ok,"cases":len(data),"batches":len(observed),"exit_code":r.returncode,"diagnostic":log[-3000:]}
        if not ok:report["status"]="FORMAL_SOLVER_VERIFIED_CROSS_LANGUAGE_FAILED"
        (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    md=ROOT/"docs/research/tga-universal/PNP-F012.md"
    make_docx(md,out/"PNP-F012.docx");verify(md,out/"PNP-F012.docx")
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--lean",default="lean")
    a=p.parse_args();r=run(a.output_dir,a.lean);print(json.dumps(r,indent=2))
    if r["status"]!="KERNEL_VERIFIED_FULL_ABSTRACT_COST":raise SystemExit(1)
