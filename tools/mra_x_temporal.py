"""Phase XVII: three-transaction counterfactual learning for online migration."""
import argparse
import copy
import hashlib
import json
import math
import random
import statistics as st
import time
from pathlib import Path
import mra_x_arbitrate as arb
import mra_x_indexed as idx
import mra_x_topology as ref
import mra_x_certify as cert
import mra_x_gap_agent as gap
import mra_x_separator as sep

ACTIONS=('rebuild','reorder','preserve')
HORIZON=3
require=arb.require


def initial(d,budget=1000000):
    e=idx.Indexed(d,sorted(d),budget); e.update({}); return e


def prepare(e,edits,domain_edits):
    d=dict(e.d); inputs=dict(e.inputs)
    for v,k in domain_edits.items():
        if k is None:
            if v not in d: raise ValueError('unknown variable')
            del d[v]
        else: d[v]=k
    for k,f in edits.items():
        if not isinstance(k,str) or not k or len(k)>128: raise ValueError('factor ID')
        if f is None:
            if k not in inputs: raise ValueError('unknown factor')
            del inputs[k]
        else: inputs[k]=(tuple(f[0]),dict(f[1]))
    if len(inputs)>1024 or len(edits)>2048: raise ValueError('factor limit')
    ref.validate(d,list(inputs.values())); idx.Indexed(d,sorted(d),e.budget)
    if d==e.d: return d,inputs,{},'indexed',None
    stable=[v for v in e.order if v in d]+sorted(set(d)-set(e.d)); fresh=ref.min_fill(d,list(inputs.values()))
    options={}
    for name,o in (('preserve',stable),('reorder',fresh)):
        upper,full,hits=arb.estimate(e,d,inputs,o); options[name]=dict(order=o,upper=upper,full=full,hits=hits)
    options['rebuild']=dict(order=fresh,upper=options['reorder']['full'],full=options['reorder']['full'],hits=0)
    viable=[k for k in ACTIONS if options[k]['full']<=e.budget]
    if not viable: raise idx.BudgetExceeded('no viable order')
    base=min(viable,key=lambda k:(options[k]['upper'],options[k]['full'],ACTIONS.index(k)))
    # The two min-fill paths have identical final numerical state; consider only one alternate order.
    alt='preserve' if base!='preserve' else 'reorder'
    if alt not in viable or options[alt]['order']==options[base]['order']: alt=None
    return d,inputs,options,base,alt


def context(e,d,inputs,options,base,alt,past):
    b,a=options[base],options[alt]
    return [math.log2(max(1,len(d)))/7, math.log2(max(1,len(inputs)))/10,
            math.log((a['upper']+1)/(b['upper']+1)),math.log((a['full']+1)/(b['full']+1)),
            (a['hits']-b['hits'])/max(1,len(d)),sum(past[-3:])/3,
            sum(e.d.get(v)!=d.get(v) for v in set(e.d)|set(d))/max(1,len(d))]


def select(samples,x,base,alt):
    if alt is None: return base
    near=sorted(samples,key=lambda s:sum((a-b)**2 for a,b in zip(x,s['x'])))[:5]
    # Conservative departure: local majority and >=10% median predicted horizon saving.
    if len(near)<5: return base
    if sum((a-b)**2 for a,b in zip(x,near[-1]['x']))>1: return base
    return alt if sum(s['gain']>0 for s in near)>=4 and st.median(s['gain'] for s in near)>=.1 else base


def execute(e,edits,prepared,action,verify=False):
    d,inputs,options,base,alt=prepared
    if action=='indexed':
        new=copy.deepcopy(e); r=new.update(edits)
    else:
        p=options[action]
        if action=='rebuild':
            new=idx.Indexed(d,p['order'],e.budget); r=new.update(inputs)
        else: new,r=arb.transfer(e,d,inputs,p['order'])
        require(r['actual']<=p['upper'] and r['result']['assignments_evaluated']==p['full'])
    if verify:
        q=r['result']; fs=list(new.inputs.values())
        require(q==ref.solve(d,fs,new.order) and cert.verify_solution(d,fs,q)==q['assignments_evaluated'])
    return new,r


def step(e,edit,samples,past,verify=False):
    es,ds=edit; p=prepare(e,es,ds); d,inputs,opts,base,alt=p
    x=context(e,d,inputs,opts,base,alt,past) if alt else None
    action=select(samples,x,base,alt) if alt else base
    new,r=execute(e,es,p,action,verify)
    return new,dict(action=action,base=base,actual=r['actual'],full=r['result']['assignments_evaluated'],optimum=r['result']['optimum'],migration=d!=e.d)


def rollout(e,stream,p,action):
    new,r=execute(e,stream[0][0],p,action,True); costs=[r['actual']]; opt=[r['result']['optimum']]
    for edit in stream[1:HORIZON]:
        new,row=step(new,edit,[],[],True); costs.append(row['actual']); opt.append(row['optimum'])
    return costs,opt


