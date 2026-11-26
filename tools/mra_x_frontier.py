"""Integrated curriculum and matched SciPy/HiGHS baseline; no proof promotion."""
import argparse
import hashlib
import json
import math
import sqlite3
import time
from pathlib import Path
import mra_x_topology as ref
import mra_x_gap_agent as gap
import mra_x_curriculum_agent as cur
import mra_x_upgrade as up


def highs(domains, factors):
    """One-hot variable and allowed-tuple MILP; validate returned witness exactly."""
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import coo_matrix
    ref.validate(domains, factors)
    if any(not t for _, t in factors):
        return None, None, 'empty_factor'
    cost=[]; xs={}; ts=[]; rows=[]
    def col(c=0):
        cost.append(c); return len(cost)-1
    for v,d in domains.items():
        xs[v]=[col() for _ in range(d)]
        rows.append(([(j,1) for j in xs[v]],1))
    for scope, table in factors:
        ids=[(a,col(c)) for a,c in table.items()]; ts.append(ids)
        rows.append(([(j,1) for _,j in ids],1))
        for i,v in enumerate(scope):
            for x,j in enumerate(xs[v]):
                rows.append(([(k,1) for a,k in ids if a[i]==x]+[(j,-1)],0))
    if not cost: return 0,{},'empty_problem'
    rr=[]; cc=[]; vv=[]; rhs=[]
    for i,(entries,b) in enumerate(rows):
        rhs.append(b)
        for j,w in entries: rr.append(i); cc.append(j); vv.append(w)
    matrix=coo_matrix((vv,(rr,cc)),shape=(len(rows),len(cost))).tocsc()
    r=milp(np.array(cost,dtype=float),integrality=np.ones(len(cost)),bounds=Bounds(0,1),
           constraints=LinearConstraint(matrix,rhs,rhs),options={'time_limit':10.,'mip_rel_gap':0.})
    if r.status==2: return None,None,'solver_infeasible'
    if r.status!=0 or r.x is None: raise RuntimeError('HiGHS status '+str(r.status))
    if max(abs(r.x-np.rint(r.x)))>1e-6: raise ValueError('nonintegral solver result')
    w={v:max(range(len(ids)),key=lambda x:r.x[ids[x]]) for v,ids in xs.items()}
    value=ref.score(factors,w)
    if value is None or abs(value-r.fun)>1e-6: raise ValueError('invalid solver witness')
    return value,w,'solver_optimal'


