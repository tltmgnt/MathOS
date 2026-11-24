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
NAMES=("highest_bit","highest_descent","pivot_strict_decrease","next_pivot_lower","mask_replace","provenance_xor","provenance_refutes","unit_dot","flip_coordinate","backstep_pivot","backstep_preserves_lower","fresh_or_xor")
def trace(n,rows):
    """Instrumented mirror of B006 affine core; not a verified Python semantics."""
    basis={};steps=0;lower_checks=0
    def original(w):
        a=b=0
        for i,(u,v) in enumerate(rows):
            if w>>i&1:a^=u;b^=v
        return a,b
    for j,(a,b) in enumerate(rows):
        w=1<<j;last=n
        while a:
            p=a.bit_length()-1
            assert p<last and original(w)==(a,b)
            last=p
            if p not in basis:
                basis[p]=(a,b,w);break
            u,v,z=basis[p]
            assert u.bit_length()-1==p
            a,b,w=a^u,b^v,w^z
            assert a<1<<p and original(w)==(a,b)
            steps+=1
        if not a and b:
            assert original(w)==(0,1)
            return False,w,steps,lower_checks
    x=0;prior=[]
    for p,(a,b,w) in sorted(basis.items()):
        assert x<1<<p and original(w)==(a,b)
        if (a&x).bit_count()%2!=b:
            assert x|(1<<p)==x^(1<<p)
            x|=1<<p
        assert (a&x).bit_count()%2==b
        for u,v in prior:
            assert (u&x).bit_count()%2==v
            lower_checks+=1
        prior.append((a,b))
    assert all((a&x).bit_count()%2==b for a,b in rows)
    return True,x,steps,lower_checks

def controls():
    from mathos.research.breakthrough_cycle6 import solve_blocks,verify_result
    pairs=[(0,0),(0,1),(1,0),(1,1)]
    count=sat=xors=lower=0
    for n in range(4):
        universe=list(product(range(1<<n),(0,1)))
        for m in range(4):
            for rows in product(universe,repeat=m):
                yes,w,steps,lc=trace(n,rows)
                actual=solve_blocks([pairs]*n,rows)
                assert verify_result([pairs]*n,rows,actual)
                assert yes==actual["sat"] and steps==actual["row_xors"]
                if yes:assert w==sum((a*b)<<i for i,(a,b) in enumerate(actual["witness"]))
                else:assert w==sum(1<<i for i in actual["xor_certificate"])
                count+=1;sat+=yes;xors+=steps;lower+=lc
    return {"systems":count,"sat":sat,"unsat":count-sat,"row_xor_steps":xors,"lower_row_checks":lower,
            "scope":"finite trace mirror compared with actual B006 outputs; not full program refinement"}
def run(out,lean):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/"artifacts"):raise ValueError("output path")
    out.mkdir(parents=True,exist_ok=False)
    v=subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if v.returncode or not re.search(r"\bversion 4\.14\.0\b",v.stdout):raise RuntimeError("Lean 4.14.0 required")
    paths=[ROOT/"formal"/n for n in ("ProctorGF2.lean","ProctorGF2Solver.lean","ProctorGF2Certificate.lean","ProctorGF2Checker.lean","ProctorPNPProjection.lean","ProctorPNPEncoding.lean","ProctorGF2Codec.lean","ProctorGF2Highest.lean")]
    src=[p.read_text() for p in paths]
    combined="import Init.Data.Nat.Bitwise.Lemmas\n"+"\n".join(s.removeprefix("import Init\n") for s in src)
    strict=GF_NAMES+SOLVER_NAMES+CERT_NAMES+CHECK_NAMES
    formal=check(combined,out/"highest",lean,strict+MASK_NAMES+CODEC_NAMES+NAMES,"ProctorGF2")
    log=(out/"highest/kernel.txt").read_text()
    domain={n:next((l for l in log.splitlines() if l.startswith("'ProctorPNP."+n+"' ")),None) for n in PNP_NAMES+DOMAIN_NAMES}
    def allowed(ns,n,line,strict=False):
        head="'"+ns+"."+n+"' "
        if line==head+"does not depend on any axioms":return True
        if strict or not isinstance(line,str) or not line.startswith(head+"depends on axioms: [") or not line.endswith("]"):return False
        names=set(line[len(head+"depends on axioms: ["):-1].split(", "))
        return bool(names) and names<={"propext","Quot.sound"}
    old_ok=all(allowed("ProctorGF2",n,formal["axioms"][n],True) for n in strict)
    domain_ok=all(allowed("ProctorPNP",n,line,True) for n,line in domain.items())
    library_ok=all(allowed("ProctorGF2",n,formal["axioms"][n]) for n in MASK_NAMES+CODEC_NAMES+NAMES)
    passed=formal["exit_code"]==0 and old_ok and domain_ok and library_ok
    report={"status":"KERNEL_VERIFIED_HIGHEST_PIVOT_INVARIANTS" if passed else "UNVERIFIED",
            "formal":formal,"domain_audit":domain,"controls":controls(),"lean_version":v.stdout.strip(),
            "strict_prior_gate":old_ok,"strict_domain_gate":domain_ok,"library_gate":library_ok,
            "source_hashes":{p.name:digest(s.encode()) for p,s in zip(paths,src)},
            "provider":"deterministic_specialist_replay","live_ai":False,"global_promotion":"NONE",
            "python_program_refinement_verified":False,"formal_bit_cost_verified":False,
            "remaining":["full basis insertion and global Python loop refinement","formal total bit cost"]}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    md=ROOT/"docs/research/tga-universal/PNP-F008.md"
    make_docx(md,out/"PNP-F008.docx");verify(md,out/"PNP-F008.docx")
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--lean",default="lean")
    a=p.parse_args();r=run(a.output_dir,a.lean);print(json.dumps(r,indent=2))
    if r["status"]!="KERNEL_VERIFIED_HIGHEST_PIVOT_INVARIANTS":raise SystemExit(1)
