"""F016: instrumented total structural Boolean-tape solver."""
import argparse
import json
from itertools import product
from pathlib import Path
import re
import subprocess

from mathos.research import tga_proctor_tape_solver as prior
from mathos.research import tga_proctor_pnp_tape_integration as integration
from scripts.millennium_docx import make_docx, verify

NAMES = ("preTape_bound", "affineTape_mono", "totalTape_mono",
         "finishTotalTape", "solveTotalTape", "totalTape_valid",
         "totalTape_bound", "totalTape_input_bound")


def pre_charge(n,r,scans,pads,generated):
    return 4*scans+4*pads+(4*n+4)*generated+4*n+2*r+2


def budget(n,r,q,m):
    return pre_charge(n,r,3*q,n*n,n)+prior.bound(n,m)+4*q+4*n+5*(2*n+r+1)


def input_size(n,r,q):
    return 1+n+r+2*q+r*(n+1)


def contains_count(y,ys):
    visits=0
    for b in ys:
        visits+=1
        if y==b:
            return True,visits
    return False,visits


def build_domains(ds):
    # Mirrors F012 buildLocal/buildDomains: map gate, two short-circuit
    # membership passes, prefix-pad tail rows, then materialize width n.
    local=[]
    scans=0
    for d in ds:
        ys=[integration.gate(p) for p in d]
        f,a=contains_count(False,ys)
        t,b=contains_count(True,ys)
        scans+=len(d)+a+b
        if not f and not t:
            local.append([([],True)])
        elif f!=t:
            local.append([([True],t)])
        else:
            local.append([])
    rows=[]
    pads=0
    for part in reversed(local):
        pads+=len(rows)
        rows=part+[([False]+a,b) for a,b in rows]
    n=len(ds)
    rows=[(tuple(a+[False]*(n-len(a))),b) for a,b in rows]
    return rows,scans,pads


def solve(domains,rows):
    ds,rs=integration.normalize(domains,rows)
    n,r=len(ds),len(rs)
    extra,scans,pads=build_domains(ds)
    aug=rs+tuple(extra)
    pre=pre_charge(n,r,scans,pads,len(extra))
    (sat,payload),affine=prior.mirror_cells(n,aug)
    lifting=0
    if sat:
        ps=[]
        visits=0
        for d,y in zip(ds,payload):
            for p in d:
                visits+=1
                if integration.gate(p)==y:
                    ps.append(p)
                    break
            else:
                raise AssertionError("unliftable affine output")
        lifting=4*visits+4*n
        wire=[True]+[bool(b) for p in ps for b in p]
    else:
        wire=[False]+list(payload)
    construction=3*len(wire)
    # Explicit counted copy; the construction charge is per emitted cell.
    copied=[]
    copying=0
    for b in wire:
        copied.append(b)
        copying+=2
    return {"wire":copied,"preprocess":pre,"affine":affine,
            "lifting":lifting,"construction":construction,"copying":copying,
            "total":pre+affine+lifting+construction+copying}


def cases():
    yield from integration.cases()
    pairs=integration.PAIRS
    yield ((pairs[0],)*20+(pairs[3],),), (((True,),True),)
    yield ((pairs[3],)*20+(pairs[0],),), (((True,),False),)
    yield ((),pairs,pairs,pairs), ()
    yield (pairs,)*5, ()
    yield (), (((),True),((),False))
    yield (pairs,)*4, tuple(((True,False,True,False),b) for b in (False,True))


def fixtures():
    data=[]
    counts={"systems":0,"sat":0,"unsat":0}
    for k in ("preprocess","affine","lifting","construction","copying","total"):
        counts[k+"_sum"]=0
    for ds,rs in cases():
        result=solve(ds,rs)
        w=result["wire"]
        reference=integration.solve(ds,rs)
        brute=any(all(integration.dot(a,tuple(map(integration.gate,ps)))==b for a,b in rs)
                  for ps in product(*ds))
        assert bool(w[0])==brute and integration.verify_wire(ds,rs,w)
        assert w==reference["wire"] and result["affine"]==reference["affine_steps"]
        assert result["copying"]==reference["wire_steps"]
        assert not integration.verify_wire(ds,rs,w[:-1])
        assert not integration.verify_wire(ds,rs,w+[False])
        n,r,q=len(ds),len(rs),sum(map(len,ds))
        extra,scans,pads=build_domains(ds)
        assert tuple(extra)==integration.domain_tapes(ds)
        assert scans<=3*q and pads<=n*n and len(extra)<=n
        assert result["preprocess"]<=pre_charge(n,r,3*q,n*n,n)
        assert result["lifting"]<=4*q+4*n
        assert result["total"]<=budget(n,r,q,r+n)
        S=input_size(n,r,q)
        assert budget(n,r,q,r+n)<=budget(S,S,S,S)==8*S**3+26*S**2+55*S+7
        counts["systems"]+=1
        counts["sat" if brute else "unsat"]+=1
        for k in ("preprocess","affine","lifting","construction","copying","total"):
            counts[k+"_sum"]+=result[k]
        data.append((ds,rs,result))
    return data,counts


def eval_source(data):
    def bit(b): return "true" if b else "false"
    def vec(v): return "["+",".join(map(bit,v))+"]"
    def pair(p): return "("+bit(p[0])+","+bit(p[1])+")"
    es=[]
    for ds,rs,result in data:
        dom="["+",".join("["+",".join(map(pair,d))+"]" for d in ds)+"]"
        rows="["+",".join("⟨"+vec(a)+","+bit(b)+"⟩" for a,b in rs)+"]"
        proof="True.intro"
        for _ in rs: proof="⟨rfl,"+proof+"⟩"
        args=f"{dom} {rows} ({proof})"
        checks=[f"r.wire == {vec(result['wire'])}"]
        checks += [f"r.{k} == {result[k]}" for k in
                   ("preprocess","affine","lifting","construction","copying")]
        checks += [f"ProctorPNP.totalTapeSteps r == {result['total']}"]
        es.append(f"(let r := ProctorPNP.solveTotalTape {args}; "+" && ".join(checks)+")")
    return "\n".join("#eval (["+ ",\n".join(es[i:i+16])+"].all id)" for i in range(0,len(es),16))+"\n"


