"""F005: checked primal/dual interface, actual B006 outputs, no full Python refinement claim."""
import argparse
import json
from itertools import product
from pathlib import Path
import re
import subprocess
from mathos.research.tga_proctor_gf2_certificate import ROOT,NAMES as CERT_NAMES
from mathos.research.tga_proctor_gf2_solver import NAMES as SOLVER_NAMES
from mathos.research.tga_proctor_gf2 import NAMES as GF_NAMES,check,digest
from mathos.research.tga_proctor_pnp import NAMES as PNP_NAMES
from mathos.research.breakthrough_cycle6 import solve_blocks,verify_result
from scripts.millennium_docx import make_docx,verify

NAMES=("weighted_lhs","weighted_rhs","dualCheck_iff","primalCheck_iff","checkOutput_sound","generated_accepted")
def bits(n,a):
    if type(n) is not int or not 0<=n<=64 or type(a) is not int or not 0<=a<1<<n:
        raise ValueError("width or bitmask")
    return [(a>>i)&1 for i in range(n)]
def project(blocks,rows):
    eq=list(rows)
    for j,d in enumerate(blocks):
        if not d:raise ValueError("empty domain handled separately")
        values={a*b for a,b in d}
        if len(values)==1:eq.append((1<<j,next(iter(values))))
    return eq
def encode(blocks,rows,r):
    """Transport an actual solver result to the projected GF2 interface."""
    n=len(blocks);eq=project(blocks,rows)
    if not verify_result(blocks,rows,r):raise ValueError("invalid original solver result")
    if r["sat"]:
        w=[a*b for a,b in r["witness"]]
    else:
        w=bits(len(eq),sum(1<<i for i in r["xor_certificate"]))
    return {"n":n,"rows":[[bits(n,a),b] for a,b in eq],"sat":r["sat"],"bits":w}
def fixtures():
    pairs=list(product((0,1),repeat=2))
    domains=[tuple(p for j,p in enumerate(pairs) if mask>>j&1) for mask in range(16)]
    data=[];empty=sat=unsat=0
    def one(blocks,rows):
        nonlocal empty,sat,unsat
        r=solve_blocks(blocks,rows)
        assert verify_result(blocks,rows,r)
        if any(not d for d in blocks):
            assert not r["sat"] and "empty_block" in r
            empty+=1;return
        item=encode(blocks,rows,r)
        data.append(item)
        sat+=r["sat"];unsat+=not r["sat"]
    for blocks in product(domains,repeat=3):
        one(blocks,[(3,0),(6,1)])
    # Every two-row affine system on two unrestricted AND blocks.
    for rows in product(product(range(4),(0,1)),repeat=2):
        one([pairs,pairs],rows)
    one([],[]);one([],[(0,1)])
    return data,{"sat":sat,"unsat":unsat,"empty_domain_cases":empty,"projected_cases":len(data)}
def literal(v):
    return "true" if v else "false"
def vec(xs):
    return "["+",".join(literal(b) for b in xs)+"]"
def expr(d):
    rows="["+",".join("⟨"+vec(a)+","+literal(b)+"⟩" for a,b in d["rows"])+"]"
    return "ProctorGF2.checkOutput "+str(d["n"])+" "+rows+" ("+literal(d["sat"])+","+vec(d["bits"])+")"
def batches(data):
    # Each bounded batch is independently evaluated by Lean, not Python.
    lines=[]
    for i in range(0,len(data),64):
        es=",\n  ".join(expr(d) for d in data[i:i+64])
        lines.append("#eval (["+es+"].all id)")
    return "\n".join(lines)+"\n"
def run(out,lean):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/"artifacts"):raise ValueError("output path")
    out.mkdir(parents=True,exist_ok=False)
    v=subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if v.returncode or not re.search(r"\bversion 4\.14\.0\b",v.stdout):raise RuntimeError("Lean 4.14.0 required")
    paths=[ROOT/"formal"/n for n in ("ProctorGF2.lean","ProctorGF2Solver.lean","ProctorGF2Certificate.lean","ProctorGF2Checker.lean")]
    src=[p.read_text() for p in paths]
    base=src[0]+"\n"+src[1].removeprefix("import Init\n")+"\n"+src[2]
    projection=check((ROOT/"formal/ProctorPNPProjection.lean").read_text(),out/"projection",lean,PNP_NAMES,"ProctorPNP")
    proof=check(base+"\n"+src[3],out/"checker",lean,GF_NAMES+SOLVER_NAMES+CERT_NAMES+NAMES,"ProctorGF2")
    data,counts=fixtures()
    (out/"fixtures.json").write_text(json.dumps(data,separators=(",",":"))+"\n")
    report={"status":"UNVERIFIED","provider":"deterministic_specialist_replay","live_ai":False,"lean_version":v.stdout.strip(),
      "source_hashes":{p.name:digest(s.encode()) for p,s in zip(paths,src)},
      "python_source_sha256":digest((ROOT/"mathos/research/breakthrough_cycle6.py").read_bytes()),
      "formal":proof,"projection":projection,"controls":counts,"global_promotion":"NONE",
      "python_program_refinement_verified":False,"formal_bit_cost_verified":False}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    if projection["accepted"] and proof["accepted"]:
        # Compile actual Python results as fixed Boolean data. The kernel theorem
        # proves checker soundness universally; these evaluations exercise the transport.
        # Deliberately corrupt one SAT witness and one UNSAT certificate.
        bad=[{"n":1,"rows":[[[1],1]],"sat":True,"bits":[0]},
             {"n":1,"rows":[[[1],0],[[1],1]],"sat":False,"bits":[1,0]}]
        test=batches(data)
        test+="\n".join("#eval ("+expr(d)+")" for d in bad)+"\n"
        # Separate evaluation script with no axiom audit output except prior module prints.
        replay=base+"\n"+src[3]+"\n"+test
        p=out/"CrossLanguage.lean";p.write_text(replay,encoding="utf-8")
        r=subprocess.run([lean,"-DwarningAsError=true",str(p)],capture_output=True,text=True,timeout=120)
        log=r.stdout+r.stderr;(out/"cross-language.txt").write_text(log)
        observed=[l for l in log.splitlines() if l in ("true","false")]
        expected=["true"]*((len(data)+63)//64)+["false","false"]
        passed=r.returncode==0 and observed==expected
        report["cross_language"]={"passed":passed,"exit_code":r.returncode,"accepted_batches":observed.count("true"),
           "expected_batches":len(expected)-2,"rejected_mutations":observed.count("false"),
           "source_sha256":digest(p.read_bytes()),"log_sha256":digest(log.encode()),"diagnostic":log[-3000:]}
        if passed:report["status"]="KERNEL_VERIFIED_CERTIFICATE_INTERFACE"
    report["remaining"]=["formal_bit_complexity","python_program_refinement","formal_bitmask_transport_and_domain_encoding"]
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    md=ROOT/"docs/research/tga-universal/PNP-F005.md"
    make_docx(md,out/"PNP-F005.docx");verify(md,out/"PNP-F005.docx")
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--lean",default="lean")
    a=p.parse_args();r=run(a.output_dir,a.lean);print(json.dumps(r,indent=2))
    if r["status"]!="KERNEL_VERIFIED_CERTIFICATE_INTERFACE":raise SystemExit(1)
