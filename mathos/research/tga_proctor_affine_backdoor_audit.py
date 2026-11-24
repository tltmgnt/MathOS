"""F027 strict Lean replay and bounded backdoor controls."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from mathos.research.tga_proctor_affine_backdoor import controls

ROOT=Path(__file__).resolve().parents[2]
NAMES=("classify_correct","covered_no_nonlinear","duplicate_literal",
       "tautology_literal","literal_complement","incompatible_units","opposite_units_unsat")


def run(out,lean):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/"artifacts"):
        raise ValueError("output path")
    out.mkdir(parents=True,exist_ok=False)
    v=subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if v.returncode or not re.search(r"\bversion 4\.14\.0\b",v.stdout):
        raise RuntimeError("Lean 4.14.0 required")
    src=(ROOT/"formal"/"ProctorAffineBackdoor.lean").read_text()
    target=out/"Backdoor.lean"
    target.write_text("import Init\n"+src,encoding="utf-8")
    proc=subprocess.run([lean,"-DwarningAsError=true",str(target)],
                        capture_output=True,text=True,timeout=120)
    log=proc.stdout+proc.stderr
    (out/"kernel.txt").write_text(log,encoding="utf-8")
    if proc.returncode:
        print(log)
    audit={n:next((l for l in log.splitlines()
                   if l.startswith("'ProctorAffineBackdoor."+n+"' ")),None)
           for n in NAMES}
    strict=all(audit[n]=="'ProctorAffineBackdoor."+n+"' does not depend on any axioms"
               for n in NAMES)
    report={"status":"KERNEL_VERIFIED_LOCAL_AFFINE_BACKDOOR" if strict and proc.returncode==0 else "UNVERIFIED",
            "lean_version":v.stdout.strip(),"exit_code":proc.returncode,"axiom_gate":strict,
            "audit":audit,"controls":controls(),"source_sha256":hashlib.sha256(src.encode()).hexdigest(),
            "cover_algorithm_formally_verified":False,"python_refinement_verified":False,
            "universal_logarithmic_backdoor_verified":False,
            "unrestricted_polynomial_time_verified":False,"machine_refinement_verified":False,
            "global_promotion":"NONE","independent_review":False}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir",required=True,type=Path)
    p.add_argument("--lean",default="lean")
    a=p.parse_args()
    r=run(a.output_dir,a.lean)
    print(json.dumps(r,indent=2))
    if r["status"]!="KERNEL_VERIFIED_LOCAL_AFFINE_BACKDOOR":
        raise SystemExit(1)
