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
from mathos.research.tga_proctor_pnp_full_cost import NAMES as FULL_NAMES,fixtures as prior_fixtures
from mathos.research.tga_proctor_bit_cells import CELL_NAMES,NAMES as WIRE_NAMES
TAPE_NAMES=("initTape","tapeXor","tapeScan","tapeUpdate","tapeClearAll","tapeStripAll","tapeBase","solveTape","tapeCertify","tape_output_valid","tape_cost_bound")
def bits(n,a):return [(a>>i)&1 for i in range(n)]
def mirror_tape(n,rows):
    m=len(rows)
    ts=[(bits(n,a),b,bits(m,1<<i)) for i,(a,b) in enumerate(rows)]
    init=2*m*(m+1)
    def go(k,ts):
        if not k:
            for i,(_,b,w) in enumerate(ts):
                if b:return (False,w),2*(i+1)
            return (True,[]),2*len(ts)
        pivot=None;scans=0
        for r in ts:
            scans+=2
            if r[0][0]:pivot=r;break
        nxt=[];updates=0
        for a,b,w in ts:
            updates+=4
            if pivot is not None and a[0]:
                u,v,z=pivot
                a=[x^y for x,y in zip(a,u)];b^=v
                w=[x^y for x,y in zip(w,z)]
                updates+=4*(k+m+1)
            nxt.append((a[1:],b,w))
        (ok,x),cost=go(k-1,nxt)
        if not ok:return (False,x),scans+updates+cost+1
        if pivot is None:return (True,[0]+x),scans+updates+cost+1
        a,b,_=pivot
        return (True,[b^(sum(u*v for u,v in zip(a[1:],x))%2)]+x),scans+updates+cost+4*(k-1)+4
    ans,cost=go(n,ts)
    return ans,init+cost
def bound(n,m):return 4*m*m+4*m+n*(m*(4*(n+m+1)+6)+4*n+4)+2*m
def fixtures():
    data=[];yes=no=0;steps=0
    for n in range(4):
        universe=list(product(range(1<<n),(0,1)))
        for m in range(4):
            for rs in product(universe,repeat=m):
                (ok,x),c=mirror_tape(n,rs)
                brute=any(all((a&v).bit_count()%2==b for a,b in rs) for v in range(1<<n))
                assert brute==ok and c<=bound(n,m)
                mask=sum(v<<i for i,v in enumerate(x))
                if ok:
                    assert len(x)==n and all((a&mask).bit_count()%2==b for a,b in rs)
                else:
                    assert len(x)==m
                    a=b=0
                    for (u,v),w in zip(rs,x):
                        if w:a^=u;b^=v
                    assert (a,b)==(0,1)
                data.append((n,rs,ok,x,c));yes+=ok;no+=not ok;steps+=c
    return data,{"systems":len(data),"sat":yes,"unsat":no,"modeled_steps_sum":steps}
def eval_source(data):
    def bit(b):return "true" if b else "false"
    def vec(v):return "["+",".join(map(bit,v))+"]"
    es=[]
    for n,rs,ok,x,c in data:
        rows="["+",".join("⟨"+vec(bits(n,a))+","+bit(b)+"⟩" for a,b in rs)+"]"
        proof="True.intro"
        for _ in rs:proof="⟨rfl,"+proof+"⟩"
        args=f"{n} {rows} ({proof})"
        es.append(f"(ProctorGF2.tapeOutput {args} == ({bit(ok)},{vec(x)}) && (ProctorGF2.tapeCertify {args}).steps == {c})")
    return "\n".join("#eval (["+ ",\n".join(es[i:i+32])+"].all id)" for i in range(0,len(es),32))+"\n",len(es)