def run(out,lean):
    out = Path(out).resolve()
    if out.is_relative_to(prior.ROOT) and not out.is_relative_to(prior.ROOT/"artifacts"):
        raise ValueError("output path")
    out.mkdir(parents=True,exist_ok=False)
    v = subprocess.run([lean,"--version"],capture_output=True,text=True,timeout=30)
    if v.returncode or not re.search(r"\bversion 4\.14\.0\b",v.stdout):
        raise RuntimeError("Lean 4.14.0 required")
    files = ("ProctorGF2.lean","ProctorGF2Solver.lean","ProctorGF2Certificate.lean",
             "ProctorGF2Checker.lean","ProctorPNPProjection.lean","ProctorPNPEncoding.lean",
             "ProctorGF2Codec.lean","ProctorGF2Highest.lean","ProctorGF2Global.lean",
             "ProctorGF2Cost.lean","ProctorPNPEndToEnd.lean","ProctorPNPFullCost.lean",
             "ProctorBitCells.lean","ProctorTapeSolver.lean","ProctorPNPTapeIntegration.lean","ProctorPNPTotalTapeCost.lean")
    src = [(prior.ROOT/"formal"/p).read_text() for p in files]
    combined = "import Init.Data.Nat.Bitwise.Lemmas\n"+"\n".join(s.removeprefix("import Init\n") for s in src)
    strict = prior.GF_NAMES+prior.SOLVER_NAMES+prior.CERT_NAMES+prior.CHECK_NAMES
    lib = prior.MASK_NAMES+prior.CODEC_NAMES+prior.HIGHEST_NAMES+prior.GLOBAL_NAMES+prior.COST_NAMES+prior.CELL_NAMES+prior.TAPE_NAMES
    formal = prior.check(combined,out/"total-tape",lean,strict+lib,"ProctorGF2")
    log = (out/"total-tape/kernel.txt").read_text()
    def allowed(ns,n,strict=False):
        head = "'"+ns+"."+n+"' "
        line = next((l for l in log.splitlines() if l.startswith(head)),None)
        if line == head+"does not depend on any axioms": return True
        prefix = head+"depends on axioms: ["
        return bool(not strict and line and line.startswith(prefix) and line.endswith("]")
                    and set(line[len(prefix):-1].split(", ")) <= {"propext","Quot.sound"})
    old_ok = all(allowed("ProctorGF2",n,True) for n in strict)
    library_ok = all(allowed("ProctorGF2",n) for n in lib)
    domain_ok = all(allowed("ProctorPNP",n,True) for n in prior.PNP_NAMES+prior.DOMAIN_NAMES)
    new_names = prior.END_NAMES+prior.FULL_NAMES+prior.WIRE_NAMES+integration.NAMES+NAMES
    new_audit = {n:next((l for l in log.splitlines() if l.startswith("'ProctorPNP."+n+"' ")),None) for n in new_names}
    new_ok = all(allowed("ProctorPNP",n) for n in new_names)
    passed = formal["exit_code"] == 0 and old_ok and library_ok and domain_ok and new_ok
    data,counts = fixtures()
    report = {"status":"UNVERIFIED","formal":formal,"controls":counts,"new_audit":new_audit,
              "strict_prior_gate":old_ok,"library_gate":library_ok,"strict_domain_gate":domain_ok,
              "new_gate":new_ok,"lean_version":v.stdout.strip(),
              "source_hashes":{p:prior.digest(s.encode()) for p,s in zip(files,src)},
              "provider":"deterministic_specialist_replay","live_ai":False,"global_promotion":"NONE",
              "formal_bit_cost_verified":False,"python_program_refinement_verified":False,
              "structural_total_charge_verified":passed,
              "remaining":["input parsing and machine-level simulation",
                           "Python execution refinement","allocator and counter overhead"]}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    if passed:
        p = out/"CrossLanguage.lean"
        p.write_text(combined+"\n"+eval_source(data),encoding="utf-8")
        r = subprocess.run([lean,"-DwarningAsError=true",str(p)],capture_output=True,text=True,timeout=240)
        log = r.stdout+r.stderr
        (out/"cross-language.txt").write_text(log)
        observed = [l for l in log.splitlines() if l in ("true","false")]
        ok = r.returncode == 0 and observed == ["true"]*((len(data)+15)//16)
        report["cross_language"] = {"passed":ok,"cases":len(data),"batches":len(observed),
                                    "exit_code":r.returncode,"diagnostic":log[-3000:]}
        report["status"] = "KERNEL_VERIFIED_TOTAL_STRUCTURAL_TAPE_COST" if ok else "FORMAL_VERIFIED_CROSS_LANGUAGE_FAILED"
        (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    md = prior.ROOT/"docs/research/tga-universal/PNP-F016.md"
    make_docx(md,out/"PNP-F016.docx")
    verify(md,out/"PNP-F016.docx")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--lean",default="lean")
    args = p.parse_args()
    report = run(args.output_dir,args.lean)
    print(json.dumps(report,indent=2))
    if report["status"] != "KERNEL_VERIFIED_TOTAL_STRUCTURAL_TAPE_COST":
        raise SystemExit(1)
