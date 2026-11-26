"""Matched Phase XXXV verification and compression ablation."""
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
import mra_x_localverify as local
import mra_x_routed as r
import mra_x_service as s
import mra_x_singlepass as sp
import mra_x_state as state
import mra_x_separator as sep
import mra_x_topology as ref


def corpus():
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in (12,48):
            d,fs=sep.instance(35100+i*100+n,n,kind); v=next(iter(d)); f=fs[0]; tab=dict(f[1]); row=next(iter(tab)); tab[row]+=5
            edits=[({str(j):x for j,x in enumerate(fs)},{}),({'0':(f[0],tab)},{}),({'0':f},{}),({'new':((v,'extra'),{(0,0):0})},{'extra':2}),({}, {'extra':3}),({'new':None},{'extra':None}),({}, {v:d[v]+1}),({}, {v:d[v]}),({'0':(f[0],{})},{}),({'0':f},{}),({'duplicate':f},{}),({'duplicate':None},{})]+[({}, {})]*6
            yield f'{kind}-{n}',d,edits


def run(cls,path,d,edits,check=False):
    store=cls(path,d); rows=[]
    for j,(es,ds) in enumerate(edits):
        x=store.apply(es,ds); q=x['receipt']; e=store.engine
        if check:
            rr=ref.solve(e.d,list(e.inputs.values()),e.order); receipt=k.check(s.certificate(e,rr))
            a.require(all(q[key]==receipt[key] for key in ('problem_sha256','certificate_sha256','optimum','variables','visits')) and store.get(store.version)==receipt)
            restored=state.restore(state.snapshot(e,store.version)); a.require(restored.buckets==e.buckets and restored.counts==e.counts)
        rows.append(dict(optimum=q['optimum'],action=x['action'],actual=x['actual'],full=q['visits'],fresh=q.get('fresh',q['visits']),hits=q.get('hits',0),keys=q.get('keys_built',e.n),routes=q.get('rewired',q.get('routes',len(e.inputs)+e.n)),local=q.get('local',False),memlevel=q.get('memlevel',0)))
        if j==5:
            old=state.snapshot(e,store.version); store=cls(path); a.require(state.snapshot(store.engine,store.version)==old)
    history=[store.get(v) for v in (3,6,12,18)]
    if check:
        versions,docs,demand=store.history(); a.require(versions==list(range(3,19)) and all(k.check(docs[v-3])==h for v,h in zip((3,6,12,18),history)))
    with sqlite3.connect(path) as db: pages=db.execute('PRAGMA page_count').fetchone()[0]*db.execute('PRAGMA page_size').fetchone()[0]
    return dict(rows=rows,history=history,pages=pages)


def controls(root):
    path=root/'control.sqlite'; x=local.Store(path,{'a':2,'b':2}); x.apply({'f':(('a','b'),{(0,0):0,(0,1):0})}); q=x.apply({'f':(('a','b'),{(1,0):0,(1,1):0})})['receipt']; a.require(q['hits']==1 and q['keys_built']==1); total=1
    old=state.snapshot(x.engine,x.version); receipts=copy.deepcopy(x._receipts)
    def reject(fn,errors=(ValueError,)):
        nonlocal total
        try: fn()
        except errors: total+=1
        else: raise ValueError('invalid state accepted')
    def unchanged():
        a.require(state.snapshot(x.engine,x.version)==old and x._receipts==receipts and state.snapshot(local.Store(path).engine,x.version)==old)
    execute=s.t.execute
    for mode in ('objective','witness','trace','bool','message','input','count','id'):
        def faulty(*args):
            e,z=execute(*args); rr=z['result']
            if mode=='objective': rr['optimum']=99
            if mode=='witness': rr['witness']['a']=0
            if mode=='trace': rr['trace'][0][2][0][1]=0; e.records=copy.deepcopy(rr['trace'])
            if mode=='bool': rr['trace'][1][2][0][1]=False; e.records=copy.deepcopy(rr['trace'])
            if mode=='message': e.outputs[0][1][(0,)]=99
            if mode=='input': e.inputs['f']=(('a','b'),{(0,0):0})
            if mode=='count': e.counts[0]+=1
            if mode=='id': e.inputs['other']=e.inputs.pop('f')
            return e,z
        with patch.object(s.t,'execute',faulty): reject(lambda:x.apply({}))
        unchanged()
    with sqlite3.connect(path) as db: db.execute("CREATE TRIGGER refuse BEFORE INSERT ON dense_versions BEGIN SELECT RAISE(ABORT,'injected'); END")
    reject(lambda:x.apply({'f':(('a',),{(0,):4})}),(sqlite3.IntegrityError,)); unchanged()
    with sqlite3.connect(path) as db: db.execute('DROP TRIGGER refuse')
    stale=local.Store(path); q=x.apply({})['receipt']; a.require(q['rewired']==q['keys_built']==q['fresh']==0); total+=1
    reject(lambda:stale.apply({})); a.require(stale._receipts==receipts and stale.version==old['version'])
    q=x.apply({'f':(('b',),{(0,):2})})['receipt']; a.require(q['optimum']==2 and q['rewired']>0); total+=1
    q=x.apply({'constant':((),{():-3})})['receipt']; a.require(q['optimum']==-1 and q['keys_built']==0); total+=1
    q=x.apply({}, {'b':3})['receipt']; a.require(not q['local']); total+=1
    y=local.Store(path); a.require(y.seed['hits']==0 and y.get(y.version)['optimum']==-1); total+=1
    return total