def corpus(train):
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in ((8,24) if train else (16,48)):
            for mode in range(3):
                seed=(17100 if train else 17600)+i*100+n*3+mode
                d,f=sep.instance(seed,n,kind); vs=list(d); v=vs[0] if mode==0 else vs[n//2] if mode==1 else vs[-1]
                u=vs[-1] if v!=vs[-1] else vs[0]
                edge=((v,'extra'),{(0,0):0}); other=((u,'extra'),{(0,0):1})
                change=({'0':(f[0][0],{})},{}) if mode==0 else ({'other':other},{}) if mode==1 else ({},{v:d[v]+1})
                undo=({'0':f[0]},{}) if mode==0 else ({'other':None},{}) if mode==1 else ({},{v:d[v]})
                stream=[({str(j):a for j,a in enumerate(f)},{}),({'new':edge},{'extra':2}),change,undo,({}, {'extra':3}),({},{}),({'new':None},{'extra':None}),({}, {v:d[v]+1}),({}, {v:d[v]}),({}, {})]
                yield f'{kind}:{n}:{mode}:{seed}',d,stream


def train_model():
    samples=[]; comparisons=checks=0; ids=[]
    for name,d,stream in corpus(True):
        ids.append(name); e=initial(d); past=[]
        for t,edit in enumerate(stream):
            p=prepare(e,*edit); nd,inputs,opts,base,alt=p
            if alt and t+HORIZON<=len(stream):
                b,bo=rollout(e,stream[t:t+HORIZON],p,base); a,ao=rollout(e,stream[t:t+HORIZON],p,alt); require(bo==ao)
                samples.append(dict(id=name,step=t,x=context(e,nd,inputs,opts,base,alt,past),base=base,alt=alt,base_costs=b,alt_costs=a,gain=(sum(b)-sum(a))/max(1,sum(b))))
                comparisons+=1; checks+=2*HORIZON
            e,row=step(e,edit,[],past,True); past.append(int(row['migration'])); checks+=1
    return dict(schema=1,horizon=HORIZON,samples=samples,training_ids=ids),comparisons,checks


def run(d,stream,samples,verify=False):
    e=initial(d); rows=[]; past=[]
    for edit in stream:
        e,r=step(e,edit,samples,past,verify); rows.append(r); past.append(int(r['migration']))
        if verify and len(e.d)<=9: require(r['optimum']==ref.brute(e.d,list(e.inputs.values())))
    return rows


def audit(modelpath):
    model,comparisons,checks=train_model(); h=gap.digest(model)
    with modelpath.open('x') as f: json.dump(dict(model=model,sha256=h),f,indent=2)
    loaded=json.loads(modelpath.read_text()); require(gap.digest(loaded['model'])==loaded['sha256']==h)
    samples=loaded['model']['samples']; rows=[]; performance=[]; controls=1
    for i,(name,d,stream) in enumerate(corpus(False)):
        require(name not in model['training_ids']); a=run(d,stream,samples,True); b=run(d,stream,[],True)
        require([r['optimum'] for r in a]==[r['optimum'] for r in b]); checks+=2*len(stream)
        rows.append(dict(id=name,learned=a,baseline=b))
        times={'learned':[],'baseline':[]}
        for j in range(3):
            names=list(times); random.Random(i*11+j).shuffle(names)
            for k in names:
                start=time.perf_counter_ns(); run(d,stream,samples if k=='learned' else []); times[k].append(time.perf_counter_ns()-start)
        performance.append(dict(id=name,times_ns=times))
    require(gap.digest(loaded['model'])==h); controls+=1
    require(select([],None,'rebuild',None)=='rebuild'); controls+=1
    e=initial({'a':2},budget=4); before=copy.deepcopy(e.__dict__)
    try: step(e,({}, {'a':0}),samples,[])
    except ValueError: require(e.__dict__==before); controls+=1
    else: raise ValueError('invalid edit accepted')
    try: step(e,({'g':(('a','b'),{(0,0):0})}, {'b':4}),samples,[])
    except idx.BudgetExceeded: require(e.__dict__==before); controls+=1
    else: raise ValueError('budget accepted')
    total={k:sum(r['actual'] for batch in rows for r in batch[k]) for k in ('learned','baseline')}
    ratios=[st.median(p['times_ns']['learned'])/st.median(p['times_ns']['baseline']) for p in performance]
    geo=math.exp(st.mean(map(math.log,ratios))); worst=max(ratios)
    out=dict(rows=rows,model_sha256=h,training_comparisons=comparisons,checks=checks,controls=controls,totals=total,performance=performance,geomean_ratio=geo,worst_ratio=worst,decision='REVIEW_CANDIDATE' if total['learned']<=.9*total['baseline'] and geo<=.9 and worst<=1.2 else 'NO_PROMOTION',source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('mra_x_*.py'))},scope='three-step enumeration rollouts at training only; frozen current-edit/past-only inference; in-memory transactions, no SQLite timings; synthetic repeated local measurements, not independent replication or formal proof')
    out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); p.add_argument('--model',type=Path,required=True); a=p.parse_args(); r=audit(a.model)
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps({k:r[k] for k in ('training_comparisons','checks','controls','totals','geomean_ratio','worst_ratio','decision')},indent=2))
