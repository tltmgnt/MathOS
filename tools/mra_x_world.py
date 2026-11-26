"""Phase XVIII: edit-event forecasting and action-conditioned counterfactual learning."""
import argparse
import hashlib
import json
import math
import random
import statistics as st
import time
from pathlib import Path
import mra_x_temporal as temporal
import mra_x_gap_agent as gap
import mra_x_separator as sep
import mra_x_topology as ref

EVENTS=('add','remove','resize','factor','idle')
require=temporal.require


def event(e,edit):
    es,ds=edit
    if any(v not in e.d and k is not None for v,k in ds.items()): return 'add'
    if any(k is None for k in ds.values()): return 'remove'
    if any(e.d.get(v)!=k for v,k in ds.items()): return 'resize'
    return 'factor' if es else 'idle'


def corpus(split):
    start,sizes={'train':(18100,(8,16,24)), 'validation':(18500,(12,20)), 'holdout':(18900,(16,32,48))}[split]
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in sizes:
            for mode in range(2):
                seed=start+i*100+n*2+mode; rng=random.Random(seed)
                d,f=sep.instance(seed,n,kind); vs=list(d); v=rng.choice(vs); u=rng.choice([x for x in vs if x!=v]); s,t=f[0]
                stream=[({str(j):x for j,x in enumerate(f)}, {})]
                # Randomize the positions and locations of valid edit motifs.
                for j in range(3):
                    v=rng.choice(vs); u=rng.choice([x for x in vs if x!=v])
                    add=({'extra':((v,'extra'),{(0,0):0})},{'extra':2})
                    drop=({'extra':None},{'extra':None})
                    resize=({}, {'extra':3})
                    modify=({'bridge':((u,'extra'),{(0,0):1})},{})
                    if mode==0:
                        motif=[add,resize,({},{}),drop]
                    else:
                        motif=[add,modify,({}, {'extra':3}),({'bridge':None,'extra':None},{'extra':None})]
                    if rng.random()<.5: motif[1:1]=[({'0':(s,{})},{}),({'0':(s,t)}, {})]
                    stream.extend(motif)
                    if rng.random()<.5: stream.extend([({}, {v:d[v]+1}),({}, {v:d[v]})])
                stream.append(({},{}))
                yield f'{split}:{seed}:{kind}:{n}',d,stream


def forecast(model,last=None):
    counts=model['transitions'].get(last,model['global']) if last is not None else model['global']
    total=sum(counts)+len(EVENTS)
    return [(x+1)/total for x in counts]


def features(e,p,past):
    d,inputs,options,base,alt=p
    x=temporal.context(e,d,inputs,options,base,alt,[int(k in EVENTS[:3]) for k in past])
    changed=[v for v in e.d if e.d[v]!=d.get(v)]
    x.append(sum(e.rank[v]/max(1,len(e.d)-1) for v in changed)/max(1,len(changed)))
    return x


def train():
    model=dict(schema=1,events=list(EVENTS),global_counts=[0]*len(EVENTS),transitions={k:[0]*len(EVENTS) for k in EVENTS},samples=[],ids=[])
    model['global']=model.pop('global_counts'); checks=0
    for name,d,stream in corpus('train'):
        model['ids'].append(name); e=temporal.initial(d); past=[]
        for i,edit in enumerate(stream):
            k=event(e,edit)
            if past: model['transitions'][past[-1]][EVENTS.index(k)]+=1; model['global'][EVENTS.index(k)]+=1
            p=temporal.prepare(e,*edit); _,_,_,base,alt=p
            if alt and i+3<=len(stream):
                b,bo=temporal.rollout(e,stream[i:i+3],p,base); a,ao=temporal.rollout(e,stream[i:i+3],p,alt); require(bo==ao); checks+=6
                # Determine the next external edit class from a real intermediate state.
                intermediate,_=temporal.execute(e,edit[0],p,base)
                model['samples'].append(dict(x=features(e,p,past),event=k,next=event(intermediate,stream[i+1]),base=base,alt=alt,gain=(sum(b)-sum(a))/max(1,sum(b)),base_costs=b,alt_costs=a))
            e,_=temporal.execute(e,edit[0],p,base,True); checks+=1; past.append(k)
    return model,checks


def estimate(model,e,p,past,k):
    _,_,_,base,alt=p
    if not alt: return None
    x=features(e,p,past); probabilities=forecast(model,k)
    near=sorted((s for s in model['samples'] if s['base']==base and s['alt']==alt and s['event']==k),key=lambda s:sum((a-b)**2 for a,b in zip(x,s['x'])))[:12]
    if len(near)<5: return None
    # Forecast-conditioned mixture. Unobserved event mass is assigned zero gain,
    # and counted as unsupported rather than silently renormalized away.
    gain=positive=support=0.
    for j,next_event in enumerate(EVENTS):
        group=[s['gain'] for s in near if s['next']==next_event]
        if group:
            w=probabilities[j]; support+=w; gain+=w*st.mean(group); positive+=w*sum(g>0 for g in group)/len(group)
    return dict(gain=gain,positive=positive,support=support,neighbors=len(near))


