"""Phase XVI: persistent measured migration policy, frozen online inference."""
import argparse
import copy
import hashlib
import json
import math
import random
import sqlite3
import statistics as st
import tempfile
import time
from pathlib import Path
import mra_x_arbitrate as arb
import mra_x_state as state
import mra_x_indexed as idx
import mra_x_topology as ref
import mra_x_certify as cert
import mra_x_gap_agent as gap
import mra_x_separator as sep

ACTIONS=('rebuild','reorder','preserve')
require=arb.require


def features(d,inputs,x):
    return [math.log1p(len(d)),math.log1p(len(inputs)),math.log1p(x['upper']),math.log1p(x['full']),x['hits']/max(1,len(d))]


def predict(samples,label,x):
    near=sorted((s for s in samples if s['action']==label),key=lambda s:sum((a-b)**2 for a,b in zip(x,s['x'])))[:5]
    if not near: return None
    return st.median(s['ns'] for s in near)


def choose(samples,d,inputs,options,viable):
    base=min(viable,key=lambda k:(options[k]['upper'],options[k]['full'],ACTIONS.index(k)))
    scores={k:predict(samples,k,features(d,inputs,options[k])) for k in viable}
    if any(v is None for v in scores.values()): return base,scores
    best=min(viable,key=lambda k:(scores[k],ACTIONS.index(k)))
    return (best if scores[best]<=.85*scores[base] else base),scores


def save_model(path,samples):
    require(0<len(samples)<=2048 and all(s['action'] in ACTIONS and s['ns']>0 and len(s['x'])==5 for s in samples))
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE IF NOT EXISTS model (id INTEGER PRIMARY KEY CHECK(id=1), digest TEXT, payload TEXT)')
        db.execute('INSERT INTO model VALUES (1,?,?)',(gap.digest(samples),gap.canonical(samples)))


def load_model(path):
    with sqlite3.connect(path) as db: h,raw=db.execute('SELECT digest,payload FROM model WHERE id=1').fetchone()
    samples=json.loads(raw); require(gap.digest(samples)==h); return samples


class Learned(arb.Store):
    def __init__(self,path,domains=None,*,samples=(),calibrate=False):
        super().__init__(path,domains); self.samples=copy.deepcopy(list(samples)); self.calibrate=calibrate

    def apply(self,edits,domain_edits=None):
        d=dict(self.engine.d); inputs=dict(self.engine.inputs)
        for v,k in (domain_edits or {}).items():
            if k is None:
                if v not in d: raise ValueError('unknown variable')
                del d[v]
            else: d[v]=k
        if d==self.engine.d: return super().apply(edits,domain_edits)
        for k,f in edits.items():
            if not isinstance(k,str) or not k or len(k)>128: raise ValueError('factor ID')
            if f is None:
                if k not in inputs: raise ValueError('unknown factor')
                del inputs[k]
            else: inputs[k]=(tuple(f[0]),dict(f[1]))
        if len(inputs)>1024: raise ValueError('factor limit')
        ref.validate(d,list(inputs.values())); idx.Indexed(d,sorted(d),self.engine.budget)
        stable=[v for v in self.engine.order if v in d]+sorted(set(d)-set(self.engine.d)); fresh=ref.min_fill(d,list(inputs.values()))
        options={}
        for label,o in (('preserve',stable),('reorder',fresh)):
            upper,full,hits=arb.estimate(self.engine,d,inputs,o); options[label]=dict(upper=upper,full=full,hits=hits,order=o)
        options['rebuild']=dict(upper=options['reorder']['full'],full=options['reorder']['full'],hits=0,order=fresh)
        viable=[k for k in ACTIONS if options[k]['full']<=self.engine.budget]
        if not viable: raise idx.BudgetExceeded('no viable order')
        selected,scores=choose(self.samples,d,inputs,options,viable)
        def execute(k):
            o=options[k]['order']
            if k=='rebuild':
                e=idx.Indexed(d,o,self.engine.budget); r=e.update(inputs)
            else: e,r=arb.transfer(self.engine,d,inputs,o)
            require(r['actual']<=options[k]['upper'] and r['result']['assignments_evaluated']==options[k]['full'])
            return e,r
        new=[]
        if self.calibrate:
            # Training only: evaluate counterfactuals from identical state, no commits.
            timing={k:[] for k in viable}
            for j in range(3):
                rotation=list(viable); random.Random(self.version*17+j).shuffle(rotation)
                for k in rotation:
                    start=time.perf_counter_ns(); e,r=execute(k); timing[k].append(time.perf_counter_ns()-start)
                    require(r['result']==ref.solve(d,list(inputs.values()),e.order))
            new=[dict(action=k,x=features(d,inputs,options[k]),ns=st.median(timing[k])) for k in viable]
        candidate,r=execute(selected); v=self.version+1
        telemetry=dict(version=v,selected=selected,options=options,bound=options[selected]['upper'],actual=r['actual'],full=r['result']['assignments_evaluated'],predicted_ns=scores,model_sha256=gap.digest(self.samples))
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT max(version) FROM checkpoints').fetchone()[0]!=self.version: raise state.StaleState('reopen')
            self.write(db,candidate,v)
            db.execute('INSERT INTO arbitration VALUES (?,?,?)',(v,gap.digest(telemetry),gap.canonical(telemetry)))
            db.execute('DELETE FROM arbitration WHERE version<=?',(v-self.retain,))
        self.engine=candidate; self.version=v; self.samples.extend(new)
        return dict(r,decision=telemetry)


