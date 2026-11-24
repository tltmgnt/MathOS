"""PNP-F004: exact original-row XOR provenance and strict formal replay."""
import argparse
import json
from itertools import product
from pathlib import Path
import re
import subprocess
from mathos.research.tga_proctor_gf2_solver import ROOT,certificate_solver,verify_result,parity,NAMES as SOLVER_NAMES
from mathos.research.tga_proctor_gf2 import digest,check,NAMES as GF_NAMES
from mathos.research.tga_proctor_pnp import NAMES as PNP_NAMES
from mathos.proof_analysis.gap_analysis import Claim,analyze
from scripts.millennium_docx import make_docx,verify

NAMES=("certify","dual_sound","dual_complete")
def dual(n,rows,weights):
    a=b=0
    for i,(u,v) in enumerate(rows):
        if (weights>>i)&1:a^=u;b^=v
    return a==0 and b==1
def controls():
    counts=[]
    for n,limit in ((0,3),(1,3),(2,3),(3,3)):
        universe=list(product(range(1<<n),(0,1)))
        yes=no=0
        for m in range(limit+1):
            for rows in product(universe,repeat=m):
                primal=any(all(parity(a&x)==b for a,b in rows) for x in range(1<<n))
                certs=[w for w in range(1<<m) if dual(n,rows,w)]
                assert primal!=bool(certs)
                r=certificate_solver(n,rows)
                assert verify_result(n,rows,r) and r["sat"]==primal
                if not primal:
                    w=sum(1<<i for i in r["certificate"])
                    assert w in certs
                yes+=primal;no+=not primal
        counts.append({"n":n,"max_rows":limit,"sat":yes,"unsat":no,"cases":yes+no})
    # This three-row contradiction needs every row, not a conflicting pair.
    rows=[(1,1),(2,1),(3,1)]
    assert [w for w in range(8) if dual(2,rows,w)]==[7]
    r=certificate_solver(2,rows)
    assert r["certificate"]==[0,1,2] and verify_result(2,rows,r)
    return {"exhaustive":counts,"total":sum(c["cases"] for c in counts),
            "three_row_minimal_certificate":[0,1,2],
            "scope":"finite primal/dual enumeration; no Python refinement proof"}
def graph(prior,cert):
    items={"projection":("Disjoint block projection",prior),"row_calculus":("GF2 row operations",prior),
        "certificate_soundness":("Contradiction certificate soundness",prior),
        "pivot_step":("Constructive elimination step",prior),"solver_iteration":("Total reference solver",prior),
        "certificate_generation_formal":("Constructive original-row XOR weight certificate",cert),
        "implementation_refinement":("Full PNP-B006 optimized implementation correspondence",False),
        "bit_cost":("Formal total bit complexity",False)}
    g={k:Claim(v,"established_external" if ok else "open") for k,(v,ok) in items.items()}
    g["scoped_solver"]=Claim("Formal B006 scoped solver","derived",(tuple(g),))
    r=analyze(g,"scoped_solver")
    return {"status":r["status"],"remaining":r["minimal_completion_sets"],"scope":"specialist only"}
def run(out,lean):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/"artifacts"):raise ValueError("output path")
    out.mkdir(parents=True,exist_ok=False)
    v=subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if v.returncode or not re.search(r"\bversion 4\.14\.0\b",v.stdout):raise RuntimeError("Lean 4.14.0 required")
    projection=check((ROOT/"formal/ProctorPNPProjection.lean").read_text(),out/"projection",lean,PNP_NAMES,"ProctorPNP")
    paths=[ROOT/"formal"/n for n in ("ProctorGF2.lean","ProctorGF2Solver.lean","ProctorGF2Certificate.lean")]
    sources=[p.read_text() for p in paths]
    base=sources[0]+"\n"+sources[1].removeprefix("import Init\n")
    prior=check(base,out/"prior",lean,GF_NAMES+SOLVER_NAMES,"ProctorGF2")
    old=projection["accepted"] and prior["accepted"]
    report={"status":"IN_PROGRESS","provider":"deterministic_specialist_replay","live_ai":False,
        "lean_version":v.stdout.strip(),"source_sha256":{p.name:digest(s.encode()) for p,s in zip(paths,sources)},
        "projection":projection,"prior":prior,"before":graph(old,False),"controls":controls(),
        "global_promotion":"NONE","canonical_open_obligations":14}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    formal=check(base+"\n"+sources[2],out/"certificate",lean,GF_NAMES+SOLVER_NAMES+NAMES,"ProctorGF2")
    accepted=old and formal["accepted"]
    report.update(formal=formal,status="KERNEL_VERIFIED_GF2_DUAL_CERTIFICATES" if accepted else "UNVERIFIED",after=graph(old,accepted))
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    md=ROOT/"docs/research/tga-universal/PNP-F004.md"
    make_docx(md,out/"PNP-F004.docx");verify(md,out/"PNP-F004.docx")
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--lean",default="lean")
    a=p.parse_args();r=run(a.output_dir,a.lean);print(json.dumps(r,indent=2))
    if r["status"]!="KERNEL_VERIFIED_GF2_DUAL_CERTIFICATES":raise SystemExit(1)
