"""Frozen out-of-development synthetic evaluation of unchanged v18.
This is independent generator/reference logic, NOT an external blind corpus.
Do not tune or update a library using these cases.
"""
import argparse
import json
import random
from pathlib import Path
from itertools import combinations
from mathos.research.pnp_evidence_benchmark import digest
from mathos.research.pnp_evidence_scheduler import train
from mathos.research.pnp_library_frontier import audit as audit_library, case_key
from mathos.research.pnp_unified_discovery_frontier_v18 import ARMS, isolated, replay_arm

SEED=180831
BASE="103991fbe57b808c042356aaa5e7058f48f616e8"
SCHEMA="mathos-pnp-v18-frozen-synthetic/1"


def exhaustive(n, f):
    # Integer truth-table masks, independent of MathOS certificate routes.
    if n>16:
        raise ValueError("exhaustive reference bound")
    m=1<<n
    mask=(1<<m)-1
    positives=[]
    for v in range(n):
        block=(1<<(1<<v))-1
        bits=0
        for i in range(1<<v,m,1<<(v+1)):
            bits|=block<<i
        positives.append(bits)
    surviving=mask
    for c in f:
        sat=0
        for x in c:
            b=positives[abs(x)-1]
            sat|=b if x>0 else mask^b
        surviving &= sat
        if not surviving:
            return False
    return bool(surviving)


def manifest():
    rng=random.Random(SEED)
    out=[]
    def add(id,family,n,f,sat):
        # Random signed bijection and clause/literal order, preserve truth.
        p=list(range(1,n+1));rng.shuffle(p)
        signed=[x if rng.randrange(2) else -x for x in p]
        g=[[signed[abs(x)-1]*(1 if x>0 else -1) for x in c] for c in f]
        for c in g:rng.shuffle(c)
        rng.shuffle(g)
        if n<=16 and exhaustive(n,g)!=sat:
            raise ValueError("independent truth-table disagreement")
        out.append({"id":id,"family":family,"n":n,"clauses":g,"reference_sat":sat})
    # Pigeonhole m+1 -> m with pairwise at-most-one in each hole.
    # Positive sibling deletes one pigeon existence constraint; use distinct holes.
    for m in (3,4,5,6,7):
        n=m*(m+1)
        v=lambda i,j:i*m+j+1
        units=[[v(i,j) for j in range(m)] for i in range(m+1)]
        atmost=[[-v(i,j),-v(k,j)] for j in range(m) for i,k in combinations(range(m+1),2)]
        for sat in (False,True):
            add(f"php_{m}_{int(sat)}","pigeonhole",n,units[int(sat):]+atmost,sat)
    # Even/odd cycle graph 2-colouring, exact signed binary constraints.
    # Adjacent vertices must differ. Alternating assignment iff length even.
    for n in (17,18,31,32,63,64,127,128):
        f=[]
        for i in range(1,n+1):
            j=i%n+1
            f.extend([[i,j],[-i,-j]])
        add(f"cycle_{n}","cycle2",n,f,n%2==0)
    # Larger fresh pure 3-CNF cases around density 4.25, truth tables as oracle.
    for n in (12,14,16):
        for i in range(4):
            f=[[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3)]
               for _ in range(round(n*4.25))]
            add(f"random3_{n}_{i}","random3",n,f,exhaustive(n,f))
    return out


def inputs(source,scheduler,failures,lr,dev):
    audit_library(source,scheduler,failures,lr)
    if dev["upstream"]!=[digest(x) for x in (source,scheduler,failures,lr)]:
        raise ValueError("development evidence provenance mismatch")
    forbidden={case_key(r["case"]) for r in source["rows"]}
    for k in ("training","evaluation"):
        forbidden.update(case_key(r["case"]) for r in failures[k])
    for k in ("training","retrospective","discovery","heldout"):
        forbidden.update(case_key(r["case"]) for r in lr[k])
    forbidden.update(case_key(r["case"]) for r in dev["rows"])
    rows=manifest()
    keys=[case_key(c) for c in rows]
    if len(set(keys))!=len(keys) or forbidden.intersection(keys):
        raise ValueError("normalized input overlap")
    policy=train(source)
    if (digest(lr["library"])!="e3a6ce6c5e148e95e9760c4c924be2f9457e6ff98c864efab6ff5b93570adb03"
            or digest(lr["v15_source_templates"])!="c7d31f4cb372ffdfd3106d632249313221f0192c16c8b02e6494279d6f0659d9"
            or digest(policy)!="c5f6ee569aa050f4077b83d1ab4a58642fabbcb59cc1fa653e5d92d131475898"
            or failures["selected_plan"]!=["min_product",8]):
        raise ValueError("frozen release policy/library mismatch; do not score")
    return rows,policy,failures["selected_plan"],lr["v15_source_templates"],lr["library"]