def campaign(seed, trials, priority):
    # Integrate scheduler and predicted orders in the executable curriculum path.
    records={}; cache={}
    for code,topic,lab,deps,obligation in up.schedule(list(reversed(cur.MODULES))):
        blocked=[d for d in deps if records[d]['status']!='LAB_PASS']
        status='OPEN_RESEARCH' if obligation else 'BLOCKED' if blocked else 'LAB_PASS'
        evidence={}; error=None
        if status=='LAB_PASS':
            try:
                if lab=='heldout':
                    chosen=base=0
                    for i,f in enumerate(gap.FAMILIES):
                        d,fs=cur.sample(f,seed+100000+i); expected=gap.oracle(d,fs)
                        _,order=up.choose(d,fs); r=ref.solve(d,fs,order); b=ref.solve(d,fs)
                        cur.require(gap.check_result(d,fs,expected,r) and gap.check_result(d,fs,expected,b))
                        cur.require(up.predict(d,fs,order)[0]==r['assignments_evaluated']<=b['assignments_evaluated'])
                        chosen+=r['assignments_evaluated']; base+=b['assignments_evaluated']
                    evidence={'selected_visits':chosen,'baseline_visits':base,'checks':22,'policy':'structural prediction'}
                else: evidence=cur.run_lab(lab,seed,cache,None)
            except Exception as exc: status='LAB_FAIL'; error=type(exc).__name__
        records[code]={'status':status,'blocked_by':blocked,'evidence':evidence,'error':error,'obligation':obligation}
    # Predefined corpus; priority changes order only, not membership.
    import scipy
    cases=[]; failures=[]
    # Warm up dependency import (not included in per-instance elapsed time).
    highs({'warm':1},[])
    for family in priority:
        i=list(gap.FAMILIES).index(family)
        for t in range(trials):
            case_seed=seed+200000+i*100+t
            d,variants=gap.build(family,case_seed,t)
            for edit,fs in variants:
                expected=gap.oracle(d,fs); entry={'family':family,'seed':case_seed,'edit':edit,'expected':expected,'instance_sha256':gap.digest(gap.instance_record(d,fs))}
                try:
                    start=time.perf_counter_ns(); _,o=up.choose(d,fs); r=ref.solve(d,fs,o); entry['mathos_ns']=time.perf_counter_ns()-start
                    start=time.perf_counter_ns(); val,w,kind=highs(d,fs); entry['highs_ns']=time.perf_counter_ns()-start
                    entry.update(mathos=r['optimum'],highs=val,highs_status=kind,visits=r['assignments_evaluated'])
                    entry['ok']=gap.check_result(d,fs,expected,r) and val==expected and (w is None if expected is None else set(w)==set(d) and ref.score(fs,w)==expected)
                except Exception as exc: entry.update(ok=False,error=type(exc).__name__+': '+str(exc))
                if not entry['ok']: failures.append({**entry,'instance':gap.instance_record(d,fs)})
                cases.append(entry)
    # Incremental repair integrated into a bounded factor edit lab; original gate remains open.
    edits=visits=full=reused=0
    for i,f in enumerate(gap.FAMILIES):
        d,fs=cur.sample(f,seed+300000+i); o=ref.min_fill(d,fs); engine=up.Incremental(d,o)
        engine.solve(fs); v=list(d)[-1]; add=((v,),{(x,):x for x in range(d[v])})
        for changed in (fs+[add],fs,fs[1:],fs,fs):
            r=engine.solve(changed); b=ref.solve(d,changed,o)
            cur.require(gap.check_result(d,changed,gap.oracle(d,changed),r))
            cur.require((r['optimum'],r['witness'],r['trace'])==(b['optimum'],b['witness'],b['trace']))
            edits+=1; visits+=r['assignments_evaluated']; full+=b['assignments_evaluated']; reused+=r['reused_buckets']
    records['OPT-703']['evidence']={'bounded_updates':edits,'visits':visits,'full_visits':full,'reused_buckets':reused,'formal_proof':False}
    records['RES-802']['evidence']={'baseline':'SciPy/HiGHS MILP','cases':len(cases),'mismatches':len(failures),'requested_other_solvers':'not run'}
    summary={s:sum(r['status']==s for r in records.values()) for s in ('LAB_PASS','LAB_FAIL','OPEN_RESEARCH','BLOCKED')}
    return {'seed':seed,'trials':trials,'priority':priority,'summary':summary,'modules':records,'cases':cases,'failures':failures,'scipy_version':scipy.__version__, 'source_sha256':{Path(p).name:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in (__file__,ref.__file__,gap.__file__,cur.__file__,up.__file__)},'scope':'small synthetic integer-cost instances; timings include encoding/planning, exclude oracle and imports; no native peak-memory measurements, independent replication, physical machine or mechanized proof'}


def load_priority(db):
    db.execute('CREATE TABLE IF NOT EXISTS frontier (id TEXT PRIMARY KEY, report TEXT NOT NULL)')
    totals={f:[0,0,0] for f in gap.FAMILIES}; count=0
    for key,raw in db.execute('SELECT id,report FROM frontier'):
        r=json.loads(raw)
        if gap.digest(r)!=key: raise ValueError('ledger digest mismatch')
        count+=1
        for c in r['cases']:
            a=totals[c['family']]; a[0]+=not c['ok']; a[1]+=c.get('visits',0); a[2]+=1
    return sorted(totals,key=lambda f:(-totals[f][0],-totals[f][1]/max(1,totals[f][2]),f)),count


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--seed',type=int,default=48000); p.add_argument('--trials',type=int,default=4); p.add_argument('--ledger',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    if not 1<=a.trials<=8: p.error('trials must be 1..8')
    with sqlite3.connect(a.ledger) as db:
        priority,count=load_priority(db); r=campaign(a.seed,a.trials,priority); r['prior_runs_read']=count; key=gap.digest(r)
        with a.output.open('x') as f: json.dump({'evidence_sha256':key,'report':r},f,indent=2)
        db.execute('INSERT OR IGNORE INTO frontier VALUES (?,?)',(key,gap.canonical(r)))
    print(json.dumps({'summary':r['summary'],'cases':len(r['cases']),'failures':len(r['failures']),'incremental':r['modules']['OPT-703']['evidence'],'predictive':r['modules']['OPT-702']['evidence'],'prior_runs_read':count,'priority':priority},indent=2))
    return int(bool(r['failures'] or r['summary']['LAB_FAIL'] or r['summary']['BLOCKED']))

if __name__=='__main__': raise SystemExit(main())
