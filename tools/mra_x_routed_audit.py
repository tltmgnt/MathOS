"""Matched durable transaction and reconstruction audit."""
import argparse
import copy
import json
import math
import random
import sqlite3
import statistics as st
import time
from pathlib import Path
from unittest.mock import patch
import mra_x_archive as a
import mra_x_kernel as k
import mra_x_service as s
import mra_x_precommit as p
import mra_x_routed as r
import mra_x_state as state
import mra_x_separator as sep
import mra_x_topology as ref


def corpus():
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in (8,32,64):
            d,fs=sep.instance(30100+i*100+n,n,kind); v=next(iter(d)); f=fs[0]
            edits=[({str(j):x for j,x in enumerate(fs)},{}),({},{}),({'new':((v,'extra'),{(0,0):0})},{'extra':2}),({}, {'extra':3}),({'new':None},{'extra':None}),({}, {v:d[v]+1}),({}, {v:d[v]}),({'0':(f[0],{})},{}),({'0':f},{}),({},{}),({'duplicate':f},{}),({'duplicate':None},{})]
            yield f'{kind}-{n}',d,edits


def run(cls,path,d,edits,check=False):
    start=time.perf_counter_ns(); store=cls(path,d); init=time.perf_counter_ns()-start; rows=[]; profile={key:0 for key in ('solver','gate','persist')}; reopen=0
    for j,(es,ds) in enumerate(edits):
        x=store.apply(es,ds); q=x['receipt']; e=store.engine
        if check:
            result=ref.solve(e.d,list(e.inputs.values()),e.order); a.require(result['optimum']==q['optimum']); receipt=k.check(s.certificate(e,result))
            a.require(all(q[key]==receipt[key] for key in ('problem_sha256','certificate_sha256','optimum','variables','visits')) and store.get(store.version)==receipt)
            if cls is r.Store:
                restored=state.restore(state.snapshot(e,store.version)); a.require(restored.buckets==e.buckets and restored.counts==e.counts)
        rows.append(dict(version=x['version'],action=x['action'],actual=x['actual'],optimum=q['optimum'],full=q['visits'],fresh=q.get('fresh',q['visits']),hits=q.get('hits',0),lookups=q['lookups'],routes=q.get('routes',0)))
        for key,value in x.get('profile_ns',{}).items(): profile[key]+=value
        if j==5:
            old=state.snapshot(e,store.version); begin=time.perf_counter_ns(); store=cls(path); reopen=time.perf_counter_ns()-begin; a.require(state.snapshot(store.engine,store.version)==old)
            if cls is r.Store: a.require(store.seed['hits']==0 and store.seed['fresh']==store.seed['visits'])
    return rows,dict(init=init,reopen=reopen,**profile)


def controls(root):
    total=0; path=root/'control.sqlite'; x=r.Store(path,{'a':2,'b':2},budget=16)
    x.apply({'f':(('a','b'),{(0,0):0,(0,1):0})}); q=x.apply({'f':(('a','b'),{(1,0):0,(1,1):0})}); a.require(q['receipt']['hits']==1); total+=1
    old=state.snapshot(x.engine,x.version); receipts=copy.deepcopy(x._receipts)
    def reject(fn,errors=(ValueError,)):
        nonlocal total
        try: fn()
        except errors: total+=1
        else: raise ValueError('bad state accepted')
    def unchanged():
        a.require(state.snapshot(x.engine,x.version)==old and x._receipts==receipts and state.snapshot(r.Store(path).engine,x.version)==old)
    execute=s.t.execute
    for mode in ('optimum','witness','trace','message','input','counts','budget','id'):
        def faulty(*args):
            e,z=execute(*args); result=z['result']
            if mode=='optimum': result['optimum']=99
            if mode=='witness': result['witness']['a']=0
            if mode=='trace': result['trace'][0][2][0][1]=0; e.records=copy.deepcopy(result['trace'])
            if mode=='message': e.outputs[0][1][(0,)]=99
            if mode=='input': e.inputs['f']=(('a','b'),{(0,0):0})
            if mode=='counts': e.counts[0]+=1
            if mode=='budget': e.budget+=1
            if mode=='id': e.inputs['other']=e.inputs.pop('f')
            return e,z
        with patch.object(s.t,'execute',faulty): reject(lambda:x.apply({}))
        unchanged()
    reject(lambda:x.apply({}, {'a':1})); unchanged()
    with sqlite3.connect(path) as db: db.execute("CREATE TRIGGER refuse BEFORE INSERT ON verified BEGIN SELECT RAISE(ABORT,'injected'); END")
    reject(lambda:x.apply({}),(sqlite3.IntegrityError,)); unchanged()
    with sqlite3.connect(path) as db: db.execute('DROP TRIGGER refuse')
    stale=r.Store(path); a.require(x.apply({})['receipt']['fresh']==0); total+=1
    reject(lambda:stale.apply({})); a.require(stale._receipts==receipts and stale.version==old['version'])
    with sqlite3.connect(path) as db:
        v,sh,sr,ch,cr,reads=db.execute('SELECT * FROM verified ORDER BY version DESC LIMIT 1').fetchone(); snap=json.loads(sr); snap['counts'][0]+=1; db.execute('UPDATE verified SET sh=?,snapshot=? WHERE version=?',(a.digest(snap),a.canonical(snap),v))
    reject(lambda:r.Store(path))
    return total


def audit(root):
    root=root.resolve(); root.mkdir(); rows=[]; timings=[]; methods={'full':s.Store,'incremental':p.Store,'routed':r.Store}
    for i,(name,d,edits) in enumerate(corpus()):
        results={label:run(cls,root/f'{name}-{label}.sqlite',d,edits,True)[0] for label,cls in methods.items()}
        for x,y,z in zip(*results.values()):
            a.require(all(x[key]==y[key]==z[key] for key in ('version','action','actual','optimum','full')) and y['fresh']==z['fresh'] and y['hits']==z['hits'])
        rows.append(dict(name=name,**results)); elapsed={label:[] for label in methods}; profiles={label:[] for label in methods}
        for rep in range(3):
            labels=list(methods); random.Random(i*19+rep).shuffle(labels)
            for label in labels:
                path=root/f'timing-{i}-{rep}-{label}.sqlite'; start=time.perf_counter_ns(); _,profile=run(methods[label],path,d,edits); elapsed[label].append(time.perf_counter_ns()-start); profiles[label].append(profile); path.unlink()
        timings.append(dict(name=name,ns=elapsed,profiles=profiles))
    ratios={label:[st.median(x['ns']['routed'])/st.median(x['ns'][label]) for x in timings] for label in ('full','incremental')}
    geo={label:math.exp(st.mean(map(math.log,x))) for label,x in ratios.items()}; worst={label:max(x) for label,x in ratios.items()}
    out=dict(rows=rows,controls=controls(root),timings=timings,geomean=geo,worst=worst,decision='REVIEW_CANDIDATE' if max(geo.values())<=.9 and max(worst.values())<=1.2 else 'NO_PROMOTION',scope='synthetic matched SQLite batches, initialization, 12 edits, reopen; independent routed checker reconstructs all routes and validates all certificate schemas; enumeration only on changed receipts; full check on reopening without solver replay; no claim of fully dependency-local processing or formal proof')
    out['evidence_sha256']=a.digest(out); return out


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--directory',type=Path,required=True); args=parser.parse_args(); out=audit(args.directory); (args.directory/'evidence.json').write_bytes(a.canonical(out))
    print(json.dumps({key:out[key] for key in ('controls','geomean','worst','decision')},indent=2))
