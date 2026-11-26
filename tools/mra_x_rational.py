"""Phase XX: amortized structural surrogate with zero online shadow evaluations."""
import argparse
import hashlib
import json
import math
import random
import statistics as st
import time
from pathlib import Path
import mra_x_temporal as t
import mra_x_separator as sep
import mra_x_gap_agent as gap

require=t.require
WEIGHTS=(0,1,2,4,8)  # quarter-units of anticipated full-order cost


def corpus(split):
    start,sizes={'train':(20100,(8,16)), 'validation':(20500,(12,)), 'test':(20900,(24,32))}[split]
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in sizes:
            for mode in range(2):
                seed=start+i*100+n*2+mode; rng=random.Random(seed)
                d,f=sep.instance(seed,n,kind); vs=list(d)
                stream=[({str(j):x for j,x in enumerate(f)}, {})]
                for j in range(2):
                    v,u=rng.sample(vs,2); z=f'new{j}'; fid=f'edge{j}'
                    k=str(rng.randrange(len(f)-1)); s,tab=f[int(k)]
                    stream.append(({fid:((v,z),{(0,0):0})},{z:2}))
                    if mode: stream.append(({f'bridge{j}':((u,z),{(0,0):1})},{}))
                    if rng.random()<.7: stream.extend([({}, {z:3}),({}, {z:2})])
                    if rng.random()<.6: stream.extend([({k:(s,{})},{}),({k:(s,tab)}, {})])
                    stream.append(({fid:None,**({f'bridge{j}':None} if mode else {})},{z:None}))
                    stream.extend([({}, {u:d[u]+1}),({}, {u:d[u]})])
                stream.append(({},{})); yield f'{split}:{seed}:{kind}:{n}',d,stream


def select(p,weight):
    require(type(weight) is int and weight in WEIGHTS)
    base,alt=p[3:]; opts=p[2]
    if not weight or alt is None: return base,0
    a,b=opts[alt],opts[base]
    # At most two extra scalar scores; no hypothetical kernel calls.
    # Never increase the conservative immediate bound by more than 25%.
    if 4*a['upper']>5*b['upper']: return base,0
    sa=4*a['upper']+weight*a['full']; sb=4*b['upper']+weight*b['full']
    return (alt if 100*sa<=95*sb and sa<sb else base),2


def run(d,stream,weight,verify=False):
    e=t.initial(d); rows=[]
    for edit in stream:
        p=t.prepare(e,*edit); action,scores=select(p,weight)
        e,r=t.execute(e,edit[0],p,action,verify)
        q=r['result']; rows.append(dict(action=action,base=p[3],actual=r['actual'],full=q['assignments_evaluated'],optimum=q['optimum'],scores=scores,shadow_visits=0))
    return rows


def aggregate(split,weight,verify=True):
    batches=[]
    for name,d,stream in corpus(split):
        batches.append(dict(id=name,rows=run(d,stream,weight,verify)))
    return batches


def total(batches):
    rows=[r for b in batches for r in b['rows']]
    return dict(work=sum(r['actual'] for r in rows),transactions=len(rows),departures=sum(r['action']!=r['base'] for r in rows),scores=sum(r['scores'] for r in rows),shadow_visits=sum(r['shadow_visits'] for r in rows))


def equal(a,b):
    require([x['id'] for x in a]==[x['id'] for x in b])
    require([[r['optimum'] for r in x['rows']] for x in a]==[[r['optimum'] for r in x['rows']] for x in b])


def audit(modelpath):
    train0=aggregate('train',0); training=[]; checks=total(train0)['transactions']
    for w in WEIGHTS:
        a=train0 if w==0 else aggregate('train',w); equal(train0,a)
        if w: checks+=total(a)['transactions']
        training.append(dict(weight=w,**total(a)))
    candidate=min(training[1:],key=lambda r:(r['work'],r['weight']))['weight']
    va=aggregate('validation',candidate); vb=aggregate('validation',0); equal(va,vb)
    validation=[dict(weight=0,**total(vb)),dict(weight=candidate,**total(va))]; checks+=total(va)['transactions']+total(vb)['transactions']
    selected=candidate if validation[1]['work']<=.95*validation[0]['work'] else 0
    model=dict(schema=1,candidate=candidate,selected=selected,weights=list(WEIGHTS),training_ids=[b['id'] for b in train0],validation_ids=[b['id'] for b in vb],shadow_budget=0)
    h=gap.digest(model)
    with modelpath.open('x') as f: json.dump(dict(model=model,sha256=h),f,indent=2)
    loaded=json.loads(modelpath.read_text()); require(gap.digest(loaded['model'])==loaded['sha256']==h); model=loaded['model']
    base=aggregate('test',0); active=aggregate('test',model['candidate']); equal(base,active); checks+=total(base)['transactions']+total(active)['transactions']
    require(not ({b['id'] for b in base}&set(model['training_ids']+model['validation_ids'])))
    times=[]
    for i,(name,d,stream) in enumerate(corpus('test')):
        elapsed={'baseline':[],'active':[]}
        for j in range(3):
            names=list(elapsed); random.Random(i*17+j).shuffle(names)
            for k in names:
                start=time.perf_counter_ns(); run(d,stream,model['candidate'] if k=='active' else 0); elapsed[k].append(time.perf_counter_ns()-start)
        times.append(dict(id=name,ns=elapsed))
    controls=1
    for bad in (-1,True,3,100):
        try: select((None,None,{},'indexed',None),bad)
        except ValueError: controls+=1
        else: raise ValueError('invalid weight')
    p=(None,None,{'preserve':{'upper':8,'full':100},'reorder':{'upper':11,'full':1}},'preserve','reorder')
    require(select(p,8)==('preserve',0)); controls+=1
    require(select(p,0)==('preserve',0)); controls+=1
    require(gap.digest(model)==h); controls+=1
    b,a=total(base),total(active); require(a['shadow_visits']==0 and a['scores']<=2*a['transactions'])
    ratios=[st.median(x['ns']['active'])/st.median(x['ns']['baseline']) for x in times]; geo=math.exp(st.mean(map(math.log,ratios))); worst=max(ratios)
    out=dict(training=training,validation=validation,model_sha256=h,candidate=candidate,selected=selected,checks=checks,controls=controls,baseline=b,active=a,rows=dict(baseline=base,active=active),times=times,geomean_ratio=geo,worst_ratio=worst,decision='REVIEW_CANDIDATE' if selected and a['work']<=.9*b['work'] and geo<=.9 and worst<=1.2 else 'NO_PROMOTION',source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('mra_x_*.py'))},scope='offline grid selection of structural cost surrogate; zero online shadow kernel executions; scalar scoring only after Phase XV planning; no wall-time cap; synthetic in-memory timings exclude training, verification and persistence; no formal proof or deployment')
    out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); p.add_argument('--model',type=Path,required=True); a=p.parse_args(); r=audit(a.model)
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps({k:v for k,v in r.items() if k not in ('rows','times','source_sha256')},indent=2))
