"""Frozen research comparison: v18 vs experimental matching-first, no solver promotion."""
import argparse
import json
import os
import random
import resource
import signal
import subprocess
import sys
import time
from collections import Counter
from itertools import combinations, product
from pathlib import Path
from independent_pnp_v18_frozen_frontier import exhaustive, manifest as previous_manifest
from mathos.research.pnp_evidence_benchmark import digest
from mathos.research.pnp_evidence_scheduler import train
from mathos.research.pnp_library_frontier import audit as audit_library, case_key
from mathos.research.pnp_unified_discovery_frontier_v18 import (
    isolated, run_arm, replay_arm, cases as development_cases, WALL, MEMORY)
from mathos.research.pnp_structural_kernel import Exhausted
from mathos.research.pnp_matching_certificates import solve, verify

SEED=184729
MANIFEST="8fd7cf8eb5f2a24e814c62179d2dee71e8278d7cd3d9c153d7e3e7a28ca9692e"
LIBRARY="e3a6ce6c5e148e95e9760c4c924be2f9457e6ff98c864efab6ff5b93570adb03"
POLICY="c5f6ee569aa050f4077b83d1ab4a58642fabbcb59cc1fa653e5d92d131475898"
OLD="c7d31f4cb372ffdfd3106d632249313221f0192c16c8b02e6494279d6f0659d9"


def encoding(neighbors, holes):
    groups=[];bucket=[[] for _ in range(holes)];v=0
    for row in neighbors:
        g=[]
        for b in row:
            v+=1;g.append(v);bucket[b].append(v)
        groups.append(g)
    return v,groups+[[-x,-y] for b in bucket for x,y in combinations(b,2)]


def scramble(n,f,rng):
    p=list(range(1,n+1));rng.shuffle(p)
    p=[x if rng.randrange(2) else -x for x in p]
    g=[[p[abs(x)-1]*(1 if x>0 else -1) for x in c] for c in f]
    for c in g:rng.shuffle(c)
    rng.shuffle(g)
    return g


def manifest():
    rng=random.Random(SEED);out=[]
    for h in (3,4,5,6,7,8):
        for sat in (False,True):
            ns=[list(range(h)) for _ in range(h+1)]+[list(range(h,h+3))]
            if sat:ns[h][-1]=h
            n,f=encoding(ns,h+3)
            out.append({"id":f"matching_{h}_{int(sat)}","family":"matching",
                        "n":n,"clauses":scramble(n,f,rng),"reference_sat":sat})
    for n in (12,14,16):
        count={False:0,True:0}
        for _ in range(1000):
            f=[]
            while len(f)<5*n:
                c=sorted(v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3))
                if c not in f:f.append(c)
            sat=exhaustive(n,f)
            if count[sat]==2:continue
            i=count[sat];count[sat]+=1
            out.append({"id":f"pure3_{n}_{int(sat)}_{i}","family":"pure3",
                        "n":n,"clauses":f,"reference_sat":sat})
            if min(count.values())==2:break
        else:raise ValueError("class quota unavailable")
    if digest(out)!=MANIFEST:raise ValueError("frozen manifest mismatch")
    return out