def summary(rows):
    out={}
    for family in ("all","pigeonhole","cycle2","random3"):
        rs=[r for r in rows if family=="all" or r["case"]["family"]==family]
        out[family]={}
        for arm in ARMS:
            xs=[r["arms"][arm] for r in rs]
            out[family][arm]={**{d:sum(x["result"]["decision"]==d for x in xs) for d in ("sat","unsat","unknown")},
                              "wall_seconds":sum(x["wall_seconds"] for x in xs)}
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("benchmark","scheduler","failures","library","development"):
        p.add_argument("--"+k,type=Path,required=True)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--checkpoint",type=Path)
    mode.add_argument("--audit",type=Path)
    a=p.parse_args()
    paths=[a.benchmark,a.scheduler,a.failures,a.library,a.development]
    data=[json.loads(x.read_text()) for x in paths]
    rows,policy,plan,old,lib=inputs(*data)
    meta={"schema":SCHEMA,"seed":SEED,"candidate_base":BASE,"manifest_sha256":digest(rows),
          "upstream":[digest(x) for x in data],"library_sha256":digest(lib),
          "scope":"frozen_synthetic_not_blinded_or_orbit_disjoint","universal_obligation":"unresolved"}
    def verdict(c,x):
        d=x["result"]["decision"]
        if d not in ("sat","unsat","unknown") or (d!="unknown" and (d=="sat")!=c["reference_sat"]):
            raise ValueError("false or invalid verdict")
    if a.audit:
        r=json.loads(a.audit.read_text())
        if any(r[k]!=v for k,v in meta.items()) or r["completion"]!="completed" or [x["case"] for x in r["rows"]]!=rows:
            raise ValueError("manifest or metadata mismatch")
        for row in r["rows"]:
            c=row["case"]
            if set(row["arms"])!=set(ARMS):raise ValueError("missing arm")
            for arm,x in row["arms"].items():
                replay_arm(arm,c,policy,plan,old,lib,x["result"])
                verdict(c,x)
        if r["summary"]!=summary(r["rows"]):raise ValueError("summary mismatch")
        print(json.dumps({"status":"positive_claims_replayed"}))
        return
    if a.checkpoint.resolve() in {x.resolve() for x in paths}:p.error("cannot overwrite source evidence")
    a.checkpoint.parent.mkdir(parents=True,exist_ok=True)
    r={**meta,"completion":"running","rows":[]}
    def save():
        t=a.checkpoint.with_suffix(".tmp");t.write_text(json.dumps(r,sort_keys=True,indent=2));t.replace(a.checkpoint)
    save()
    for i,c in enumerate(rows):
        row={"case":c,"arms":{}}
        for arm in ARMS[i%len(ARMS):]+ARMS[:i%len(ARMS)]:
            # Neither reference truth nor family/id enters the worker.
            req={"arm":arm,"case":{"n":c["n"],"clauses":c["clauses"]},
                 "policy":policy,"plan":plan,"old":old,"library":lib}
            x=isolated(req);verdict(c,x);row["arms"][arm]=x
        r["rows"].append(row);save()
    if digest(lib)!=meta["library_sha256"]:raise ValueError("library mutated")
    r["summary"]=summary(r["rows"]);r["completion"]="completed";save()
    print(json.dumps(r["summary"],sort_keys=True,indent=2))


if __name__=="__main__":main()