def run(d,stream,model,threshold,verify=False):
    e=temporal.initial(d); past=[]; rows=[]
    for edit in stream:
        k=event(e,edit); p=temporal.prepare(e,*edit); _,_,_,base,alt=p
        pred=estimate(model,e,p,past,k) if threshold is not None else None
        action=alt if pred and pred['gain']>=threshold and pred['positive']>=.7 and pred['support']>=.75 else base
        e,r=temporal.execute(e,edit[0],p,action,verify)
        if verify and len(e.d)<=9: require(r['result']['optimum']==ref.brute(e.d,list(e.inputs.values())))
        rows.append(dict(event=k,action=action,base=base,actual=r['actual'],optimum=r['result']['optimum'],prediction=pred)); past.append(k)
    return rows


def audit(modelpath):
    model,checks=train(); train_hash=gap.digest(model); val=[]
    for threshold in (None,.05,.15,.3):
        work=changes=0
        for name,d,stream in corpus('validation'):
            require(name not in model['ids']); a=run(d,stream,model,threshold,True); checks+=len(a)
            work+=sum(r['actual'] for r in a); changes+=sum(r['action']!=r['base'] for r in a)
        val.append(dict(threshold=threshold,work=work,changes=changes))
    # Select only if validation enumeration improves by >=5%; fallback on ties.
    best=min(val,key=lambda r:r['work']); threshold=best['threshold'] if best['work']<=.95*val[0]['work'] else None
    require(gap.digest(model)==train_hash); model['threshold']=threshold; frozen=gap.digest(model)
    with modelpath.open('x') as f: json.dump(dict(model=model,sha256=frozen),f,indent=2)
    loaded=json.loads(modelpath.read_text()); require(gap.digest(loaded['model'])==loaded['sha256']==frozen); model=loaded['model']
    rows=[]; brier=unconditional=0.; forecasts=correct=0; effects=[]; times=[]
    for i,(name,d,stream) in enumerate(corpus('holdout')):
        a=run(d,stream,model,threshold,True); b=run(d,stream,model,None,True); checks+=len(a)+len(b)
        require([r['optimum'] for r in a]==[r['optimum'] for r in b])
        for left,right in zip(b,b[1:]):
            p=forecast(model,left['event']); q=forecast(model); target=EVENTS.index(right['event']); forecasts+=1
            correct+=max(range(len(EVENTS)),key=lambda j:p[j])==target
            brier+=sum((v-int(j==target))**2 for j,v in enumerate(p)); unconditional+=sum((v-int(j==target))**2 for j,v in enumerate(q))
        # Post-hoc diagnostic interventions on the baseline trajectory only.
        e=temporal.initial(d); past=[]
        for j,edit in enumerate(stream):
            p=temporal.prepare(e,*edit); _,_,_,base,alt=p; k=event(e,edit)
            if alt and j+3<=len(stream):
                bc,bo=temporal.rollout(e,stream[j:j+3],p,base); ac,ao=temporal.rollout(e,stream[j:j+3],p,alt); require(bo==ao); checks+=6
                effects.append(dict(id=name,step=j,estimate=estimate(model,e,p,past,k),gain=(sum(bc)-sum(ac))/max(1,sum(bc)),base_costs=bc,alt_costs=ac))
            e,_=temporal.execute(e,edit[0],p,base); past.append(k)
        elapsed={'learned':[],'baseline':[]}
        for repeat in range(3):
            rotation=list(elapsed); random.Random(i*13+repeat).shuffle(rotation)
            for label in rotation:
                start=time.perf_counter_ns(); run(d,stream,model,threshold if label=='learned' else None); elapsed[label].append(time.perf_counter_ns()-start)
        times.append(dict(id=name,ns=elapsed)); rows.append(dict(id=name,learned=a,baseline=b))
    require(gap.digest(model)==frozen); controls=2
    require(abs(sum(forecast(model,'add'))-1)<1e-12); controls+=1
    empty=dict(model,samples=[]); e=temporal.initial({'a':2,'b':2}); p=temporal.prepare(e,{},{}); require(estimate(empty,e,p,[],'idle') is None); controls+=1
    totals={k:sum(r['actual'] for batch in rows for r in batch[k]) for k in ('learned','baseline')}
    ratios=[st.median(t['ns']['learned'])/st.median(t['ns']['baseline']) for t in times]; geo=math.exp(st.mean(map(math.log,ratios))); worst=max(ratios)
    out=dict(checks=checks,controls=controls,model_sha256=frozen,training_samples=len(model['samples']),validation=val,threshold=threshold,forecast_count=forecasts,forecast_correct=correct,brier=brier/forecasts,unconditional_brier=unconditional/forecasts,effects=effects,rows=rows,totals=totals,times=times,geomean_ratio=geo,worst_ratio=worst,decision='REVIEW_CANDIDATE' if threshold is not None and totals['learned']<=.9*totals['baseline'] and geo<=.9 and worst<=1.2 else 'NO_PROMOTION',source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('mra_x_*.py'))},scope='synthetic edit motifs; first-order categorical forecast; paired intervention effects under fixed continuation; heuristic confidence not statistical interval; in-memory timings exclude training, verification and persistence; no deployment')
    out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); p.add_argument('--model',type=Path,required=True); a=p.parse_args(); r=audit(a.model)
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps({k:r[k] for k in ('checks','controls','training_samples','validation','threshold','forecast_count','forecast_correct','brier','unconditional_brier','totals','geomean_ratio','worst_ratio','decision')},indent=2))