def self_test():
    import copy
    rng=random.Random(184121);counts=Counter()
    opts=[tuple(c) for k in (3,4) for c in combinations(range(4),k)]
    def oracle(ns):return any(len(set(a))==len(a) for a in product(*ns))
    for k in range(1,5):
        for ns in product(opts,repeat=k):
            n,f=encoding(ns,4);d="sat" if oracle(ns) else "unsat"
            if solve(n,f)["decision"]!=d or solve(n,scramble(n,f,rng))["decision"]!=d:
                raise ValueError("exhaustive mismatch")
            counts[d]+=1;counts["metamorphic"]+=1
    for _ in range(400):
        h=rng.randint(3,7);ns=[rng.sample(range(h),rng.randint(3,h)) for _ in range(rng.randint(1,8))]
        n,f=encoding(ns,h);d="sat" if oracle(ns) else "unsat"
        if solve(n,scramble(n,f,rng))["decision"]!=d:raise ValueError("random mismatch")
        counts[d]+=1
    for h in (3,5,8,16,32):
        n,f=encoding([list(range(h))]*(h+1),h)
        if solve(n,f)["decision"]!="unsat" or solve(n,f[1:])["decision"]!="sat":
            raise ValueError("scaling mismatch")
        counts["scaling_pairs"]+=1
    n,f=encoding([[0,1,2]]*4,3);r=solve(n,f)
    bad=copy.deepcopy(r);bad["buckets"][0].append(bad["buckets"][1][0])
    for g,c in ((f,bad),(f[:-1],r),(f,{"decision":"sat","model":[True]*n})):
        try:verify(n,g,c)
        except ValueError:counts["tamper_rejected"]+=1
        else:raise ValueError("forgery accepted")
    if solve(3,[[1,2,3],[1,2]])!={"decision":"unknown"}:raise ValueError("scope violation")
    return dict(counts)


def worker():
    resource.setrlimit(resource.RLIMIT_AS,(MEMORY,MEMORY))
    resource.setrlimit(resource.RLIMIT_CPU,(WALL,WALL))
    os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
    req=json.load(sys.stdin);c=req["case"];n,f=c["n"],c["clauses"]
    try:
        r=solve(n,f);verify(n,f,r)
        fallback=run_arm(req) if r["decision"]=="unknown" else None
        result={"decision":fallback["decision"] if fallback else r["decision"],
                "matching":r,"fallback":fallback}
    except (MemoryError, Exhausted):
        result={"decision":"unknown","resource_exhausted":True}
    print(json.dumps({"result":result}))


def experimental(req):
    start=time.monotonic()
    try:
        p=subprocess.run([sys.executable,__file__,"--worker"],input=json.dumps(req),
                         text=True,capture_output=True,timeout=WALL)
    except subprocess.TimeoutExpired:
        return {"result":{"decision":"unknown","timeout":True},"wall_seconds":time.monotonic()-start}
    if p.returncode in (-signal.SIGXCPU,-signal.SIGKILL):
        return {"result":{"decision":"unknown","process_resource_signal":p.returncode},
                "wall_seconds":time.monotonic()-start}
    if p.returncode:raise RuntimeError(p.stderr[-4000:])
    r=json.loads(p.stdout);r["wall_seconds"]=time.monotonic()-start
    return r


def replay_experimental(c,policy,plan,old,lib,r):
    if any(k in r for k in ("timeout","resource_exhausted","process_resource_signal")):
        if r["decision"]!="unknown" or len(r)!=2:raise ValueError("exhaustion record")
        return
    a,b=r["matching"],r["fallback"];verify(c["n"],c["clauses"],a)
    if a["decision"]=="unknown":
        if b is None:raise ValueError("missing fallback")
        replay_arm("v18",c,policy,plan,old,lib,b)
        d=b["decision"]
    else:
        if b is not None:raise ValueError("unexpected fallback")
        d=a["decision"]
    if r["decision"]!=d:raise ValueError("candidate verdict mismatch")


def summary(rows):
    out={}
    for family in ("all","matching","pure3"):
        rs=[r for r in rows if family=="all" or r["case"]["family"]==family]
        out[family]={}
        for arm in ("v18","matching-first"):
            xs=[r["arms"][arm] for r in rs]
            out[family][arm]={**{d:sum(x["result"]["decision"]==d for x in xs)
                                  for d in ("sat","unsat","unknown")},
                              "wall_seconds":sum(x["wall_seconds"] for x in xs)}
    return out


