"""Phase XIX: bounded scenario planning with explicit simulation accounting."""
import argparse
import hashlib
import json
import math
import random
import statistics as st
import time
from pathlib import Path
import mra_x_temporal as t
import mra_x_world as w
import mra_x_separator as sep
import mra_x_gap_agent as gap

require=t.require
SCENARIOS=3
DEPTH=2


def corpus(split):
    start,sizes={'train':(19100,(8,12)), 'validation':(19500,(10,)), 'test':(19900,(16,24))}[split]
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in sizes:
            for mode in range(2):
                seed=start+i*100+n*2+mode; rng=random.Random(seed)
                d,f=sep.instance(seed,n,kind); vs=list(d)
                stream=[({str(j):x for j,x in enumerate(f)}, {})]
                for j in range(1):
                    v,u=rng.sample(vs,2); z=f'new{j}'; fid=f'edge{j}'; s,tab=f[rng.randrange(len(f)-1)]
                    stream.append(({fid:((v,z),{(0,0):0})},{z:2}))
                    if mode: stream.append(({f'bridge{j}':((u,z),{(0,0):1})},{}))
                    if rng.random()<.7: stream.extend([({}, {z:3}),({}, {z:2})])
                    if rng.random()<.6:
                        k=str(f.index((s,tab))); stream.extend([({k:(s,{})},{}),({k:(s,tab)}, {})])
                    stream.append(({fid:None,**({f'bridge{j}':None} if mode else {})},{z:None}))
                    stream.extend([({}, {u:d[u]+1}),({}, {u:d[u]})])
                stream.append(({},{})); yield f'{split}:{seed}:{kind}:{n}',d,stream


def train():
    model={'global':[0]*len(w.EVENTS),'transitions':{k:[0]*len(w.EVENTS) for k in w.EVENTS},'ids':[]}
    checks=0
    for name,d,stream in corpus('train'):
        model['ids'].append(name); e=t.initial(d); last=None
        for edit in stream:
            k=w.event(e,edit)
            if last is not None:
                model['global'][w.EVENTS.index(k)]+=1; model['transitions'][last][w.EVENTS.index(k)]+=1
            p=t.prepare(e,*edit); e,_=t.execute(e,edit[0],p,p[3],True); checks+=1; last=k
    return model,checks


def propose(e,kind,rng,original):
    # Concrete valid edit from the current simulated state, never a future test edit.
    d=e.d; fs=e.inputs; added=sorted(set(d)-original)
    if kind=='add' and d and len(d)<128 and len(fs)<1024:
        z='scenario'; j=0
        while z in d or z in fs: j+=1; z=f'scenario{j}'
        v=rng.choice(sorted(d)); return {z:((v,z),{(0,0):0})},{z:2}
    if kind=='remove' and added:
        v=rng.choice(added); return {k:None for k,(s,_) in fs.items() if v in s},{v:None}
    if kind=='resize' and d:
        v=rng.choice(added or sorted(d)); k=d[v]+1 if d[v]<4 else d[v]-1
        edits={fid:(s,{a:c for a,c in tab.items() if a[s.index(v)]<k}) for fid,(s,tab) in fs.items() if v in s and k<d[v]}
        return edits,{v:k}
    if kind=='factor' and fs:
        fid=rng.choice(sorted(fs)); s,tab=fs[fid]; tab=dict(tab)
        if tab:
            a=rng.choice(sorted(tab)); tab[a]+=rng.choice((-1,1))
        else: tab[tuple(0 for _ in s)]=0
        return {fid:(s,tab)},{}
    return {},{}


def plan(e,edit,p,model,k,original,seed,verify):
    base,alt=p[3:]; require(alt is not None)
    a,ar=t.execute(e,edit[0],p,base,verify); b,br=t.execute(e,edit[0],p,alt,verify)
    require(ar['result']['optimum']==br['result']['optimum']); costs=[]; sim=0; checks=2; events=[]
    for j in range(SCENARIOS):
        rng=random.Random(seed+j); left,right=a,b; last=k; ac=ar['actual']; bc=br['actual']; realized=[]
        for _ in range(DEPTH):
            label=rng.choices(w.EVENTS,weights=w.forecast(model,last))[0]; future=propose(left,label,rng,original); last=w.event(left,future); realized.append(last)
            left,x=t.step(left,future,[],[],verify); right,y=t.step(right,future,[],[],verify)
            require(x['optimum']==y['optimum']); ac+=x['actual']; bc+=y['actual']; sim+=x['actual']+y['actual']; checks+=2
        costs.append([ac,bc]); events.append(realized)
    gain=(sum(x for x,y in costs)-sum(y for x,y in costs))/max(1,sum(x for x,y in costs))
    return (a,ar),(b,br),dict(gain=gain,wins=sum(y<x for x,y in costs),costs=costs,events=events,checks=checks,simulation=sim)


