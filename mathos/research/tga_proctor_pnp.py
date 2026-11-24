"""Specialist proof replay with a fixed, source-aligned PNP contract."""
import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import subprocess
import re
from mathos.research.tga_agent import ROOT
from mathos.proof_analysis.gap_analysis import Claim,analyze
from scripts.millennium_docx import make_docx,verify

FORMAL=ROOT/"formal/ProctorPNPProjection.lean"
PAPER=ROOT/"docs/research/breakthrough/PNP-B006.md"
NAMES=("project","lift","projection_iff","shared_projection","shared_clash")
def digest(b):return hashlib.sha256(b).hexdigest()

def controls():
    pairs=list(product((False,True),repeat=2))
    ds=[tuple(p for j,p in enumerate(pairs) if mask>>j&1) for mask in range(16)]
    checked=0
    for domains in product(ds,repeat=3):
        images=[{a and b for a,b in d} for d in domains]
        left={tuple(a and b for a,b in ps) for ps in product(*domains)}
        right=set(product(*images))
        assert left==right
        checked+=1
    return {"three_block_domain_instances":checked,"includes_empty_domains":True,
            "shared_coordinate_conflict":True,"scope":"finite regression only"}

def graph(accepted):
    g={"projection":Claim("Formal disjoint-block projection equivalence","established_external" if accepted else "open"),
       "affine_encoding":Claim("Formal GF(2) equation encoding","open"),
       "elimination":Claim("Verified elimination and certificate correctness","open"),
       "bit_cost":Claim("Verified bit complexity","open"),
       "scoped_solver":Claim("Formal B006 scoped solver","derived",(("projection","affine_encoding","elimination","bit_cost"),))}
    r=analyze(g,"scoped_solver")
    return {"status":r["status"],"remaining":r["minimal_completion_sets"],
            "scope":"specialist formal reconstruction only"}

def run(out,lean="lean"):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/"artifacts"):raise ValueError("output path")
    out.mkdir(parents=True,exist_ok=False)
    v=subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if v.returncode or not re.search(r"\bversion 4\.14\.0\b",v.stdout):raise RuntimeError("Lean 4.14.0 required")
    src=FORMAL.read_text()
    # Fixed curated source, not arbitrary model code. Preserve exact contract.
    contract={"target":"PNP-B006.projection_iff","source_paper_sha256":digest(PAPER.read_bytes()),
              "formal_source_sha256":digest(src.encode()),"theorem":"ProctorPNP.projection_iff",
              "scope":"every finite list of disjoint Boolean-pair domains; any output predicate"}
    report={"contract":contract,"provider":"deterministic_specialist_fixture","live_ai":False,
            "lean_version":v.stdout.strip(),"controls":controls(),"before":graph(False),
            "attempts":[],"global_promotion":"NONE","canonical_open_obligations":14}
    # Inadequate proof attempt: replace only the target proof, retain exact type.
    start=src.index("theorem projection_iff")
    proof=src.index(" := by\n",start)+len(" := by\n")
    end=src.index("\n/-- Local singleton",proof)
    failed=src[:proof]+"  rfl\n"+src[end:]
    for i,(method,source) in enumerate((("reflexivity",failed),("constructive_lifting",src)),1):
        d=out/f"attempt-{i:02d}";d.mkdir()
        p=d/"Candidate.lean";p.write_text(source,encoding="utf-8")
        r=subprocess.run([lean,"-DwarningAsError=true",str(p)],capture_output=True,text=True,timeout=90)
        log=r.stdout+r.stderr
        (d/"kernel.txt").write_text(log,encoding="utf-8")
        audit={name:next((x for x in log.splitlines() if x.startswith("'ProctorPNP."+name+"' ")),None) for name in NAMES}
        accepted=r.returncode==0 and all(audit[n]=="'ProctorPNP."+n+"' does not depend on any axioms" for n in NAMES)
        report["attempts"].append({"method":method,"exit_code":r.returncode,"accepted":accepted,
             "source_sha256":digest(p.read_bytes()),"log_sha256":digest(log.encode()),"axioms":audit})
        (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
        if accepted:break
    accepted=report["attempts"][-1]["accepted"]
    report["status"]="KERNEL_VERIFIED_SCOPED_PROJECTION" if accepted else "UNVERIFIED"
    report["after"]=graph(accepted)
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    md=ROOT/"docs/research/tga-universal/PNP-F001.md"
    make_docx(md,out/"PNP-F001.docx");verify(md,out/"PNP-F001.docx")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir",required=True,type=Path);p.add_argument("--lean",default="lean")
    a=p.parse_args();r=run(a.output_dir,a.lean);print(json.dumps(r,indent=2))
    if r["status"]!="KERNEL_VERIFIED_SCOPED_PROJECTION":raise SystemExit(1)
