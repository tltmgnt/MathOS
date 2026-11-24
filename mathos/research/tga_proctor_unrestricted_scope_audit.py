"""Pinned Lean kernel replay and independent scope controls."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from mathos.research.tga_proctor_unrestricted_scope import controls

ROOT=Path(__file__).resolve().parents[2]
NAMES=("dot_comm_scope","dot_add_right_scope","bx_three","row_closed",
       "system_closed","or_not_affine_projection","clause_encoding_correct","clause_gate_iff")


def run(out,lean):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/"artifacts"):
        raise ValueError("output path")
    out.mkdir(parents=True,exist_ok=False)
    version=subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if version.returncode or not re.search(r"\bversion 4\.14\.0\b",version.stdout):
        raise RuntimeError("Lean 4.14.0 required")
    paths=[ROOT/"formal"/n for n in ("ProctorGF2.lean","ProctorUnrestrictedScope.lean")]
    src=[p.read_text() for p in paths]
    target=out/"Scope.lean"
    target.write_text("\n".join(src),encoding="utf-8")
    proc=subprocess.run([lean,"-DwarningAsError=true",str(target)],
                        capture_output=True,text=True,timeout=120)
    log=proc.stdout+proc.stderr
    (out/"kernel.txt").write_text(log,encoding="utf-8")
    audit={n:next((line for line in log.splitlines()
                   if line.startswith("'ProctorUnrestrictedScope."+n+"' ")),None)
           for n in NAMES}
    strict=all(audit[n]=="'ProctorUnrestrictedScope."+n+"' does not depend on any axioms"
               for n in NAMES)
    # The mathematical scope declarations use the existing GF2 list semantics.
    # Require empty dependency lists; do not accept sorryAx or new assumptions.
    ok=proc.returncode==0 and strict
    report={"status":"KERNEL_VERIFIED_AFFINE_SCOPE" if ok else "UNVERIFIED",
            "lean_version":version.stdout.strip(),"exit_code":proc.returncode,
            "axiom_gate":strict,"audit":audit,"controls":controls(),
            "source_hashes":{p.name:hashlib.sha256(s.encode()).hexdigest()
                             for p,s in zip(paths,src)},
            "machine_refinement_verified":False,"python_refinement_verified":False,
            "unrestricted_polynomial_time_verified":False,
            "general_cnf_compiler_formally_verified":False,
            "independent_review":False,"global_promotion":"NONE"}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir",required=True,type=Path)
    p.add_argument("--lean",default="lean")
    args=p.parse_args()
    report=run(args.output_dir,args.lean)
    print(json.dumps(report,indent=2))
    if report["status"]!="KERNEL_VERIFIED_AFFINE_SCOPE":
        raise SystemExit(1)