def audit(root):
    root=root.resolve(); root.mkdir(); rows=[]; timings=[]; methods={'full':s.Store,'routed':r.Store,'singlepass':sp.Store,'local':local.Store,'adaptive':local.Adaptive}
    for i,(name,d,edits) in enumerate(corpus()):
        results={key:run(cls,root/f'{name}-{key}.sqlite',d,edits,True) for key,cls in methods.items()}
        for key in methods:
            a.require(results[key]['history']==results['full']['history'])
            for x,y in zip(results[key]['rows'],results['full']['rows']): a.require(all(x[k]==y[k] for k in ('optimum','action','actual','full')))
        for key in ('local','adaptive'):
            for x,y in zip(results[key]['rows'],results['singlepass']['rows']): a.require(all(x[k]==y[k] for k in ('fresh','hits')))
        rows.append(dict(name=name,**results)); ns={key:[] for key in methods}
        for rep in range(3):
            labels=list(methods); random.Random(i*19+rep).shuffle(labels)
            for key in labels:
                path=root/f'timing-{i}-{rep}-{key}.sqlite'; start=time.perf_counter_ns(); run(methods[key],path,d,edits); ns[key].append(time.perf_counter_ns()-start); path.unlink()
        timings.append(dict(name=name,ns=ns))
    ratios={key:[st.median(x['ns']['local'])/st.median(x['ns'][key]) for x in timings] for key in ('full','routed','singlepass')}; geo={key:math.exp(st.mean(map(math.log,v))) for key,v in ratios.items()}; worst={key:max(v) for key,v in ratios.items()}
    adaptive=math.exp(st.mean(math.log(st.median(x['ns']['adaptive'])/st.median(x['ns']['local'])) for x in timings))
    physical=sum(x['local']['pages'] for x in rows)/sum(x['routed']['pages'] for x in rows); ncontrols=controls(root)
    out=dict(rows=rows,controls=ncontrols,timings=timings,geomean=geo,worst=worst,adaptive_ratio=adaptive,physical_ratio=physical,decision='REVIEW_CANDIDATE' if ncontrols==16 and max(geo.values())<=.9 and max(worst.values())<=1.2 and physical<=.5 else 'NO_PROMOTION',scope='fixed-domain/order copy-on-write verified routes, all certificate fields still scanned; migration fallback; size-based compression ablation; local warm SQLite timing includes create, 18 commits, reopen, four historical reads, page accounting; not RSS or power-loss or formal proof')
    out['evidence_sha256']=a.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--directory',type=Path,required=True); args=p.parse_args(); out=audit(args.directory); (args.directory/'evidence.json').write_bytes(a.canonical(out)); print(json.dumps({key:out[key] for key in ('controls','geomean','worst','adaptive_ratio','physical_ratio','decision')},indent=2))
