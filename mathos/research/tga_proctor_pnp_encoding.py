"""PNP-F006: exact domain encoding and natural-number bitmask representation replay."""
import argparse
import json
from itertools import product
from pathlib import Path
import re
import subprocess
from mathos.research.tga_proctor_gf2_checker import ROOT,NAMES as CHECK_NAMES
from mathos.research.tga_proctor_gf2_certificate import NAMES as CERT_NAMES
from mathos.research.tga_proctor_gf2_solver import NAMES as SOLVER_NAMES
from mathos.research.tga_proctor_gf2 import NAMES as GF_NAMES,check,digest
from mathos.research.tga_proctor_pnp import NAMES as PNP_NAMES
from mathos.research.breakthrough_cycle6 import solve_blocks,verify_result
from scripts.millennium_docx import make_docx,verify
NAMES=("decode_xor","decode_dot","decode_shift","maskSat_iff")
DOMAIN_NAMES=("domain_spec","encoded_iff","encoded_unsat")

def domain_rows(blocks):
    result=[]
    for j,block in enumerate(blocks):
        values={a*b for a,b in block}
        if not values:result.append((0,1))
        elif len(values)==1:result.append((1<<j,next(iter(values))))
    return result

def controls():
    pairs=list(product((0,1),repeat=2))
    domains=[tuple(p for j,p in enumerate(pairs) if mask>>j&1) for mask in range(16)]
    cases=sat=0
    for blocks in product(domains,repeat=3):
        rows=[(3,0),(6,1)]
        eq=rows+domain_rows(blocks)
        a={tuple(a*b for a,b in ps) for ps in product(*blocks)
           if all(sum((u*v)<<j for j,(u,v) in enumerate(ps)).__and__(m).bit_count()%2==r for m,r in rows)}
        b={ys for ys in product((0,1),repeat=3)
           if all((m&sum(v<<i for i,v in enumerate(ys))).bit_count()%2==r for m,r in eq)}
        assert a==b
        r=solve_blocks(blocks,rows)
        assert verify_result(blocks,rows,r) and r["sat"]==bool(a)
        sat+=bool(a);cases+=1
    bit_cases=0
    for n in range(7):
        for a,b in product(range(1<<n),repeat=2):
            av=[(a>>i)&1 for i in range(n)];bv=[(b>>i)&1 for i in range(n)]
            assert [(a^b)>>i&1 for i in range(n)]==[u^v for u,v in zip(av,bv)]
            assert (a&b).bit_count()%2==sum(u*v for u,v in zip(av,bv))%2
            for s in (0,1,n):
                assert [(a>>s)>>i&1 for i in range(n)]==[(a>>(s+i))&1 for i in range(n)]
            bit_cases+=1
    return {"domain_cases":cases,"sat":sat,"unsat":cases-sat,"bitmask_pairs":bit_cases,
            "scope":"finite implementation controls only"}

def run(out,lean):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/"artifacts"):raise ValueError("output path")
    out.mkdir(parents=True,exist_ok=False)
    v=subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if v.returncode or not re.search(r"\bversion 4\.14\.0\b",v.stdout):raise RuntimeError("Lean 4.14.0 required")
    paths=[ROOT/"formal"/n for n in ("ProctorGF2.lean","ProctorGF2Solver.lean","ProctorGF2Certificate.lean","ProctorGF2Checker.lean","ProctorPNPProjection.lean","ProctorPNPEncoding.lean")]
    src=[p.read_text() for p in paths]
    base=src[0]+"\n"+"\n".join(s.removeprefix("import Init\n") for s in src[1:5])
    # Same module definitions, explicit import of core Nat bitwise lemmas.
    combined="import Init.Data.Nat.Bitwise.Lemmas\n"+base.removeprefix("import Init\n")+"\n"+src[5]
    formal=check(combined,out/"encoding",lean,GF_NAMES+SOLVER_NAMES+CERT_NAMES+CHECK_NAMES+NAMES,"ProctorGF2")
    log=(out/"encoding/kernel.txt").read_text()
    audit={n:next((l for l in log.splitlines() if l.startswith("'ProctorPNP."+n+"' ")),None) for n in PNP_NAMES+DOMAIN_NAMES}
    domain_ok=all(audit[n]=="'ProctorPNP."+n+"' does not depend on any axioms" for n in audit)
    prior_ok=all(formal["axioms"][n]=="'ProctorGF2."+n+"' does not depend on any axioms" for n in GF_NAMES+SOLVER_NAMES+CERT_NAMES+CHECK_NAMES)
    # Library-backed proof status is distinct from strict axiom-free acceptance.
    library_ok=all(formal["axioms"][n] in ("'ProctorGF2."+n+"' does not depend on any axioms",
        "'ProctorGF2."+n+"' depends on axioms: [propext, Quot.sound]") for n in NAMES)
    compiled=formal["exit_code"]==0
    report={"status":"KERNEL_VERIFIED_DOMAIN_AND_LIBRARY_MASK" if compiled and domain_ok and prior_ok and library_ok else "UNVERIFIED",
            "domain_strict_gate":compiled and domain_ok,"prior_strict_gate":compiled and prior_ok,
            "mask_library_gate":compiled and library_ok,"mask_empty_axiom_gate":formal["accepted"],
            "library_policy":"Reported separately; propext and Quot.sound accepted only for library-dependent kernel verification, not the existing strict empty-axiom gate.",
            "formal":formal,"domain_audit":audit,"controls":controls(),"lean_version":v.stdout.strip(),
            "source_hashes":{p.name:digest(s.encode()) for p,s in zip(paths,src)},
            "provider":"deterministic_specialist_replay","live_ai":False,"global_promotion":"NONE",
            "python_program_refinement_verified":False,"formal_bit_cost_verified":False,
            "remaining":["Python program semantics/refinement","formal parity-popcount and full mask codec roundtrip","formal total bit cost"]}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    md=ROOT/"docs/research/tga-universal/PNP-F006.md"
    make_docx(md,out/"PNP-F006.docx");verify(md,out/"PNP-F006.docx")
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--lean",default="lean")
    a=p.parse_args();r=run(a.output_dir,a.lean);print(json.dumps(r,indent=2))
    if r["status"]!="KERNEL_VERIFIED_DOMAIN_AND_LIBRARY_MASK":raise SystemExit(1)
