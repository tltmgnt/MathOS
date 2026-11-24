"""F015: disjoint-domain solver with explicit Boolean input and output tapes."""
import argparse
import json
from itertools import product
from pathlib import Path
import re
import subprocess

from mathos.research import tga_proctor_tape_solver as prior
from scripts.millennium_docx import make_docx, verify

NAMES = ("fitRowsTape_exact", "fitRowsTape_sat", "augmentedTape_exact",
         "augmentedTape_length", "augmentedTape_sat", "augmentedTape_refutes",
         "solveBlockTape", "blockTape_valid")
PAIRS = tuple(product((False, True), repeat=2))


def normalize(domains, rows):
    ds = tuple(tuple(tuple(p) for p in d) for d in domains)
    rs = tuple((tuple(a), b) for a, b in rows)
    def bit(v):
        return type(v) in (bool, int) and v in (0, 1)
    if any(len(p) != 2 or not all(map(bit, p)) for d in ds for p in d):
        raise ValueError("invalid domain pair")
    if any(len(a) != len(ds) or not all(map(bit, a)) or not bit(b) for a,b in rs):
        raise ValueError("invalid rectangular coupling row")
    return ds, rs


def gate(p):
    return bool(p[0] and p[1])


def dot(a, x):
    d = False
    for u, v in zip(a, x):
        d ^= bool(u and v)
    return d


def domain_tapes(ds):
    n = len(ds)
    out = []
    for j, d in enumerate(ds):
        seen0 = seen1 = False
        for p in d:
            if gate(p):
                seen1 = True
            else:
                seen0 = True
        if not seen0 and not seen1:
            out.append((tuple(False for _ in ds), True))
        elif seen0 != seen1:
            out.append((tuple(i == j for i in range(n)), seen1))
    return tuple(out)


def solve(domains, rows):
    ds, rs = normalize(domains, rows)
    augmented = rs + domain_tapes(ds)
    (sat, payload), steps = prior.mirror_cells(len(ds), augmented)
    if sat:
        pairs = [next(p for p in d if gate(p) == y) for d,y in zip(ds,payload)]
        wire = [True] + [bool(b) for p in pairs for b in p]
    else:
        wire = [False] + list(payload)
    # Matches F013's counted output copy, not a host-runtime measurement.
    return {"wire": wire, "affine_steps": steps, "wire_steps": 2*len(wire)}


def verify_wire(domains, rows, wire):
    ds, rs = normalize(domains, rows)
    if not wire or any(type(v) not in (bool,int) or v not in (0,1) for v in wire):
        return False
    tag, *bs = wire
    if tag:
        if len(bs) != 2*len(ds):
            return False
        ps = tuple(zip(bs[::2],bs[1::2]))
        return all(p in d for p,d in zip(ps,ds)) and all(
            dot(a, tuple(map(gate,ps))) == b for a,b in rs)
    aug = rs + domain_tapes(ds)
    if len(bs) != len(aug):
        return False
    coeff = [False]*len(ds)
    rhs = False
    for (a,b),w in zip(aug,bs):
        if w:
            coeff = [u ^ bool(v) for u,v in zip(coeff,a)]
            rhs ^= bool(b)
    return rhs and not any(coeff)


def cases():
    subsets = [tuple(p for p,chosen in zip(PAIRS,sel) if chosen)
               for sel in product((False,True),repeat=4)]
    for ds in product(subsets,repeat=3):
        yield ds, (((True,True,False),False),((False,True,True),True))
    for n in range(3):
        universe = [(a,b) for a in product((False,True),repeat=n) for b in (False,True)]
        for rs in product(universe,repeat=2):
            yield (PAIRS,)*n, rs
    yield (), ()


