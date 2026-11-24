"""PNP-F003: recursive Lean solver replay and executable low-pivot XOR certificates.

The Python routine is not the extracted Lean solver. Refinement and bit-cost
formalization are deliberately separate open obligations.
"""
import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import re
import subprocess
from mathos.research.tga_agent import ROOT
from mathos.proof_analysis.gap_analysis import Claim, analyze
from mathos.research.tga_proctor_gf2 import NAMES as GF2_NAMES, check
from mathos.research.tga_proctor_pnp import NAMES as PNP_NAMES
from scripts.millennium_docx import make_docx, verify

NAMES=("scan","solve","witness_spec","none_iff")
def digest(b): return hashlib.sha256(b).hexdigest()

def parity(mask): return mask.bit_count() & 1

def valid(n,rows):
    if type(n) is not int or n<0: raise ValueError("dimension")
    if any(type(a) is not int or not 0<=a<(1<<n) or type(b) is not int or b not in (0,1) for a,b in rows):
        raise ValueError("row outside exact dimension")

def certificate_solver(n,rows):
    """Eliminate one low coordinate at a time, retaining row provenance."""
    rows=list(rows)
    valid(n,rows)
    current=[(a,b,1<<i) for i,(a,b) in enumerate(rows)]
    history=[]
    xors=0
    for _ in range(n):
        pivot=next((r for r in current if r[0]&1),None)
        history.append(None if pivot is None else (pivot[0]>>1,pivot[1]))
        nxt=[]
        for a,b,p in current:
            if pivot is not None and a&1:
                a^=pivot[0];b^=pivot[1];p^=pivot[2]
                xors+=1
            assert not a&1
            nxt.append((a>>1,b,p))
        current=nxt
    for a,b,p in current:
        assert a==0
        if b:
            return {"sat":False,"certificate":[i for i in range(len(rows)) if (p>>i)&1],"row_xors":xors}
    x=0
    for pivot in reversed(history):
        bit=0 if pivot is None else pivot[1]^parity(pivot[0]&x)
        x=(x<<1)|bit
    return {"sat":True,"witness":x,"row_xors":xors}

def verify_result(n,rows,result):
    """Independent check on original explicit-width rows."""
    valid(n,rows)
    if type(result.get("sat")) is not bool: return False
    if result["sat"]:
        x=result.get("witness")
        return type(x) is int and 0<=x<(1<<n) and all(parity(a&x)==b for a,b in rows)
    sel=result.get("certificate")
    if type(sel) is not list or not sel or any(type(i) is not int or not 0<=i<len(rows) for i in sel):return False
    if len(set(sel))!=len(sel):return False
    a=b=0
    for i in sel: a^=rows[i][0];b^=rows[i][1]
    return (a,b)==(0,1)

def controls():
    counts=[]
    for n,limit in ((0,4),(1,4),(2,4),(3,3)):
        universe=list(product(range(1<<n),(0,1)))
        yes=no=0
        for m in range(limit+1):
            for rows in product(universe,repeat=m):
                actual=certificate_solver(n,rows)
                expected=any(all(parity(a&x)==b for a,b in rows) for x in range(1<<n))
                assert actual["sat"]==expected
                assert verify_result(n,rows,actual)
                assert actual["row_xors"]<=n*m
                yes+=expected;no+=not expected
        counts.append({"dimension":n,"max_rows":limit,"sat":yes,"unsat":no,"cases":yes+no})
    large=[]
    for n in (16,64,256,1024):
        # One long row, with either an independent unit equation or its own contradiction.
        a=(1<<n)-1
        for rows in ([(a,1),(1,0)],[(a,1),(a,0)]):
            r=certificate_solver(n,rows)
            assert verify_result(n,rows,r)
            assert r["row_xors"]<=n*len(rows)
            large.append({"dimension":n,"sat":r["sat"],"row_xors":r["row_xors"]})
    assert not verify_result(2,[(3,0),(3,1)],{"sat":False,"certificate":[0]})
    assert not verify_result(2,[(3,0),(3,1)],{"sat":False,"certificate":[0,0,1]})
    assert not verify_result(2,[(3,1)],{"sat":True,"witness":0})
    return {"exhaustive":counts,"total_cases":sum(x["cases"] for x in counts),
            "large_controls":large,"tampered_certificates_or_witnesses_rejected":3,
            "python_lean_refinement_verified":False}

def graph(proj,gf2,solver):
    g={k:Claim(label,"established_external" if ok else "open") for k,label,ok in (
       ("projection","Disjoint-block projection",proj),
       ("row_calculus","GF(2) row replacement",gf2),
       ("certificate_soundness","GF(2) contradiction certificate soundness",gf2),
       ("pivot_step","Constructive pivot step",gf2),
       ("solver_iteration","Total exact-dimension Lean decision and witness",solver),
       ("certificate_generation_formal","Formal row-provenance certificate construction",False),
       ("implementation_refinement","Bitmask and full PNP-B006 solver correspondence",False),
       ("bit_cost","Formal polynomial bit complexity",False))}
    g["scoped_solver"]=Claim("Formal B006 scoped solver","derived",(tuple(g),))
    r=analyze(g,"scoped_solver")
    return {"status":r["status"],"remaining":r["minimal_completion_sets"],
            "scope":"specialist formal reconstruction only"}

def run(out,lean):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/"artifacts"):raise ValueError("output path")
    out.mkdir(parents=True,exist_ok=False)
    v=subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if v.returncode or not re.search(r"\bversion 4\.14\.0\b",v.stdout):raise RuntimeError("Lean 4.14.0 required")
    gf=(ROOT/"formal/ProctorGF2.lean").read_text()
    tail=(ROOT/"formal/ProctorGF2Solver.lean").read_text()
    # Combine exact prior checked definitions with the new module, no arbitrary model code.
    combined=gf+"\n"+tail.removeprefix("import Init\n")
    prior=check((ROOT/"formal/ProctorPNPProjection.lean").read_text(),out/"projection",lean,PNP_NAMES,"ProctorPNP")
    gf2=check(gf,out/"gf2",lean,GF2_NAMES,"ProctorGF2")
    report={"status":"IN_PROGRESS","provider":"deterministic_specialist_replay","live_ai":False,
            "lean_version":v.stdout.strip(),"source_paper_sha256":digest((ROOT/"docs/research/breakthrough/PNP-B006.md").read_bytes()),
            "solver_module_sha256":digest(tail.encode()),"projection":prior,"gf2":gf2,
            "before":graph(prior["accepted"],gf2["accepted"],False),"controls":controls(),
            "global_promotion":"NONE","canonical_open_obligations":14}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    formal=check(combined,out/"solver",lean,NAMES,"ProctorGF2")
    report["solver"]=formal
    report["status"]="KERNEL_VERIFIED_TOTAL_GF2_SOLVER" if prior["accepted"] and gf2["accepted"] and formal["accepted"] else "UNVERIFIED"
    report["after"]=graph(prior["accepted"],gf2["accepted"],formal["accepted"])
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    md=ROOT/"docs/research/tga-universal/PNP-F003.md"
    make_docx(md,out/"PNP-F003.docx");verify(md,out/"PNP-F003.docx")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--lean",default="lean")
    a=p.parse_args();r=run(a.output_dir,a.lean);print(json.dumps(r,indent=2))
    if r["status"]!="KERNEL_VERIFIED_TOTAL_GF2_SOLVER":raise SystemExit(1)
