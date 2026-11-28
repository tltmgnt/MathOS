"""Evidence-guided scheduling of the existing certificate portfolio.

Training uses structured/development rows only; the frozen scheduler is
evaluated on holdout cases against a fixed-order, equal-quota baseline.
Both execute real plans with shared per-case work and time budgets.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import time

from .pnp_evidence_benchmark import audit as audit_benchmark, benchmark, canonical, digest, CONFIG
from .pnp_structural_kernel import Budget, Exhausted
from .pnp_unified_portfolio import DEFAULT_PLANS, Slice, run, verify_report
from .pnp_outcome_engine import checkpoint

VERSION = "mathos-pnp-evidence-scheduler/1"
MAX_TOTAL = 2_000_000
MIN_CAP = 32


def _limits(total, seconds):
    if type(total) is not int or not 1 <= total <= MAX_TOTAL:
        raise ValueError("total work must be in 1..2000000")
    if type(seconds) not in (int,float) or not 0 < seconds <= 60:
        raise ValueError("seconds must be in (0,60]")


def _fit(rows):
    """Greedy marginal coverage per observed attempted work on training.

    No reference answers, timings, holdout rows, or aggregate benchmark
    metrics enter the scoring function. Failed runs contribute work too.
    Once marginal coverage is exhausted, retain every remaining route
    as a fallback, sorted by observed work then original plan index.
    """
    training = [r for r in rows if r["case"]["group"] in ("structured","development")]
    if not training:
        raise ValueError("empty training set")
    records = [[p["report"]["entries"][0] for p in r["plans"]] for r in training]
    remaining = set(range(len(records)))
    available = set(range(len(DEFAULT_PLANS)))
    order = []
    while available:
        def stats(i):
            gain = sum(records[j][i]["decision"]!="unknown" for j in remaining)
            work = sum(max(1,records[j][i]["work_steps"]) for j in remaining)
            # If training is covered, order fallbacks on all training rows.
            if not remaining:
                work = sum(max(1,row[i]["work_steps"]) for row in records)
            return gain,work
        i = min(available,key=lambda i:(-Fraction(stats(i)[0],max(1,stats(i)[1])),
                                        -stats(i)[0],stats(i)[1],i))
        gain,work=stats(i)
        successful=[r[i]["work_steps"] for r in records if r[i]["decision"]!="unknown"]
        # Twice the largest successful training cost, with a floor.
        # If never successful, a fallback gets its equal-share allowance.
        cap=max(MIN_CAP,2*max(successful)) if successful else None
        order.append({"plan":list(DEFAULT_PLANS[i]),"marginal_training_decisions":gain,
                      "observed_attempt_work":work,"suggested_cap":cap})
        remaining={j for j in remaining if records[j][i]["decision"]=="unknown"}
        available.remove(i)
    # Bind only policy-relevant training observations (no holdout digest).
    observations=[{"id":r["case"]["id"],"entries":[
        {"plan":list(e["plan"]),"decision":e["decision"],"work_steps":e["work_steps"]}
        for e in row]} for r,row in zip(training,records)]
    return {"algorithm":"greedy-marginal-coverage-per-work/1","training_sha256":digest(observations),
            "training_ids":[r["case"]["id"] for r in training],
            "training_cases":len(training),"training_union_decided":len(training)-len(remaining),
            "order":order}


def train(source):
    if not audit_benchmark(source)["complete"]:
        raise ValueError("complete audited benchmark required")
    return _fit(source["rows"])


def _schedule(policy, arm, total):
    equal=max(1,total//len(DEFAULT_PLANS))
    if arm=="baseline":
        return [(list(p),equal) for p in DEFAULT_PLANS]
    if arm!="learned":
        raise ValueError("unknown scheduler arm")
    return [(p["plan"],min(total,p["suggested_cap"] if p["suggested_cap"] is not None else equal))
            for p in policy["order"]]


def execute(n, f, policy, arm, total, seconds):
    _limits(total,seconds)
    parent=Budget(seconds=seconds,max_steps=total,max_cells=200_000)
    attempts=[]
    decision="unknown"
    start=time.perf_counter_ns()
    for plan,cap in _schedule(policy,arm,total):
        quota=min(cap,total-parent.steps)
        if quota<=0:
            break
        # The inner single-plan quota is exactly this slice. Unused work
        # is retained globally, but no attempt may exceed its own cap.
        report=run(n,f,Slice(parent,quota),plans=(plan,),**CONFIG)
        attempts.append({"quota":quota,"report":report})
        if report["decision"]!="unknown":
            decision=report["decision"]
            break
        # A zero-work time exhaustion is not a reason to retry or guess.
        if time.monotonic()>=parent.deadline:
            break
    elapsed=time.perf_counter_ns()-start
    return {"arm":arm,"decision":decision,"attempts":attempts,
            "work_steps":parent.steps,"elapsed_ns":elapsed}


def replay(n,f,policy,total,record):
    schedule=_schedule(policy,record["arm"],total)
    attempts=record["attempts"]
    if not 1<=len(attempts)<=len(schedule):
        raise ValueError("invalid attempted schedule length")
    used=0
    known="unknown"
    for (plan,cap),attempt in zip(schedule,attempts):
        quota=min(cap,total-used)
        r=attempt["report"]
        if (known!="unknown" or quota<=0 or type(attempt["quota"]) is not int or
                attempt["quota"]!=quota or [list(p) for p in r["plans"]]!=[plan] or
                r["options"]!=CONFIG or r["per_plan_work_quota"]!=quota):
            raise ValueError("attempt schedule mismatch")
        steps=r["work_steps"]
        if (type(steps) is not int or not 0<=steps<=quota or
                steps!=r["entries"][0]["work_steps"]):
            raise ValueError("work accounting mismatch")
        verify_report(n,f,r,Budget(seconds=10,max_steps=4_000_000,max_cells=200_000))
        used+=steps
        known=r["decision"]
    # A prefix with unknown can be a deadline stop; its missing routes
    # cannot establish coverage failure, completeness, or a lower bound.
    if (record["decision"]!=known or record["work_steps"]!=used or
            type(record["elapsed_ns"]) is not int or record["elapsed_ns"]<0):
        raise ValueError("scheduler conclusion mismatch")
    return True


def _summary(rows):
    arms={a:{"decided":0,"sat":0,"unsat":0,"unknown":0,"work_steps":0,
             "attempts":0,"exhausted_attempts":0,"elapsed_ns":0} for a in ("baseline","learned")}
    paired={"both_decided":0,"learned_only":0,"baseline_only":0,"both_unknown":0}
    queue=[]
    for row in rows:
        decisions=[]
        for a,s in arms.items():
            r=row[a]
            d=r["decision"]
            decisions.append(d!="unknown")
            s[d]+=1
            s["decided"]+=d!="unknown"
            s["work_steps"]+=r["work_steps"]
            s["attempts"]+=len(r["attempts"])
            s["exhausted_attempts"]+=sum(p["report"]["entries"][0]["status"]=="resource_exhausted" for p in r["attempts"])
            s["elapsed_ns"]+=r["elapsed_ns"]
        b,l=decisions
        key="both_decided" if b and l else "baseline_only" if b else "learned_only" if l else "both_unknown"
        paired[key]+=1
        if not l:
            queue.append({"case_id":row["case"]["id"],
                          "priority":0 if not b else 1,
                          "reason":"both_schedules_unknown" if not b else "learned_schedule_missed_baseline_decision",
                          "reference_sat":row["reference"],
                          "scope":"observed under configured budgets, not a hardness result"})
    queue.sort(key=lambda q:(q["priority"],q["case_id"]))
    return {"holdout_cases":len(rows),"arms":arms,"paired":paired,"research_queue":queue}


def evaluate(source,*,total=100_000,seconds=5,checkpoint_path=None):
    _limits(total,seconds)
    policy=train(source)
    holdout=[r for r in source["rows"] if r["case"]["group"]=="holdout"]
    if not holdout:
        raise ValueError("holdout cases required")
    result={"schema":VERSION,"source_sha256":digest(source),"policy":policy,
            "total_steps_per_case":total,"seconds_per_case":seconds,"rows":[],
            "completion":"running","universal_obligation":"unresolved",
            "p_equals_np_established":False,"p_not_equals_np_established":False,
            "novel_theorem_verified":False}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,result)
    try:
        save()
        for j,row in enumerate(holdout):
            case,ref=row["case"],row["reference"]
            n,f=case["n"],case["clauses"]
            entry={"case":case,"reference":ref}
            # Alternate execution order to reduce systematic warmup bias.
            for arm in (("baseline","learned") if j%2==0 else ("learned","baseline")):
                a=execute(n,f,policy,arm,total,seconds)
                replay(n,f,policy,total,a)
                if a["decision"]!="unknown" and (a["decision"]=="sat")!=ref:
                    raise AssertionError("scheduled decision disagrees with reference")
                entry[arm]=a
            result["rows"].append(entry)
            save()
        result["completion"]="completed"
    except Exhausted as exc:
        result["completion"],result["reason"]="resource_exhausted",str(exc)
    except (AssertionError,ValueError) as exc:
        result["completion"],result["reason"]="diagnostic_required",str(exc)
    result["summary"]=_summary(result["rows"])
    save()
    return result


def audit(source,result):
    policy=train(source)
    total,seconds=result["total_steps_per_case"],result["seconds_per_case"]
    _limits(total,seconds)
    expected=[r for r in source["rows"] if r["case"]["group"]=="holdout"]
    rows=result["rows"]
    if (result["schema"]!=VERSION or result["source_sha256"]!=digest(source) or
            result["policy"]!=policy or result["universal_obligation"]!="unresolved" or
            any(result[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified")) or
            not expected or len(rows)>len(expected) or
            result["completion"] not in ("completed","resource_exhausted","diagnostic_required") or
            (result["completion"]=="completed" and len(rows)!=len(expected))):
        raise ValueError("source, policy, governance or completion mismatch")
    for row,ref in zip(rows,expected):
        if row["case"]!=ref["case"] or row["reference"] is not ref["reference"]:
            raise ValueError("holdout case mismatch")
        n,f=row["case"]["n"],row["case"]["clauses"]
        for arm in ("baseline","learned"):
            a=row[arm]
            if a["arm"]!=arm:
                raise ValueError("arm mismatch")
            replay(n,f,policy,total,a)
            if a["decision"]!="unknown" and (a["decision"]=="sat")!=row["reference"]:
                raise ValueError("reference decision mismatch")
    if result["summary"]!=_summary(rows):
        raise ValueError("aggregate mismatch")
    return {"status":"replayed","complete":result["completion"]=="completed",
            "holdout_cases":len(rows),"timings_and_search_work_certified":False,
            "universal_obligation":"unresolved"}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--benchmark",type=Path,required=True)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--audit",type=Path)
    p.add_argument("--total-steps",type=int,default=100_000)
    p.add_argument("--seconds",type=float,default=5)
    a=p.parse_args(argv)
    def read(path):
        if path.stat().st_size>32_000_000:
            raise ValueError("JSON exceeds 32 MB")
        return json.loads(path.read_text(encoding="utf-8"))
    try:
        source=read(a.benchmark)
        if a.audit:
            result=audit(source,read(a.audit))
            print(json.dumps(result,indent=2,sort_keys=True))
            return int(not result["complete"])
        if a.checkpoint and a.checkpoint.resolve()==a.benchmark.resolve():
            raise ValueError("cannot overwrite benchmark")
        result=evaluate(source,total=a.total_steps,seconds=a.seconds,checkpoint_path=a.checkpoint)
        print(json.dumps(result,indent=2,sort_keys=True))
        return int(result["completion"]!="completed")
    except (OSError,ValueError,KeyError,TypeError,Exhausted) as exc:
        p.error(str(exc))


if __name__=="__main__":
    raise SystemExit(main())
