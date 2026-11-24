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
CELL_NAMES=("xorCells_spec","dotCells_spec","mask_xor_cells","mask_dot_cells","readCell_at","writeCell_at","taggedCells_spec","arithmetic_budget_bound","copyCells_spec")
NAMES=("pair_roundtrip","wire_valid","wire_length_bound","wire_copy_bound")
def bits(n,a):return [(a>>j)&1 for j in range(n)]
def fixtures():
    data,old=prior_fixtures()
    # Full output packet controls; each instance independently decoded.
    packets=[]
    for ds,rs,ok,result,_ in data:
        n,m=len(ds),len(rs)
        M=m+sum(len({a*b for a,b in d})<2 for d in ds)
        packet=[1]+[b for p in result for b in p] if ok else [0]+bits(M,result)
        assert len(packet)<=2*n+m+1
        if ok:
            assert list(zip(packet[1::2],packet[2::2]))==list(result)
        else:
            assert sum(b<<i for i,b in enumerate(packet[1:]))==result
        packets.append((ds,rs,packet))
    return packets,{"wire_packets":len(packets),"sat":old["sat"],"unsat":old["unsat"],
        "mask_pairs":sum(4**n for n in range(5)),"memory_cases":sum(n*2**n*2 for n in range(1,5))}
def eval_source(data):
    def bit(b):return "true" if b else "false"
    def vec(v):return "["+",".join(map(bit,v))+"]"
    def pair(p):return "("+bit(p[0])+","+bit(p[1])+")"
    es=[]
    for n in range(5):
        for a,b in product(range(1<<n),repeat=2):
            aa,bb=vec(bits(n,a)),vec(bits(n,b))
            xx=vec(bits(n,a^b))
            es.append(f"((ProctorGF2.xorCells {aa} {bb}).value == {xx} && (ProctorGF2.xorCells {aa} {bb}).steps == {4*n} && (ProctorGF2.dotCells {aa} {bb}).value == {bit((a&b).bit_count()%2)} && (ProctorGF2.dotCells {aa} {bb}).steps == {4*n})")
        for a in range(1<<n):
            for j in range(n):
                for v in (0,1):
                    bs=vec(bits(n,a));out=vec(bits(n,(a&~(1<<j))|(v<<j)))
                    es.append(f"((ProctorGF2.readCell {j} {bs}).value == some {bit((a>>j)&1)} && (ProctorGF2.readCell {j} {bs}).steps == {j+1} && (ProctorGF2.writeCell {bit(v)} {j} {bs}).value == some {out} && (ProctorGF2.writeCell {bit(v)} {j} {bs}).steps == {2*(j+1)})")
    for ds,rs,packet in data:
        dom="["+",".join("["+",".join(map(pair,a))+"]" for a in ds)+"]"
        rows="["+",".join("("+str(a)+","+bit(b)+")" for a,b in rs)+"]"
        proof="True.intro"
        for _ in rs:proof="⟨by decide,"+proof+"⟩"
        args=dom+" "+rows+" ("+proof+")"
        es.append(f"(let r := ProctorPNP.wireRun {args}; r.value == {vec(packet)} && r.steps == {2*len(packet)})")
    return "\n".join("#eval (["+ ",\n".join(es[i:i+24])+"].all id)" for i in range(0,len(es),24))+"\n",len(es)
