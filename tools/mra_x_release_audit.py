"""Held-out comparative checkpoint audit with abrupt child-process exits."""
import argparse
import copy
import json
import math
import os
import random
import sqlite3
import statistics as st
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path
from unittest.mock import patch
import mra_x_archive as a
import mra_x_dense as dense
import mra_x_kernel as k
import mra_x_release as rel
import mra_x_routed as r
import mra_x_service as s
import mra_x_state as state
import mra_x_separator as sep
import mra_x_topology as ref


def corpus():
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in (16,48):
            d,fs=sep.instance(33100+i*100+n,n,kind); v=next(iter(d)); f=fs[0]; table=dict(f[1]); row=next(iter(table)); table[row]+=7
            edits=[({str(j):x for j,x in enumerate(fs)},{}),({'0':(f[0],table)},{}),({'0':f},{}),({'new':((v,'extra'),{(0,0):0})},{'extra':2}),({}, {'extra':3}),({'new':None},{'extra':None}),({}, {v:d[v]+1}),({}, {v:d[v]}),({'0':(f[0],{})},{}),({'0':f},{}),({'duplicate':f},{}),({'duplicate':None},{})]+[({}, {})]*6
            yield f'{kind}-{n}',d,edits


def run(cls,path,d,edits,check=False):
    store=cls(path,d); rows=[]; recovery=0
    for j,(es,ds) in enumerate(edits):
        x=store.apply(es,ds); q=x['receipt']; e=store.engine
        if check:
            rr=ref.solve(e.d,list(e.inputs.values()),e.order); receipt=k.check(s.certificate(e,rr))
            a.require(all(q[key]==receipt[key] for key in ('problem_sha256','certificate_sha256','optimum','variables','visits')) and store.get(store.version)==receipt)
        rows.append(dict(optimum=q['optimum'],action=x['action'],actual=x['actual'],full=q['visits'],fresh=q.get('fresh',q['visits']),hits=q.get('hits',0)))
        if j==5:
            old=state.snapshot(e,store.version); start=time.perf_counter_ns(); store=cls(path); recovery=time.perf_counter_ns()-start; a.require(state.snapshot(store.engine,store.version)==old)
    start=time.perf_counter_ns(); history=[store.get(v) for v in (3,6,12,18)]; reads=time.perf_counter_ns()-start
    if check:
        versions,docs,demand=store.history(); a.require(versions==list(range(3,19)) and all(k.check(docs[v-3])==h for v,h in zip((3,6,12,18),history)))
        a.require(demand==[3 if v in (3,6,12,18) else 2 for v in range(3,19)])
    with sqlite3.connect(path) as db:
        pages=db.execute('PRAGMA page_count').fetchone()[0]*db.execute('PRAGMA page_size').fetchone()[0]
    return dict(rows=rows,history=history,pages=pages),dict(reopen=recovery,reads=reads)


def child(path,stage):
    class Interrupted(rel.Store):
        def persist(self,db,snap,doc,receipt):
            super().persist(db,snap,doc,receipt)
            if stage=='before_commit': os._exit(71)
    x=Interrupted(path); x.apply({'new':(('a',),{(0,):-7})})
    if stage=='after_commit': os._exit(72)
    raise RuntimeError('bad stage')