def corpus(train):
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in ((8,24,48) if train else (16,32,64)):
            seed=(16100 if train else 16600)+i*100+n; d,f=sep.instance(seed,n,kind); v=next(iter(d)); last=list(d)[-1]
            edge=((v,'extra'),{(0,0):0}); other=((last,'extra'),{(0,0):1})
            stream=[({str(j):x for j,x in enumerate(f)},{}),({'new':edge},{'extra':2}),({}, {'extra':3}),({'other':other},{}),({'other':None,'new':None},{'extra':None}),({}, {v:d[v]+1}),({}, {v:d[v]}),({'0':(f[0][0],{})},{}),({'0':f[0]},{}),({}, {})]
            yield f'{kind}:{n}:{seed}',d,stream


def run(path,d,stream,samples=None,calibrate=False,verify=False):
    a=arb.Store(path,d) if samples is None else Learned(path,d,samples=samples,calibrate=calibrate)
    rows=[]
    for es,ds in stream:
        x=a.apply(es,ds); r=x['result']; e=a.engine; fs=list(e.inputs.values())
        if verify:
            require(r==ref.solve(e.d,fs,e.order) and cert.verify_solution(e.d,fs,r)==r['assignments_evaluated'])
            if len(e.d)<=9: require(r['optimum']==ref.brute(e.d,fs))
        rows.append(dict(optimum=r['optimum'],actual=x['actual'],selected=x['decision']['selected']))
    return rows,a


def audit():
    controls=0; samples=[]; train=[]; held=[]; recoveries=0
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp); modelpath=root/'model.sqlite'
        for i,(name,d,stream) in enumerate(corpus(True)):
            rows,a=run(root/f'train{i}.sqlite',d,stream,samples,True,True); samples=a.samples
            train.append(dict(id=name,rows=rows,samples=len(samples)))
        save_model(modelpath,samples); frozen=gap.digest(samples); samples=load_model(modelpath); require(gap.digest(samples)==frozen); controls+=1
        for i,(name,d,stream) in enumerate(corpus(False)):
            rows,a=run(root/f'learn{i}.sqlite',d,stream,samples,False,True); base,b=run(root/f'base{i}.sqlite',d,stream,None,False,True)
            require([r['optimum'] for r in rows]==[r['optimum'] for r in base] and gap.digest(a.samples)==frozen)
            reopened=Learned(a.path,samples=load_model(modelpath)); require(state.snapshot(reopened.engine,reopened.version)==state.snapshot(a.engine,a.version) and reopened.history()==a.history()); recoveries+=1
            times={k:[] for k in ('learned','phase15')}
            for j in range(5):
                rotation=list(times); random.Random(i*17+j).shuffle(rotation)
                for k in rotation:
                    start=time.perf_counter_ns(); run(root/f'time{i}-{j}-{k}.sqlite',d,stream,samples if k=='learned' else None); times[k].append(time.perf_counter_ns()-start)
            held.append(dict(id=name,rows=rows,baseline=base,times_ns=times))
        with sqlite3.connect(modelpath) as db: db.execute('UPDATE model SET digest=?',('0'*64,))
        try: load_model(modelpath)
        except ValueError: controls+=1
        else: raise ValueError('corrupt model accepted')
        d={'a':2}; inputs={}; opts={k:dict(upper=2,full=2,hits=0) for k in ACTIONS}; require(choose([],d,inputs,opts,list(ACTIONS))[0]=='rebuild'); controls+=1
        a=Learned(root/'rollback.sqlite',d,samples=samples); a.apply({'f':(('a',),{(1,):0})}); before=state.snapshot(a.engine,a.version)
        try: a.apply({}, {'a':1})
        except ValueError: require(state.snapshot(a.engine,a.version)==before and gap.digest(a.samples)==frozen); controls+=1
        else: raise ValueError('invalid shrink accepted')
    ratios=[st.median(h['times_ns']['learned'])/st.median(h['times_ns']['phase15']) for h in held]
    geo=math.exp(st.mean(map(math.log,ratios))); worst=max(ratios)
    out=dict(train=train,holdout=held,model=samples,model_sha256=frozen,controls=controls,recoveries=recoveries,geomean_ratio=geo,worst_ratio=worst,decision='REVIEW_CANDIDATE' if geo<=.9 and worst<=1.2 else 'NO_PROMOTION',source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('mra_x_*.py'))},scope='training shadow executions; frozen current-edit inference; local synthetic timings include SQLite and output, exclude verification and training; no production or formal claim')
    out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); r=audit()
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps({k:r[k] for k in ('controls','recoveries','geomean_ratio','worst_ratio','decision')},indent=2))