def run(out,lean):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/"artifacts"):raise ValueError("output path")
    out.mkdir(parents=True,exist_ok=False)
    v=subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if v.returncode or not re.search(r"\bversion 4\.14\.0\b",v.stdout):raise RuntimeError("Lean 4.14.0 required")
    paths=[ROOT/"formal"/n for n in ("ProctorGF2.lean","ProctorGF2Solver.lean","ProctorGF2Certificate.lean","ProctorGF2Checker.lean","ProctorPNPProjection.lean","ProctorPNPEncoding.lean","ProctorGF2Codec.lean","ProctorGF2Highest.lean","ProctorGF2Global.lean","ProctorGF2Cost.lean","ProctorPNPEndToEnd.lean","ProctorPNPFullCost.lean","ProctorBitCells.lean")]
    src=[p.read_text() for p in paths]
    combined="import Init.Data.Nat.Bitwise.Lemmas\n"+"\n".join(s.removeprefix("import Init\n") for s in src)
    strict=GF_NAMES+SOLVER_NAMES+CERT_NAMES+CHECK_NAMES
    formal=check(combined,out/"bit-cells",lean,strict+MASK_NAMES+CODEC_NAMES+HIGHEST_NAMES+GLOBAL_NAMES+COST_NAMES+CELL_NAMES,"ProctorGF2")
    log=(out/"bit-cells/kernel.txt").read_text()
    domain={n:next((l for l in log.splitlines() if l.startswith("'ProctorPNP."+n+"' ")),None) for n in PNP_NAMES+DOMAIN_NAMES}
    def allowed(ns,n,line,strict=False):
        head="'"+ns+"."+n+"' "
        if line==head+"does not depend on any axioms":return True
        if strict or not isinstance(line,str) or not line.startswith(head+"depends on axioms: [") or not line.endswith("]"):return False
        names=set(line[len(head+"depends on axioms: ["):-1].split(", "))
        return bool(names) and names<={"propext","Quot.sound"}
    old_ok=all(allowed("ProctorGF2",n,formal["axioms"][n],True) for n in strict)
    domain_ok=all(allowed("ProctorPNP",n,line,True) for n,line in domain.items())
    library_ok=all(allowed("ProctorGF2",n,formal["axioms"][n]) for n in MASK_NAMES+CODEC_NAMES+HIGHEST_NAMES+GLOBAL_NAMES+COST_NAMES+CELL_NAMES)
    new={n:next((l for l in log.splitlines() if l.startswith("'ProctorPNP."+n+"' ")),None) for n in END_NAMES+FULL_NAMES+NAMES}
    new_ok=all(allowed("ProctorPNP",n,line) for n,line in new.items())
    passed=formal["exit_code"]==0 and old_ok and domain_ok and library_ok and new_ok
    data,counts=fixtures()
    report={"status":"KERNEL_VERIFIED_CELL_PRIMITIVES_AND_WIRE" if passed else "UNVERIFIED",
            "formal":formal,"domain_audit":domain,"controls":counts,"new_audit":new,"new_gate":new_ok,"lean_version":v.stdout.strip(),
            "strict_prior_gate":old_ok,"strict_domain_gate":domain_ok,"library_gate":library_ok,
            "source_hashes":{p.name:digest(s.encode()) for p,s in zip(paths,src)},
            "provider":"deterministic_specialist_replay","live_ai":False,"global_promotion":"NONE",
            "python_program_refinement_verified":False,"formal_bit_cost_verified":False,"abstract_bit_charge_bound_verified":passed,
            "remaining":["full Python source-language refinement","whole solver simulation by bit-cell machine","concrete machine overhead and peak allocator storage"]}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    if passed:
        source,num_cases=eval_source(data)
        p=out/"CrossLanguage.lean";p.write_text(combined+"\n"+source,encoding="utf-8")
        r=subprocess.run([lean,"-DwarningAsError=true",str(p)],capture_output=True,text=True,timeout=240)
        log=r.stdout+r.stderr;(out/"cross-language.txt").write_text(log)
        observed=[l for l in log.splitlines() if l in ("true","false")]
        ok=r.returncode==0 and observed==["true"]*((num_cases+23)//24)
        report["cross_language"]={"passed":ok,"cases":num_cases,"batches":len(observed),"exit_code":r.returncode,"diagnostic":log[-3000:]}
        if not ok:report["status"]="FORMAL_SOLVER_VERIFIED_CROSS_LANGUAGE_FAILED"
        (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    md=ROOT/"docs/research/tga-universal/PNP-F013.md"
    make_docx(md,out/"PNP-F013.docx");verify(md,out/"PNP-F013.docx")
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--lean",default="lean")
    a=p.parse_args();r=run(a.output_dir,a.lean);print(json.dumps(r,indent=2))
    if r["status"]!="KERNEL_VERIFIED_CELL_PRIMITIVES_AND_WIRE":raise SystemExit(1)
