"""Audit proof compression and signed-template reuse on known and fresh inputs."""
import argparse
import json
from pathlib import Path

from .pnp_evidence_benchmark import digest,canonical
from .pnp_failure_synthesis import audit as audit_v13,fresh_cases
from .pnp_structural_kernel import Budget,Exhausted,normalize,brute
from .pnp_resolution_refutation import propose
from .pnp_proof_abstraction import compress,verify_embedding,find_embedding
from .pnp_outcome_engine import checkpoint

SEED=15015


def budget():
    return Budget(seconds=15,max_steps=4_000_000,max_cells=100_000)


def bytesize(o):
    return len(canonical(o).encode("ascii"))


def targets(source,scheduler,failures):
    audit_v13(source,scheduler,failures)
    j=[tuple(x["plan"]) for x in failures["training"][0]["attempts"]].index(tuple(failures["selected_plan"])) if failures["training"] else None
    return [(r["case"],r["attempts"][j]["proof"]) for r in failures["training"]
            if r["attempts"][j]["status"]=="refuted"]


def variants(t):
    n=t["n"]
    # Signed and shifted injection; append unrelated clauses to the target.
    embedding=tuple((-1 if i%2 else 1)*(n+2-i) for i in range(n))
    f=[tuple(sorted(embedding[x-1] if x>0 else -embedding[-x-1] for x in c)) for c in t["axioms"]]
    return n+4,f+[(n+3,n+4)],embedding


def reference(n,f):
    nn,nf,_=normalize(n,f)
    if nn>14:
        raise ValueError("reference input too large")
    return brute(nn,nf,budget())


def summary(r):
    records=r["records"]
    return {"source_proofs":len(records),"original_bytes":sum(x["original_bytes"] for x in records),
            "compact_bytes":sum(x["compact_bytes"] for x in records),
            "source_axioms":sum(x["source_axioms"] for x in records),
            "compact_axioms":sum(len(x["compact"]["template"]["axioms"]) for x in records),
            "original_steps":sum(len(x["proof"]["steps"]) for x in records),
            "compact_steps":sum(len(x["compact"]["template"]["steps"]) for x in records),
            "supplied_embedding_verified":len(records),
            "automatic_matches":sum(x["variant"]["match"]["status"]=="matched" for x in records),
            "fresh_cases":len(r["fresh"]),
            "fresh_matches":sum(x["match"] is not None for x in r["fresh"]),
            "fresh_reference_unsat":sum(not x["reference"] for x in r["fresh"])}


def run(source,scheduler,failures,*,count=16,checkpoint_path=None):
    if failures["seed"]==SEED:
        raise ValueError("fresh seed overlaps v13")
    work=targets(source,scheduler,failures)
    r={"schema":"mathos-pnp-proof-abstraction/1","upstream":[digest(x) for x in (source,scheduler,failures)],
       "count":count,"records":[],"fresh":[],"completion":"running",
       "universal_obligation":"unresolved","p_equals_np_established":False,
       "p_not_equals_np_established":False,"novel_theorem_verified":False}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        for case,p in work:
            n,f=case["n"],case["clauses"]
            compact=compress(n,f,p,budget())
            t=compact["template"]
            m,g,emb=variants(t)
            verify_embedding(m,g,t,emb,budget())
            match=find_embedding(m,g,t,budget())
            if reference(m,g):
                raise AssertionError("embedded contradiction reference mismatch")
            r["records"].append({"case":case,"proof":p,"compact":compact,
                "original_bytes":bytesize(p),"compact_bytes":bytesize(compact),
                "source_axioms":len(normalize(n,f)[1]),
                "variant":{"n":m,"clauses":g,"embedding":emb,"match":match}})
            save()
        for case in fresh_cases(SEED,count):
            n,f=case["n"],case["clauses"]
            ref=reference(n,f)
            match=None
            for i,x in enumerate(r["records"]):
                a=find_embedding(n,f,x["compact"]["template"],budget())
                if a["status"]=="matched":
                    match={"record":i,"embedding":a["embedding"]}
                    break
            if ref and match is not None:
                raise AssertionError("false contradiction match")
            r["fresh"].append({"case":case,"reference":ref,"match":match})
            save()
        r["completion"]="completed"
    except Exhausted as exc:
        r["completion"],r["reason"]="resource_exhausted",str(exc)
    except (ValueError,AssertionError) as exc:
        r["completion"],r["reason"]="diagnostic_required",str(exc)
    r["summary"]=summary(r)
    save()
    return r