def faults(root):
    path=root/'fault.sqlite'; x=rel.Store(path,{'a':2,'b':2}); x.apply({'f':(('a','b'),{(0,0):0,(1,1):2})}); old=state.snapshot(x.engine,x.version); receipts=copy.deepcopy(x._receipts); controls=0; crashes=[]
    def reject(fn,errors=(ValueError,)):
        nonlocal controls
        try: fn()
        except errors: controls+=1
        else: raise ValueError('invalid state accepted')
    def unchanged():
        a.require(state.snapshot(x.engine,x.version)==old and x._receipts==receipts and state.snapshot(rel.Store(path).engine,x.version)==old)
    execute=s.t.execute
    for mode in ('objective','count','factor_id','witness'):
        def faulty(*args):
            e,z=execute(*args)
            if mode=='objective': z['result']['optimum']=99
            if mode=='count': e.counts[0]+=1
            if mode=='factor_id': e.inputs['other']=e.inputs.pop('f')
            if mode=='witness': z['result']['witness']['a']=1
            return e,z
        with patch.object(s.t,'execute',faulty): reject(lambda:x.apply({}))
        unchanged()
    with sqlite3.connect(path) as db: db.execute("CREATE TRIGGER refuse BEFORE INSERT ON dense_versions BEGIN SELECT RAISE(ABORT,'injected'); END")
    reject(lambda:x.apply({}),(sqlite3.IntegrityError,)); unchanged()
    with sqlite3.connect(path) as db: db.execute('DROP TRIGGER refuse')
    for stage,code in [('before_commit',71),('after_commit',72)]:
        proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child',str(path),stage],timeout=20,capture_output=True)
        a.require(proc.returncode==code); y=rel.Store(path); q=y.get(y.version)
        a.require(y.version==old['version']+(stage=='after_commit') and q['optimum']==(-7 if stage=='after_commit' else 0))
        with sqlite3.connect(path) as db: a.require(db.execute('PRAGMA integrity_check').fetchone()[0]=='ok')
        crashes.append(dict(stage=stage,exit_code=code,version=y.version,optimum=q['optimum'])); controls+=1
    reject(lambda:x.apply({})); a.require(x._receipts==receipts and x.version==old['version'])
    reject(lambda:rel.Store(root/'missing.sqlite')); a.require(not (root/'missing.sqlite').exists())
    other=root/'other.sqlite'; r.Store(other,{'a':2}); reject(lambda:rel.Store(other,{'a':2}))
    y=rel.Store(path); reject(lambda:y.apply({}, {'a':0})); reject(lambda:y.get(999))
    with sqlite3.connect(path) as db: row=db.execute('SELECT * FROM dense_versions ORDER BY version DESC LIMIT 1').fetchone()
    v,h,blob,reads=row; m=dense.unpack(blob,h)
    for mode in ('objective','count','version','truncated','trailing','hash','oversize'):
        bad=copy.deepcopy(m); bh=h; bb=blob
        if mode=='objective': bad['result']['optimum']=99
        if mode=='count': bad['snapshot']['counts'][0]+=1
        if mode=='version': bad['snapshot']['version']+=1
        if mode in ('objective','count','version'):
            raw=a.canonical(bad); bh=r.sha(raw); bb=dense.compress(raw)
        if mode=='truncated': bb=blob[:-1]
        if mode=='trailing': bb=blob+b'x'
        if mode=='hash': bh='0'*64
        if mode=='oversize': bb=dense.zlib.compress(b'x'*(k.MAX_BYTES+1))
        with sqlite3.connect(path) as db: db.execute('UPDATE dense_versions SET hash=?,manifest=? WHERE version=?',(bh,bb,v))
        reject(lambda:rel.Store(path))
    with sqlite3.connect(path) as db: db.execute('UPDATE dense_versions SET hash=?,manifest=? WHERE version=?',(h,blob,v))
    a.require(rel.Store(path).get(v)['optimum']==-7)
    return controls,crashes


def audit(root):
    root=root.resolve(); root.mkdir(); rows=[]; timings=[]; methods={'full':s.Store,'routed':r.Store,'candidate':rel.Store}
    for i,(name,d,edits) in enumerate(corpus()):
        results={label:run(cls,root/f'{name}-{label}.sqlite',d,edits,True)[0] for label,cls in methods.items()}
        for label in methods:
            for x,y in zip(results['routed']['rows'],results[label]['rows']): a.require(all(x[key]==y[key] for key in ('optimum','action','actual','full')))
            a.require(results['routed']['history']==results[label]['history'])
        a.require(results['routed']['rows']==results['candidate']['rows'])
        rows.append(dict(name=name,**results)); elapsed={key:[] for key in methods}; profile={key:[] for key in methods}; memory={}
        for rep in range(3):
            labels=list(methods); random.Random(i*19+rep).shuffle(labels)
            for label in labels:
                path=root/f'timing-{i}-{rep}-{label}.sqlite'; start=time.perf_counter_ns(); _,p=run(methods[label],path,d,edits); elapsed[label].append(time.perf_counter_ns()-start); profile[label].append(p); path.unlink()
        for label in (methods if i==0 else ()):
            path=root/f'memory-{i}-{label}.sqlite'; tracemalloc.start(); run(methods[label],path,d,edits); memory[label]=tracemalloc.get_traced_memory()[1]; tracemalloc.stop(); path.unlink()
        timings.append(dict(name=name,ns=elapsed,profile=profile,peak_traced_bytes=memory))
    ratios={label:[st.median(x['ns']['candidate'])/st.median(x['ns'][label]) for x in timings] for label in ('full','routed')}; geo={label:math.exp(st.mean(map(math.log,v))) for label,v in ratios.items()}; worst={label:max(v) for label,v in ratios.items()}
    controls,crashes=faults(root); physical=sum(x['candidate']['pages'] for x in rows)/sum(x['routed']['pages'] for x in rows)
    out=dict(rows=rows,controls=controls,crashes=crashes,timings=timings,geomean=geo,worst=worst,physical_ratio=physical,decision=rel.decide(geo,worst,physical,controls==19),scope='new synthetic seeds, three matched stores; timing includes creation, 18 edits, reopening, four historical reads and page accounting; memory separate traced Python allocation for first stream only, not RSS; abrupt child exit not power-loss; no production promotion')
    out['evidence_sha256']=a.digest(out); return out


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--child': child(Path(sys.argv[2]),sys.argv[3])
    p=argparse.ArgumentParser(); p.add_argument('--directory',type=Path,required=True); args=p.parse_args(); out=audit(args.directory); (args.directory/'evidence.json').write_bytes(a.canonical(out)); print(json.dumps({key:out[key] for key in ('controls','crashes','geomean','worst','physical_ratio','decision')},indent=2))