def main():
    if sys.argv[1:]==["--worker"]:worker();return
    if sys.argv[1:]==["--self-test"]:print(json.dumps(self_test(),sort_keys=True));return
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("benchmark","scheduler","failures","library"):
        p.add_argument("--"+k,type=Path,required=True)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--checkpoint",type=Path);mode.add_argument("--audit",type=Path)
    a=p.parse_args()
    paths=(a.benchmark,a.scheduler,a.failures,a.library)
    data=[json.loads(x.read_text()) for x in paths]
    source,scheduler,failures,lr=data
    audit_library(*data)
    policy,plan,old,lib=train(source),failures["selected_plan"],lr["v15_source_templates"],lr["library"]
    if (digest(policy),digest(old),digest(lib),plan)!=(POLICY,OLD,LIBRARY,["min_product",8]):
        raise ValueError("release policy mismatch")
    cases=manifest()
    known={case_key(x["case"]) for x in source["rows"]}
    for k in ("training","evaluation"):known.update(case_key(x["case"]) for x in failures[k])
    for k in ("training","discovery","heldout","retrospective"):known.update(case_key(x["case"]) for x in lr[k])
    known.update(case_key(c) for c in development_cases(source,lr))
    known.update(case_key(c) for c in previous_manifest())
    keys=[case_key(c) for c in cases]
    if len(set(keys))!=len(keys) or set(keys)&known:raise ValueError("input overlap")
    meta={"schema":"mathos-pnp-v18-matching-frontier/1","manifest_sha256":MANIFEST,
          "upstream":[digest(x) for x in data],"library_sha256":LIBRARY,
          "scope":"synthetic_development_matching_only_already_probed_not_blinded",
          "universal_obligation":"unresolved",
          "envelope":{"wall_seconds":WALL,"address_space_bytes":MEMORY,"cpu_cores":1,
                      "matching_work_not_in_legacy_step_counter":True}}
    def verdict(c,x):
        d=x["result"]["decision"]
        if d not in ("sat","unsat","unknown") or (d!="unknown" and (d=="sat")!=c["reference_sat"]):
            raise ValueError("false decision")
    if a.audit:
        r=json.loads(a.audit.read_text())
        if any(r[k]!=v for k,v in meta.items()) or r["completion"]!="completed" or [x["case"] for x in r["rows"]]!=cases:
            raise ValueError("manifest mismatch")
        for row in r["rows"]:
            c=row["case"];xs=row["arms"]
            if set(xs)!={"v18","matching-first"}:raise ValueError("missing arm")
            replay_arm("v18",c,policy,plan,old,lib,xs["v18"]["result"])
            replay_experimental(c,policy,plan,old,lib,xs["matching-first"]["result"])
            for x in xs.values():verdict(c,x)
        if summary(r["rows"])!=r["summary"]:raise ValueError("aggregate mismatch")
        print(json.dumps({"status":"positive_claims_replayed"}));return
    if a.checkpoint.resolve() in {x.resolve() for x in paths}:p.error("cannot overwrite upstream")
    a.checkpoint.parent.mkdir(parents=True,exist_ok=True)
    r={**meta,"completion":"running","rows":[]}
    def save():
        t=a.checkpoint.with_suffix(".tmp");t.write_text(json.dumps(r,sort_keys=True,indent=2));t.replace(a.checkpoint)
    save()
    for i,c in enumerate(cases):
        req={"arm":"v18","case":{"n":c["n"],"clauses":c["clauses"]},
             "policy":policy,"plan":plan,"old":old,"library":lib}
        row={"case":c,"arms":{}}
        for name,fn in ((("v18",isolated),("matching-first",experimental)) if i%2==0 else
                        (("matching-first",experimental),("v18",isolated))):
            x=fn(req);verdict(c,x);row["arms"][name]=x
        r["rows"].append(row);save()
    r["summary"]=summary(r["rows"]);r["completion"]="completed";save()
    print(json.dumps(r["summary"],sort_keys=True,indent=2))


if __name__=="__main__":main()