def run(out,lean):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/"artifacts"):raise ValueError("output path")
    out.mkdir(parents=True,exist_ok=False)
    v=subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if v.returncode or not re.search(r"\bversion 4\.14\.0\b",v.stdout):raise RuntimeError("Lean 4.14.0 required")
    paths=[ROOT/"formal"/n for n in ("ProctorGF2.lean","ProctorGF2Solver.lean","ProctorGF2Certificate.lean","ProctorGF2Checker.lean","ProctorPNPProjection.lean","ProctorPNPEncoding.lean","ProctorGF2Codec.lean","ProctorGF2Highest.lean","ProctorGF2Global.lean","ProctorGF2Cost.lean","ProctorPNPEndToEnd.lean","ProctorPNPFullCost.lean","ProctorBitCells.lean","ProctorTapeSolver.lean")]
    src=[p.read_text() for p in paths]
    combined="import Init.Data.Nat.Bitwise.Lemmas\n"+"\n".join(s.removeprefix("import Init\n") for s in src)
    strict=GF_NAMES+SOLVER_NAMES+CERT_NAMES+CHECK_NAMES
    formal=check(combined,out/"tape-solver",lean,strict+MASK_NAMES+CODEC_NAMES+HIGHEST_NAMES+GLOBAL_NAMES+COST_NAMES+CELL_NAMES+TAPE_NAMES,"ProctorGF2")
    log=(out/"tape-solver/kernel.txt").read_text()
    domain={n:next((l for l in log.splitlines() if l.startswith("'ProctorPNP."+n+"' ")),None) for n in PNP_NAMES+DOMAIN_NAMES}
    def allowed(ns,n,line,strict=False):
        head="'"+ns+"."+n+"' "
        if line==head+"does not depend on any axioms":return True
        if strict or not isinstance(line,str) or not line.startswith(head+"depends on axioms: [") or not line.endswith("]"):return False
        names=set(line[len(head+"depends on axioms: ["):-1].split(", "))
        return bool(names) and names<={"propext","Quot.sound"}
    old_ok=all(allowed("ProctorGF2",n,formal["axioms"][n],True) for n in strict)
    domain_ok=all(allowed("ProctorPNP",n,line,True) for n,line in domain.items())
    library_ok=all(allowed("ProctorGF2",n,formal["axioms"][n]) for n in MASK_NAMES+CODEC_NAMES+HIGHEST_NAMES+GLOBAL_NAMES+COST_NAMES+CELL_NAMES+TAPE_NAMES)
    new={n:next((l for l in log.splitlines() if l.startswith("'ProctorPNP."+n+"' ")),None) for n in END_NAMES+FULL_NAMES+WIRE_NAMES}
    new_ok=all(allowed("ProctorPNP",n,line) for n,line in new.items())
    passed=formal["exit_code"]==0 and old_ok and domain_ok and library_ok and new_ok
    data,counts=fixtures()
    report={"status":"KERNEL_VERIFIED_AFFINE_TAPE_SOLVER" if passed else "UNVERIFIED",
            "formal":formal,"domain_audit":domain,"controls":counts,"new_audit":new,"new_gate":new_ok,"lean_version":v.stdout.strip(),
            "strict_prior_gate":old_ok,"strict_domain_gate":domain_ok,"library_gate":library_ok,
            "source_hashes":{p.name:digest(s.encode()) for p,s in zip(paths,src)},
            "provider":"deterministic_specialist_replay","live_ai":False,"global_promotion":"NONE",
            "python_program_refinement_verified":False,"formal_bit_cost_verified":False,"abstract_bit_charge_bound_verified":passed,
            "remaining":["full Python source-language refinement","full disjoint-block preprocessing/lifting tape simulation","equivalence to highest-bit trace","finite-state machine overhead and peak allocator storage"]}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    if passed:
        source,num_cases=eval_source(data)
        p=out/"CrossLanguage.lean";p.write_text(combined+"\n"+source,encoding="utf-8")
        r=subprocess.run([lean,"-DwarningAsError=true",str(p)],capture_output=True,text=True,timeout=240)
        log=r.stdout+r.stderr;(out/"cross-language.txt").write_text(log)
        observed=[l for l in log.splitlines() if l in ("true","false")]
        ok=r.returncode==0 and observed==["true"]*((num_cases+31)//32)
        report["cross_language"]={"passed":ok,"cases":num_cases,"batches":len(observed),"exit_code":r.returncode,"diagnostic":log[-3000:]}
        if not ok:report["status"]="FORMAL_SOLVER_VERIFIED_CROSS_LANGUAGE_FAILED"
        (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    md=ROOT/"docs/research/tga-universal/PNP-F014.md"
    make_docx(md,out/"PNP-F014.docx");verify(md,out/"PNP-F014.docx")
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--lean",default="lean")
    a=p.parse_args();r=run(a.output_dir,a.lean);print(json.dumps(r,indent=2))
    if r["status"]!="KERNEL_VERIFIED_AFFINE_TAPE_SOLVER":raise SystemExit(1)