def run(d,stream,model,threshold,seed,verify=False):
    e=t.initial(d); original=set(d); rows=[]
    for i,edit in enumerate(stream):
        k=w.event(e,edit); p=t.prepare(e,*edit); base,alt=p[3:]; action=base; diagnostic=None; overhead=0
        if threshold is not None and alt is not None:
            a,b,diagnostic=plan(e,edit,p,model,k,original,seed*100+i*SCENARIOS,verify)
            if diagnostic['gain']>=threshold and diagnostic['wins']>=2: action=alt
            e,r=b if action==alt else a
            overhead=diagnostic['simulation']+(a if action==alt else b)[1]['actual']
        else: e,r=t.execute(e,edit[0],p,base,verify)
        rows.append(dict(event=k,action=action,base=base,actual=r['actual'],overhead=overhead,optimum=r['result']['optimum'],diagnostic=diagnostic))
    return rows


def totals(batches):
    rows=[r for b in batches for r in b]; actual=sum(r['actual'] for r in rows); overhead=sum(r['overhead'] for r in rows)
    return dict(transactions=len(rows),actual=actual,simulation_overhead=overhead,total=actual+overhead,departures=sum(r['action']!=r['base'] for r in rows),plans=sum(r['diagnostic'] is not None for r in rows),checks=sum(r['diagnostic']['checks'] if r['diagnostic'] else 1 for r in rows))


def audit(modelpath):
    model,training_checks=train(); val=[]
    for threshold in (None,.10):
        batches=[run(d,s,model,threshold,i+100,True) for i,(_,d,s) in enumerate(corpus('validation'))]; val.append(dict(threshold=threshold,**totals(batches)))
    threshold=.10 if val[1]['total']<=.95*val[0]['total'] else None
    model['threshold']=threshold; digest=gap.digest(model)
    with modelpath.open('x') as f: json.dump({'model':model,'sha256':digest},f,indent=2)
    loaded=json.loads(modelpath.read_text()); require(gap.digest(loaded['model'])==loaded['sha256']==digest); model=loaded['model']; rows=[]; times=[]
    for i,(name,d,s) in enumerate(corpus('test')):
        require(name not in model['ids']); base=run(d,s,model,None,i+200,True); active=run(d,s,model,.10,i+200,True)
        require([r['optimum'] for r in base]==[r['optimum'] for r in active]); rows.append(dict(id=name,baseline=base,active=active))
        elapsed={k:[] for k in ('baseline','active')}
        for j in range(2):
            labels=list(elapsed); random.Random(i*11+j).shuffle(labels)
            for k in labels:
                start=time.perf_counter_ns(); run(d,s,model,.10 if k=='active' else None,i+200); elapsed[k].append(time.perf_counter_ns()-start)
        times.append(elapsed)
    require(gap.digest(model)==digest); b=totals([r['baseline'] for r in rows]); a=totals([r['active'] for r in rows]); ratios=[st.median(x['active'])/st.median(x['baseline']) for x in times]
    # Fallback is selected only on validation; active policy always tested as a diagnostic.
    geo=math.exp(st.mean(map(math.log,ratios))); worst=max(ratios)
    out=dict(training_checks=training_checks,validation=val,threshold=threshold,model_sha256=digest,baseline=b,active=a,rows=rows,times_ns=times,geomean_ratio=geo,worst_ratio=worst,decision='REVIEW_CANDIDATE' if threshold is not None and a['total']<=.9*b['total'] and geo<=.9 and worst<=1.2 else 'NO_PROMOTION',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='synthetic edit streams; three sampled two-edit continuations; counts include rejected initial candidate and simulated future kernel visits; in-memory timing excludes verification, training and persistence; no full world-model accuracy claim')
    out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); p.add_argument('--model',type=Path,required=True); a=p.parse_args(); r=audit(a.model)
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps({k:v for k,v in r.items() if k not in ('rows','times_ns')},indent=2))
