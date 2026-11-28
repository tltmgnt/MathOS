"""Exact archived paired preservation check for indexed search portfolio."""
import argparse
import json
from pathlib import Path
from . import pnp_bucket_cdcl_portfolio as candidate
from . import pnp_indexed_rup_portfolio as baseline
from .pnp_native_xor_frontier import manifest,reference
from .pnp_failure_synthesis import audit as audit_v13
from .pnp_evidence_benchmark import digest
from .pnp_evidence_scheduler import train
from .pnp_outcome_engine import checkpoint

TOTAL,SECONDS=100_000,5


def run(source,scheduler,failures,path):
    audit_v13(source,scheduler,failures)
    policy,plan=train(source),failures["selected_plan"]
    rows=[]
    for c in manifest():
        n,f=c["n"],c["clauses"]
        a=baseline.solve(n,f,policy,plan,total=TOTAL,seconds=SECONDS)
        b=candidate.solve(n,f,policy,plan,total=TOTAL,seconds=SECONDS)
        rows.append({"case":c,"baseline":a,"candidate":b})
    r={"upstream":[digest(x) for x in (source,scheduler,failures)],"rows":rows}
    checkpoint(path,r)
    return r


def audit(source,scheduler,failures,r):
    audit_v13(source,scheduler,failures)
    policy,plan=train(source),failures["selected_plan"]
    cases=manifest()
    if len(cases)!=191 or len(r["rows"])!=len(cases) or r["upstream"]!=[digest(x) for x in (source,scheduler,failures)]:
        raise ValueError("archived manifest mismatch")
    counts={"baseline":0,"candidate":0,"eligible":0}
    for c,row in zip(cases,r["rows"]):
        if c!=row["case"]:
            raise ValueError("case mismatch")
        n,f=c["n"],c["clauses"]
        for k,engine in (("baseline",baseline),("candidate",candidate)):
            p=row[k]
            if (p["total_steps"],p["seconds"])!=(TOTAL,SECONDS):
                raise ValueError("unequal budget")
            engine.verify(n,f,policy,plan,p)
            if p["decision"]=="unknown" or (p["decision"]=="sat")!=reference(c):
                raise ValueError("archived decision loss or disagreement")
            counts[k]+=1
        counts["eligible"]+=row["candidate"]["eligible"]
    return counts


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("benchmark","scheduler","failures"):
        p.add_argument("--"+name,type=Path,required=True)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--checkpoint",type=Path)
    mode.add_argument("--audit",type=Path)
    a=p.parse_args()
    paths=[a.benchmark,a.scheduler,a.failures]
    def read(p):
        if p.stat().st_size>128_000_000:
            raise ValueError("report size cap")
        return json.loads(p.read_text(encoding="utf-8"))
    up=[read(p) for p in paths]
    if a.checkpoint:
        if a.checkpoint.resolve() in {p.resolve() for p in paths}:
            raise ValueError("cannot overwrite upstream")
        r=run(*up,a.checkpoint)
    else:
        r=read(a.audit)
    print(json.dumps(audit(*up,r),sort_keys=True))


if __name__=="__main__":
    main()