def fixtures():
    data = []
    sat = unsat = affine = wire = 0
    for ds, rs in cases():
        result = solve(ds,rs)
        w = result["wire"]
        brute = any(all(dot(a,tuple(map(gate,ps))) == b for a,b in rs)
                    for ps in product(*ds))
        assert bool(w[0]) == brute and verify_wire(ds,rs,w)
        assert not verify_wire(ds,rs,w[:-1])
        assert not verify_wire(ds,rs,w+[False])
        assert not verify_wire(ds,rs,[2]+w[1:])
        m = len(rs)+len(domain_tapes(ds))
        assert result["affine_steps"] <= prior.bound(len(ds),m)
        assert len(w) <= 2*len(ds)+len(rs)+1
        assert result["wire_steps"] == 2*len(w)
        sat += brute
        unsat += not brute
        affine += result["affine_steps"]
        wire += result["wire_steps"]
        data.append((ds,rs,result))
    return data, {"systems":len(data),"sat":sat,"unsat":unsat,
                  "affine_steps_sum":affine,"wire_steps_sum":wire}


def eval_source(data):
    def bit(b): return "true" if b else "false"
    def vec(v): return "["+",".join(map(bit,v))+"]"
    def pair(p): return "("+bit(p[0])+","+bit(p[1])+")"
    es = []
    for ds,rs,result in data:
        dom = "["+",".join("["+",".join(map(pair,d))+"]" for d in ds)+"]"
        rows = "["+",".join("⟨"+vec(a)+","+bit(b)+"⟩" for a,b in rs)+"]"
        proof = "True.intro"
        for _ in rs: proof = "⟨rfl,"+proof+"⟩"
        args = f"{dom} {rows} ({proof})"
        es.append(f"(let r := ProctorPNP.solveBlockTape {args}; "
                  f"r.wire == {vec(result['wire'])} && r.affineSteps == {result['affine_steps']} "
                  f"&& r.wireSteps == {result['wire_steps']})")
    return "\n".join("#eval (["+ ",\n".join(es[i:i+24])+"].all id)" for i in range(0,len(es),24))+"\n"


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
             "ProctorBitCells.lean","ProctorTapeSolver.lean","ProctorPNPTapeIntegration.lean")
    src = [(prior.ROOT/"formal"/p).read_text() for p in files]
    combined = "import Init.Data.Nat.Bitwise.Lemmas\n"+"\n".join(s.removeprefix("import Init\n") for s in src)
    strict = prior.GF_NAMES+prior.SOLVER_NAMES+prior.CERT_NAMES+prior.CHECK_NAMES
    lib = prior.MASK_NAMES+prior.CODEC_NAMES+prior.HIGHEST_NAMES+prior.GLOBAL_NAMES+prior.COST_NAMES+prior.CELL_NAMES+prior.TAPE_NAMES
    formal = prior.check(combined,out/"integration",lean,strict+lib,"ProctorGF2")
    log = (out/"integration/kernel.txt").read_text()
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
    new_names = prior.END_NAMES+prior.FULL_NAMES+prior.WIRE_NAMES+NAMES
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
              "remaining":["counted domain preprocessing and witness lifting",
                           "finite-state simulation","Python execution refinement"]}
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    if passed:
        p = out/"CrossLanguage.lean"
        p.write_text(combined+"\n"+eval_source(data),encoding="utf-8")
        r = subprocess.run([lean,"-DwarningAsError=true",str(p)],capture_output=True,text=True,timeout=240)
        log = r.stdout+r.stderr
        (out/"cross-language.txt").write_text(log)
        observed = [l for l in log.splitlines() if l in ("true","false")]
        ok = r.returncode == 0 and observed == ["true"]*((len(data)+23)//24)
        report["cross_language"] = {"passed":ok,"cases":len(data),"batches":len(observed),
                                    "exit_code":r.returncode,"diagnostic":log[-3000:]}
        report["status"] = "KERNEL_VERIFIED_DOMAIN_TAPE_INTEGRATION" if ok else "FORMAL_VERIFIED_CROSS_LANGUAGE_FAILED"
        (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    md = prior.ROOT/"docs/research/tga-universal/PNP-F015.md"
    make_docx(md,out/"PNP-F015.docx")
    verify(md,out/"PNP-F015.docx")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--lean",default="lean")
    args = p.parse_args()
    report = run(args.output_dir,args.lean)
    print(json.dumps(report,indent=2))
    if report["status"] != "KERNEL_VERIFIED_DOMAIN_TAPE_INTEGRATION":
        raise SystemExit(1)
