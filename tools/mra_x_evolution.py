"""Phase IV: bounded policy evolution, held-out arbitration and research memory."""
import argparse
import hashlib
import json
import math
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
import mra_x_topology as ref
import mra_x_gap_agent as gap
import mra_x_upgrade as up
import mra_x_curriculum_agent as cur

WIDTHS=(1,2,4,8,16)


def beam(domains,factors,width):
    if type(width) is not int or width not in WIDTHS: raise ValueError('unregistered policy')
    if len(domains)>9 or any(d>3 for d in domains.values()): raise ValueError('outside experiment envelope')
    initial=tuple(sorted({tuple(sorted(s)) for s,_ in factors if s}))
    states=[(0,(),initial)]; expansions=0
    for _ in domains:
        children={}
        for cost,order,scopes in states:
            for v in sorted(set(domains)-set(order)):
                boundary=tuple(sorted(set().union(*(set(s) for s in scopes if v in s))-{v}))
                rest={s for s in scopes if v not in s}
                if boundary: rest.add(boundary)
                sig=tuple(sorted(rest)); path=order+(v,)
                value=cost+domains[v]*math.prod(domains[u] for u in boundary)
                key=(frozenset(path),sig); candidate=(value,path,sig)
                if key not in children or candidate<children[key]: children[key]=candidate
                expansions+=1
        states=sorted(children.values())[:width]
    cost,order,_=states[0]
    if up.predict(domains,factors,order)[0]!=cost: raise ValueError('scope model mismatch')
    return list(order),expansions


def evaluate(width,seed,split):
    if split not in ('train','holdout'): raise ValueError('invalid split')
    rows=[]; expansions=0
    for i,family in enumerate(gap.FAMILIES):
        for trial in range(4):
            d,variants=gap.build(family,seed*10000+(0 if split=='train' else 5000)+100*i+trial,trial)
            for edit,fs in variants:
                _,base=up.choose(d,fs); order,work=beam(d,fs,width); expansions+=work
                # Conservative envelope: retain baseline if the new order is not better.
                if up.predict(d,fs,base)<=up.predict(d,fs,order): order=base
                r=ref.solve(d,fs,order); b=ref.solve(d,fs,base); expected=gap.oracle(d,fs)
                ok=gap.check_result(d,fs,expected,r) and gap.check_result(d,fs,expected,b)
                ok=ok and r['assignments_evaluated']==up.predict(d,fs,order)[0]<=b['assignments_evaluated']
                row={'family':family,'trial':trial,'edit':edit,'instance_sha256':gap.digest(gap.instance_record(d,fs)), 'ok':ok,'candidate':r['assignments_evaluated'],'baseline':b['assignments_evaluated']}
                if not ok: row['counterexample']={'instance':gap.instance_record(d,fs),'expected':expected,'candidate':r,'baseline':b}
                rows.append(row)
    return {'width':width,'split':split,'rows':rows,'candidate':sum(r['candidate'] for r in rows),'baseline':sum(r['baseline'] for r in rows),'expansions':expansions,'failures':sum(not r['ok'] for r in rows)}


def worker(width,seed,split):
    # Trusted registered code only. Resource limits are not a security sandbox.
    import resource
    resource.setrlimit(resource.RLIMIT_CPU,(20,21))
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
    resource.setrlimit(resource.RLIMIT_FSIZE,(4*1024**2,4*1024**2))
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    return evaluate(width,seed,split)


def isolated(width,seed,split):
    if type(width) is not int or width not in WIDTHS: raise ValueError('invalid policy')
    try:
        p=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--worker',str(width),str(seed),split],capture_output=True,text=True,timeout=30,env={'PATH':os.defpath,'PYTHONHASHSEED':'0','PYTHONIOENCODING':'utf-8'})
        if p.returncode: return {'width':width,'split':split,'error':'worker_exit_'+str(p.returncode)}
        return json.loads(p.stdout)
    except (subprocess.TimeoutExpired,ValueError) as exc:
        return {'width':width,'split':split,'error':type(exc).__name__}


