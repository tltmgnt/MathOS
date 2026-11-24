"""F007: codec, counting parity and original-row mask certificate transport."""
import argparse
import json
from itertools import product
from pathlib import Path
import re
import subprocess
from mathos.research.tga_proctor_pnp_encoding import ROOT,NAMES as MASK_NAMES,DOMAIN_NAMES
from mathos.research.tga_proctor_gf2_checker import NAMES as CHECK_NAMES
from mathos.research.tga_proctor_gf2_certificate import NAMES as CERT_NAMES
from mathos.research.tga_proctor_gf2_solver import NAMES as SOLVER_NAMES,certificate_solver,verify_result
from mathos.research.tga_proctor_gf2 import NAMES as GF_NAMES,digest,check
from mathos.research.tga_proctor_pnp import NAMES as PNP_NAMES
from scripts.millennium_docx import make_docx,verify
NAMES=("decode_encode","encode_decode_mod","encode_decode_exact","encode_bound","count_parity","dot_count","count_decode","count_stable","mask_lhs","mask_rhs","mask_certificate_sound")
def decode(n,a,k=0):return [(a>>(k+i))&1 for i in range(n)]
def encode(bs):return sum(b<<i for i,b in enumerate(bs))
def count(n,a,k=0):return sum(decode(n,a,k))
def controls():
    codec=0
    for n in range(9):
        for a in range(1<<(n+2)):
            bs=decode(n,a)
            assert encode(bs)==a%(1<<n) and decode(n,encode(bs))==bs
            assert count(n,a)==(a% (1<<n)).bit_count()
            if a<(1<<n):
                assert count(n+5,a)==a.bit_count()
            codec+=1
    parity=0
    for n in range(7):
        for a,b in product(range(1<<n),repeat=2):
            assert count(n,a&b)%2==(a&b).bit_count()%2==sum(u*v for u,v in zip(decode(n,a),decode(n,b)))%2
            parity+=1
    systems=dual=0
    for n in range(4):
        rows0=list(product(range(1<<n),(0,1)))
        for m in range(4):
            for rows in product(rows0,repeat=m):
                r=certificate_solver(n,rows)
                assert verify_result(n,rows,r)
                if not r["sat"]:
                    w=encode([int(i in r["certificate"]) for i in range(m)])
                    a=b=0
                    for (u,v),bit in zip(rows,decode(m,w)):
                        if bit:a^=u;b^=v
                    assert (a,b)==(0,1)
                    assert all(count(n,a&x)%2==0 for x in range(1<<n))
                    dual+=1
                systems+=1
    return {"codec_cases":codec,"parity_pairs":parity,"systems":systems,"dual_certificates":dual,
            "scope":"finite Python comparison only; formal statements independently replayed"}
def run(out,lean):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/"artifacts"):raise ValueError("output path")
    out.mkdir(parents=True,exist_ok=False)
    v=subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if v.returncode or not re.search(r"\bversion 4\.14\.0\b",v.stdout):raise RuntimeError("Lean 4.14.0 required")
    paths=[ROOT/"formal"/n for n in ("ProctorGF2.lean","ProctorGF2Solver.lean","ProctorGF2Certificate.lean","ProctorGF2Checker.lean","ProctorPNPProjection.lean","ProctorPNPEncoding.lean","ProctorGF2Codec.lean")]
    src=[p.read_text() for p in paths]
    combined="import Init.Data.Nat.Bitwise.Lemmas\n"+"\n".join(s.removeprefix("import Init\n") for s in src)
    strict=GF_NAMES+SOLVER_NAMES+CERT_NAMES+CHECK_NAMES
    formal=check(combined,out/"codec",lean,strict+MASK_NAMES+NAMES,"ProctorGF2")
    log=(out/"codec/kernel.txt").read_text()
    domain={n:next((l for l in log.splitlines() if l.startswith("'ProctorPNP."+n+"' ")),None) for n in PNP_NAMES+DOMAIN_NAMES}
    def allowed(ns,n,line,strict=False):
        head="'"+ns+"."+n+"' "
        if line==head+"does not depend on any axioms":return True
        if strict or not isinstance(line,str) or not line.startswith(head+"depends on axioms: [") or not line.endswith("]"):return False
        names=set(line[len(head+"depends on axioms: ["):-1].split(", "))
        return bool(names) and names<={"propext","Quot.sound"}
    old_ok=all(allowed("ProctorGF2",n,formal["axioms"][n],True) for n in strict)
    domain_ok=all(allowed("ProctorPNP",n,line,True) for n,line in domain.items())
    library_ok=all(allowed("ProctorGF2",n,formal["axioms"][n]) for n in MASK_NAMES+NAMES)
    passed=formal["exit_code"]==0 and old_ok and domain_ok and library_ok
    report={"status":"KERNEL_VERIFIED_CODEC_AND_MASK_CERTIFICATES" if passed else "UNVERIFIED",
            "formal":formal,"domain_audit":domain,"controls":controls(),"lean_version":v.stdout.strip(),
            "strict_prior_gate":old_ok,"strict_domain_gate":domain_ok,"library_gate":library_ok,
            "source_hashes":{p.name:digest(s.encode()) for p,s in zip(paths,src)},
            "provider":"deterministic_specialist_replay","live_ai":False,"global_promotion":"NONE",
            "python_program_refinement_verified":False,"formal_bit_cost_verified":False,
            "remaining":["Python program semantics/refinement","formal total bit cost"]}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    md=ROOT/"docs/research/tga-universal/PNP-F007.md"
    make_docx(md,out/"PNP-F007.docx");verify(md,out/"PNP-F007.docx")
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--lean",default="lean")
    a=p.parse_args();r=run(a.output_dir,a.lean);print(json.dumps(r,indent=2))
    if r["status"]!="KERNEL_VERIFIED_CODEC_AND_MASK_CERTIFICATES":raise SystemExit(1)