def audit(source,scheduler,failures,r):
    work=targets(source,scheduler,failures)
    if (r["schema"]!="mathos-pnp-proof-abstraction/1" or r["upstream"]!=[digest(x) for x in (source,scheduler,failures)]
            or r["completion"]!="completed" or failures["seed"]==SEED or r["universal_obligation"]!="unresolved"
            or any(r[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))
            or len(work)!=len(r["records"])):
        raise ValueError("invalid proof abstraction report")
    for (case,p),row in zip(work,r["records"]):
        n,f=case["n"],case["clauses"]
        c=row["compact"]
        if (row["case"]!=case or digest(row["proof"])!=digest(p)
                or digest(c)!=digest(compress(n,f,p,budget()))
                or row["original_bytes"]!=bytesize(p) or row["compact_bytes"]!=bytesize(c)
                or row["source_axioms"]!=len(normalize(n,f)[1])):
            raise ValueError("compression evidence mismatch")
        t=c["template"]
        verify_embedding(n,f,t,c["source_embedding"],budget())
        m,g,emb=variants(t)
        a=row["variant"]
        if a["n"]!=m or digest(a["clauses"])!=digest(g) or tuple(a["embedding"])!=emb:
            raise ValueError("variant mismatch")
        verify_embedding(m,g,t,emb,budget())
        if digest(a["match"])!=digest(find_embedding(m,g,t,budget())) or reference(m,g):
            raise ValueError("variant replay mismatch")
    cases=fresh_cases(SEED,r["count"])
    if len(cases)!=len(r["fresh"]):
        raise ValueError("incomplete fresh evaluation")
    for case,row in zip(cases,r["fresh"]):
        n,f=case["n"],case["clauses"]
        if case!=row["case"] or row["reference"] is not reference(n,f):
            raise ValueError("fresh reference mismatch")
        expected=None
        for i,x in enumerate(r["records"]):
            t=x["compact"]["template"]
            a=find_embedding(n,f,t,budget())
            if a["status"]=="matched":
                expected={"record":i,"embedding":a["embedding"]}
                verify_embedding(n,f,t,a["embedding"],budget())
                break
        if digest(expected)!=digest(row["match"]) or (row["reference"] and expected is not None):
            raise ValueError("fresh match mismatch")
    if r["summary"]!=summary(r):
        raise ValueError("summary mismatch")
    return True


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("benchmark","scheduler","failures"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--audit",type=Path)
    p.add_argument("--count",type=int,default=16)
    a=p.parse_args(argv)
    def read(path):
        if path.stat().st_size>32_000_000:
            raise ValueError("JSON exceeds 32 MB")
        return json.loads(path.read_text(encoding="utf-8"))
    try:
        inputs=(read(a.benchmark),read(a.scheduler),read(a.failures))
        if a.audit:
            audit(*inputs,read(a.audit))
            print(json.dumps({"status":"replayed","universal_obligation":"unresolved"}))
            return 0
        if a.checkpoint and a.checkpoint.resolve() in {p.resolve() for p in (a.benchmark,a.scheduler,a.failures)}:
            raise ValueError("cannot overwrite upstream evidence")
        r=run(*inputs,count=a.count,checkpoint_path=a.checkpoint)
        print(json.dumps(r,indent=2,sort_keys=True))
        return int(r["completion"]!="completed")
    except (OSError,ValueError,KeyError,TypeError,Exhausted) as exc:
        p.error(str(exc))


if __name__=="__main__":
    raise SystemExit(main())
