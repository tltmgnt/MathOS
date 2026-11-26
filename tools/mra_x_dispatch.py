"""Phase XI: offline runtime learning and frozen batch-level dispatch."""
import argparse
import hashlib
import json
import math
import random
import statistics as st
import time
from pathlib import Path
import mra_x_topology as ref
import mra_x_gap_agent as gap
import mra_x_meta as meta
import mra_x_adaptive as ad
import mra_x_certify as cert

ENGINES=('fixed_min_fill','fixed_hierarchy','fresh_min_fill','meta','adaptive')


def require(ok):
    if not ok: raise ValueError('dispatch audit failed')


def features(d,seq):
    if not seq or len(seq)>32 or not 1<=len(d)<=64: raise ValueError('batch envelope')
    n=len(d); scopes=[tuple(sorted(s for s,_ in f)) for f in seq]
    g=cert.graph(d,seq[0]); edges=sum(map(len,g.values()))/2
    return [math.log2(n)/6,edges/max(1,n*3),max((len(s) for s,_ in seq[0]),default=0)/4,
            sum(d.values())/(4*n),len(seq)/32,len(set(scopes))/len(seq),
            sum(a!=b for a,b in zip(scopes,scopes[1:]))/max(1,len(seq)-1)]


def fit(rows):
    require(bool(rows) and all(r['split']=='train' for r in rows))
    samples=[]
    for r in rows:
        median={k:st.median(r['times_ns'][k]) for k in ENGINES}
        samples.append({'id':r['id'],'features':r['features'],
                        'log_ratios':{k:math.log(median[k]/median['fixed_min_fill']) for k in ENGINES}})
    static=min(ENGINES,key=lambda k:st.mean(s['log_ratios'][k] for s in samples))
    return {'samples':samples,'static_baseline':static,'neighbors':3,'engines':list(ENGINES)}


def choose(model,x):
    require(model['engines']==list(ENGINES) and model['neighbors']==3 and bool(model['samples']))
    nearest=sorted(model['samples'],key=lambda s:(sum((a-b)**2 for a,b in zip(x,s['features'])),s['id']))[:3]
    scores={k:st.mean(s['log_ratios'][k] for s in nearest) for k in ENGINES}
    selected=min(ENGINES,key=lambda k:scores[k])
    default=model['static_baseline']; require(default in ENGINES)
    return selected if scores[selected]-scores[default]<math.log(.9) else default


def dispatch(model,d,seq):
    name=choose(model,features(d,seq))
    return name,meta.run(name,d,seq)


def workload(seed,n,kind,mode):
    d,seq=ad.workload(seed,n,kind); f=seq[0]
    if mode=='structural': return d,seq
    if mode=='repeat': return d,[f]*10
    changed=[]
    for i in range(5):
        j=i%(len(f)-1); s,t=f[j]; altered=dict(t)
        if altered:
            a=min(altered); altered[a]+=i+1
        changed.extend([f[:j]+[(s,altered)]+f[j+1:],f])
    return d,changed


def corpus(split):
    require(split in ('train','holdout'))
    sizes=(8,32) if split=='train' else (16,64)
    start=11100 if split=='train' else 11500
    for i,kind in enumerate(('chain','cycle','triangles')):
        for j,n in enumerate(sizes):
            for k,mode in enumerate(('structural','repeat','values')):
                seed=start+i*100+j*10+k; d,seq=workload(seed,n,kind,mode)
                yield dict(id=f'{split}:{kind}:{n}:{mode}',split=split,kind=kind,n=n,mode=mode,seed=seed),d,seq


def measure(info,d,seq,model=None):
    names=ENGINES+('dispatch',) if model is not None else ENGINES
    times={k:[] for k in names}; results={}; selected=None
    for repeat in range(5):
        rotation=list(names); random.Random(info['seed']+repeat).shuffle(rotation)
        for name in rotation:
            start=time.perf_counter_ns()
            if name=='dispatch': selected,r=dispatch(model,d,seq)
            else: r=meta.run(name,d,seq)
            times[name].append(time.perf_counter_ns()-start)
            if repeat==0: results[name]=r
    checks=0; feasible=0
    for i,f in enumerate(seq):
        expected=ref.solve(d,f)['optimum']; feasible+=expected is not None
        if len(d)==8: require(expected==ref.brute(d,f))
        for name in names:
            x=results[name][i]; r=x['result'] if 'result' in x else x
            normalized=dict(r)
            if "result" not in x and name!="fresh_min_fill":
                full=meta.up.predict(d,f,r["order"])[0]; require(0<=r["assignments_evaluated"]<=full); normalized["assignments_evaluated"]=full
            require(r["optimum"]==expected and cert.verify_solution(d,f,normalized)==normalized["assignments_evaluated"])
            checks+=1
    return {**info,'features':features(d,seq),'times_ns':times,'selected':selected,
            'checks':checks,'feasible':feasible,'instances_sha256':gap.digest([gap.instance_record(d,f) for f in seq])}


def audit():
    train=[measure(info,d,seq) for info,d,seq in corpus('train')]
    model=fit(train); frozen=gap.digest(model)
    held=[measure(info,d,seq,model) for info,d,seq in corpus('holdout')]
    require(gap.digest(model)==frozen and not ({r['instances_sha256'] for r in train}&{r['instances_sha256'] for r in held}))
    controls=0
    for bad in ([],held):
        try: fit(bad)
        except ValueError: controls+=1
        else: raise ValueError('invalid training accepted')
    d,seq=workload(11999,8,'chain','repeat')
    require(choose(model,features(d,seq))==choose(json.loads(json.dumps(model)),features(d,seq))); controls+=1
    try: features(d,[])
    except ValueError: controls+=1
    else: raise ValueError('empty workload accepted')
    ratios={k:[st.median(r['times_ns']['dispatch'])/st.median(r['times_ns'][k]) for r in held] for k in ENGINES}
    geo={k:math.exp(st.mean(map(math.log,v))) for k,v in ratios.items()}
    worst={k:max(v) for k,v in ratios.items()}; baseline=model['static_baseline']
    decision='REVIEW_CANDIDATE' if geo[baseline]<=.9 and worst[baseline]<=1.2 else 'NO_PROMOTION'
    out={'train':train,'holdout':held,'model':model,'model_sha256':frozen,'geomean_ratios':geo,'worst_ratios':worst,'decision':decision,'controls':controls,'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('mra_x_*.py'))},'scope':'batch scopes known in advance; synthetic holdout of different seeds and sizes; five sequential repetitions, randomized order; timing-dependent learning is not deterministic; excludes verification; no independent replication or external solver benchmark; no automatic promotion'}
    out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); r=audit()
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps({k:r[k] for k in ('geomean_ratios','worst_ratios','decision','controls')},indent=2))