def arbitrate(result):
    if 'error' in result or result.get('failures',1): return 'REJECTED'
    if result.get('split')!='holdout' or len(result.get('rows',[]))!=52: return 'REJECTED'
    if not all(r['ok'] and 0<=r['candidate']<=r['baseline'] for r in result['rows']): return 'REJECTED'
    if any(result[k]!=sum(r[k] for r in result['rows']) for k in ('candidate','baseline')): return 'REJECTED'
    # Require positive enumeration savings; never infer runtime or authorize deployment.
    if result['candidate']>=result['baseline']: return 'NO_GAIN'
    return 'REVIEW_CANDIDATE'


def campaign(seed,history):
    prior=next((r['selected_width'] for r in reversed(history) if r['decision']=='REVIEW_CANDIDATE'),None)
    widths=list(WIDTHS) if prior is None else sorted({1,prior,min(16,prior*2),max(1,prior//2)})
    training=[isolated(w,seed,'train') for w in widths]
    good=[r for r in training if 'error' not in r and r['failures']==0]
    selected=min(good,key=lambda r:(r['candidate'],r['expansions'],r['width'])) if good else None
    held=isolated(selected['width'],seed,'holdout') if selected else {'error':'no_valid_training_candidate'}
    decision=arbitrate(held)
    # Propose a new knowledge node; verify dependencies, do not mutate trusted curriculum.
    proposal=('EVO-BEAM-'+str(seed),'Bounded policy search and held-out assessment',None,('OPT-702','VER-602'),'Independent review, runtime and memory profiling; no automatic promotion.')
    graph=up.schedule(list(cur.MODULES)+[proposal])
    result={'seed':seed,'prior_runs':len(history),'prior_policy':prior,'training':training,'selected_width':selected['width'] if selected else None,'heldout':held,'decision':decision,'curriculum_proposal':{'id':proposal[0],'dependencies':list(proposal[3]),'status':'PROPOSED','candidate_graph_nodes':len(graph)},'source_sha256':{Path(p).name:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in (__file__,ref.__file__,gap.__file__,up.__file__,cur.__file__)},'authorizes_merge':False,'scope':'registered bounded policies only; resource-limited worker, not untrusted-code sandbox; logical counts exclude search overhead; independent review required'}
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--seed',type=int,default=401); p.add_argument('--ledger',type=Path); p.add_argument('--output',type=Path); p.add_argument('--worker',nargs=3); a=p.parse_args()
    if a.worker:
        w,s,split=a.worker; print(json.dumps(worker(int(w),int(s),split))); return 0
    if not a.ledger or not a.output or not 1<=a.seed<=100000: p.error('ledger, output and bounded seed required')
    if a.output.exists(): p.error('fresh output required')
    with sqlite3.connect(a.ledger,timeout=60) as db:
        db.execute('CREATE TABLE IF NOT EXISTS evolution (seed INTEGER PRIMARY KEY, digest TEXT NOT NULL, report TEXT NOT NULL)')
        db.execute('BEGIN IMMEDIATE'); history=[]
        for seed,key,raw in db.execute('SELECT seed,digest,report FROM evolution ORDER BY rowid'):
            r=json.loads(raw)
            if gap.digest(r)!=key or r['seed']!=seed: raise ValueError('ledger mismatch')
            if seed>=a.seed: raise ValueError('seed must increase across campaigns')
            history.append(r)
        r=campaign(a.seed,history); key=gap.digest(r)
        with a.output.open('x') as f: json.dump({'evidence_sha256':key,'report':r},f,indent=2)
        db.execute('INSERT INTO evolution VALUES (?,?,?)',(a.seed,key,gap.canonical(r)))
    print(json.dumps({'decision':r['decision'],'prior_runs':r['prior_runs'],'selected_width':r['selected_width'],'holdout':{k:v for k,v in r['heldout'].items() if k!='rows'},'training_candidates':len(r['training'])},indent=2))
    return int(r['decision']=='REJECTED')


if __name__=='__main__': raise SystemExit(main())
