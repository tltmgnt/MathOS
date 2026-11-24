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
NAMES=("rowMasks_sat","augmented_width","augmented_length","augmented_sat","pick","liftExec","augmented_refutes","solveBlocks","blockOutput_spec","block_unsat_complete","block_charge_bound")
def cases():
    pairs=list(product((0,1),repeat=2))
    domains=[tuple(p for j,p in enumerate(pairs) if mask>>j&1) for mask in range(16)]
    for ds in product(domains,repeat=3):
        yield ds,((3,0),(6,1))
    for n in range(3):
        universe=list(product(range(1<<n),(0,1)))
        for rows in product(universe,repeat=2):
            yield (tuple(pairs),)*n,rows
    yield (),()
def fixtures():
    data=[];yes=no=empty=0
    for ds,rs in cases():
        n=len(ds);eq=list(rs)
        for j,d in enumerate(ds):
            s={a*b for a,b in d}
            if not s:eq.append((0,1))
            elif len(s)==1:eq.append((1<<j,next(iter(s))))
        (ok,x),ct=mirror(n,eq)
        if ok:
            ps=tuple(next(p for p in d if p[0]*p[1]==(x>>j&1)) for j,d in enumerate(ds))
            assert all(p in d for p,d in zip(ps,ds))
            assert all((a&x).bit_count()%2==b for a,b in rs)
            result=ps;yes+=1
        else:
            a=b=0
            for j,(u,v) in enumerate(eq):
                if x>>j&1:a^=u;b^=v
            assert (a,b)==(0,1) and x<1<<len(eq)
            result=x;no+=1
        actual=solve_blocks(ds,rs)
        assert verify_blocks(ds,rs,actual) and actual["sat"]==ok
        empty+=any(not d for d in ds)
        c=charge(n,len(eq),ct)
        assert c<=polynomial(n,len(rs)+n)
        data.append((ds,rs,ok,result,c))
    return data,{"systems":len(data),"sat":yes,"unsat":no,"empty_domains":empty}
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
        return "((ProctorPNP.blockOutput "+args+" == "+out+") && (ProctorPNP.solveBlocks "+args+").charge == "+str(c)+")"
    return "\n".join("#eval (["+ ",\n".join(expr(d) for d in data[i:i+24])+"].all id)" for i in range(0,len(data),24))+"\n"
def run(out,lean):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/"artifacts"):raise ValueError("output path")
    out.mkdir(parents=True,exist_ok=False)
    v=subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if v.returncode or not re.search(r"\bversion 4\.14\.0\b",v.stdout):raise RuntimeError("Lean 4.14.0 required")
    paths=[ROOT/"formal"/n for n in ("ProctorGF2.lean","ProctorGF2Solver.lean","ProctorGF2Certificate.lean","ProctorGF2Checker.lean","ProctorPNPProjection.lean","ProctorPNPEncoding.lean","ProctorGF2Codec.lean","ProctorGF2Highest.lean","ProctorGF2Global.lean","ProctorGF2Cost.lean","ProctorPNPEndToEnd.lean")]
    src=[p.read_text() for p in paths]
    combined="import Init.Data.Nat.Bitwise.Lemmas\n"+"\n".join(s.removeprefix("import Init\n") for s in src)
    strict=GF_NAMES+SOLVER_NAMES+CERT_NAMES+CHECK_NAMES
    formal=check(combined,out/"end-to-end",lean,strict+MASK_NAMES+CODEC_NAMES+HIGHEST_NAMES+GLOBAL_NAMES+COST_NAMES,"ProctorGF2")
    log=(out/"end-to-end/kernel.txt").read_text()
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
    new={n:next((l for l in log.splitlines() if l.startswith("'ProctorPNP."+n+"' ")),None) for n in NAMES}
    new_ok=all(allowed("ProctorPNP",n,line) for n,line in new.items())
    passed=formal["exit_code"]==0 and old_ok and domain_ok and library_ok and new_ok
    data,counts=fixtures()
    report={"status":"KERNEL_VERIFIED_RESTRICTED_BLOCK_SOLVER" if passed else "UNVERIFIED",
            "formal":formal,"domain_audit":domain,"controls":counts,"new_audit":new,"new_gate":new_ok,"lean_version":v.stdout.strip(),
            "strict_prior_gate":old_ok,"strict_domain_gate":domain_ok,"library_gate":library_ok,
            "source_hashes":{p.name:digest(s.encode()) for p,s in zip(paths,src)},
            "provider":"deterministic_specialist_replay","live_ai":False,"global_promotion":"NONE",
            "python_program_refinement_verified":False,"formal_bit_cost_verified":False,"abstract_bit_charge_bound_verified":passed,
            "remaining":["preprocessing and lifting bit-cost refinement","full Python source-language refinement","real runtime/allocator cost refinement"]}
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
    md=ROOT/"docs/research/tga-universal/PNP-F011.md"
    make_docx(md,out/"PNP-F011.docx");verify(md,out/"PNP-F011.docx")
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--lean",default="lean")
    a=p.parse_args();r=run(a.output_dir,a.lean);print(json.dumps(r,indent=2))
    if r["status"]!="KERNEL_VERIFIED_RESTRICTED_BLOCK_SOLVER":raise SystemExit(1)
