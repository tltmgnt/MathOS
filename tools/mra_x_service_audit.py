"""Matched local integration audit; separate observed and later retrievals."""
import argparse
import copy
import io
import json
import random
import sqlite3
import statistics as st
import time
from pathlib import Path
from unittest.mock import patch
import mra_x_service as s
import mra_x_storage as storage_engine
import mra_x_archive as a
import mra_x_kernel as k
import mra_x_state as state
import mra_x_separator as sep
import mra_x_topology as ref
import mra_x_arbitrate as arb


def corpus():
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in (8,32):
            d,fs=sep.instance(28100+i*100+n,n,kind); v=next(iter(d)); f=fs[0]
            edge=((v,'extra'),{(0,0):0}); other=((list(d)[-1],'extra'),{(0,0):1})
            edits=[({str(j):x for j,x in enumerate(fs)},{}),({'new':edge},{'extra':2}),({}, {'extra':3}),({'other':other},{}),({'other':None,'new':None},{'extra':None}),({}, {v:d[v]+1}),({}, {v:d[v]}),({'0':(f[0],{})},{}),({'0':f},{}),({}, {})]
            yield f'{kind}-{n}',d,edits


def audit(root):
    root=root.resolve(); root.mkdir(); rows=[]; timings=[]; controls=0; reopens=0
    for i,(name,d,edits) in enumerate(corpus()):
        path=root/(name+'.sqlite'); store=s.Store(path,d); base=arb.Store(root/(name+'-baseline.sqlite'),d); transactions=[]
        for j,(es,ds) in enumerate(edits):
            x=store.apply(es,ds); y=base.apply(es,ds); r=x['receipt']; e=store.engine
            a.require(r['optimum']==y['result']['optimum'] and x['actual']==y['actual'] and r['optimum']==ref.solve(e.d,list(e.inputs.values()),e.order)['optimum'])
            if len(e.d)<=9: a.require(r['optimum']==ref.brute(e.d,list(e.inputs.values())))
            transactions.append(dict(version=x['version'],action=x['action'],actual=x['actual'],receipt=r))
            if j in (4,9):
                before=state.snapshot(e,store.version); store=s.Store(path); a.require(state.snapshot(store.engine,store.version)==before); reopens+=1
        versions=list(range(11)); rng=random.Random(28800+i); weights=[1]*11 if i%2==0 else [1]*7+[7]*4
        observed=rng.choices(versions,weights=weights,k=24)
        for v in observed: store.get(v)
        store=s.Store(path); reopens+=1; versions,docs,demand=store.history(); a.require(demand==[observed.count(v)+1 for v in versions])
        (data,manifest),scores=storage_engine.select(versions,docs,demand,12); chosen=manifest['kind']
        packages={'selected':(data,manifest),**{key:storage_engine.package(versions,docs,key) for key in ('gzip','archive','raw8','block8')}}
        files={}; anchors={}; storage={}; metrics={}
        for label,(raw,m) in packages.items():
            dp=root/f'{name}-{label}.bin'; mp=root/f'{name}-{label}.json'; dp.write_bytes(raw); mp.write_bytes(a.canonical(m)); files[label]=(dp,mp); anchors[label]=a.digest(m); storage[label]=dp.stat().st_size+mp.stat().st_size
        def read(label,v):
            dp,mp=files[label]; m=a.load(mp)
            with dp.open('rb') as fp: return storage_engine.retrieve(fp,m,anchors[label],v)
        expected=[k.check(doc) for doc in docs]
        for label in packages:
            for v in versions:
                r=read(label,v)['receipt']; a.require(all(r[key]==expected[v][key] for key in r))
        targets=random.Random(28900+i).choices(versions,weights=weights,k=12)
        for label in packages:
            rr=[read(label,v) for v in targets]; metrics[label]={key:sum(x[key] for x in rr) for key in ('fresh','records','payload_read')}
            metrics[label]['realized_proxy']=storage[label]+metrics[label]['payload_read']+12*files[label][1].stat().st_size+4*metrics[label]['fresh']
        elapsed={key:[] for key in packages}
        for rep in range(3):
            keys=list(packages); random.Random(i*13+rep).shuffle(keys)
            for label in keys:
                start=time.perf_counter_ns()
                for v in targets: read(label,v)
                elapsed[label].append(time.perf_counter_ns()-start)
        timings.append(dict(name=name,ns=elapsed)); rows.append(dict(name=name,transactions=transactions,chosen=chosen,demand=demand,targets=targets,scores=scores,storage=storage,metrics=metrics,anchors=anchors))
    path=root/'control.sqlite'; x=s.Store(path,{'a':2},budget=8); x.apply({'f':(('a',),{(1,):0})}); old=state.snapshot(x.engine,x.version)
    def reject(fn):
        nonlocal controls
        try: fn()
        except ValueError: controls+=1
        else: raise ValueError('invalid operation accepted')
    reject(lambda:x.apply({}, {'a':1})); reject(lambda:x.apply({'g':(('a','b'),{(1,0):0})},{'b':4})); a.require(state.snapshot(x.engine,x.version)==old and state.snapshot(s.Store(path).engine,x.version)==old)
    # Inject a wrong solver result; the portable checker must reject before persistence.
    execute=s.t.execute
    def faulty(*args):
        e,r=execute(*args); r['result']['optimum']=123456; return e,r
    with patch.object(s.t,'execute',faulty): reject(lambda:x.apply({}))
    a.require(state.snapshot(s.Store(path).engine,x.version)==old)
    stale=s.Store(path); x.apply({}); reject(lambda:stale.apply({})); reject(lambda:x.get(999))
    for _ in range(17): x.apply({})
    versions,docs,demand=x.history(); a.require(len(versions)==16 and versions[-1]==x.version); reject(lambda:x.get(0))
    raw,m=storage_engine.package(versions,docs,'block4'); h=a.digest(m); reject(lambda:storage_engine.retrieve(io.BytesIO(raw),m,'0'*64,versions[-1])); reject(lambda:storage_engine.retrieve(io.BytesIO(raw[:-1]),m,h,versions[-1]))
    bad=copy.deepcopy(m); bad['versions'][-1]+=1; reject(lambda:storage_engine.retrieve(io.BytesIO(raw),bad,a.digest(bad),versions[-1]))
    with sqlite3.connect(path) as db: db.execute('UPDATE verified SET ch=? WHERE version=?',('0'*64,x.version))
    reject(lambda:s.Store(path)); reject(lambda:x.get(x.version))
    out=dict(rows=rows,controls=controls,reopens=reopens,timings=timings,scope='verified precommit portable gate; learned retained-version request frequencies plus pseudocount; bounded offline byte/work surrogate; warm local retrieval timings exclude generation/selection, commit and DB read telemetry; no independent proof or authenticated storage')
    out['evidence_sha256']=a.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--directory',type=Path,required=True); args=p.parse_args(); r=audit(args.directory); (args.directory/'evidence.json').write_bytes(a.canonical(r)); print(json.dumps(dict(controls=r['controls'],reopens=r['reopens'],chosen=[x['chosen'] for x in r['rows']]),indent=2))
