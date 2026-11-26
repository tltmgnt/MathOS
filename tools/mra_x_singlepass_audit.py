"""Matched serialization, allocation and recovery audit with fresh seeds."""
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
import mra_x_release as rel
import mra_x_release_audit as old
import mra_x_routed as r
import mra_x_service as s
import mra_x_singlepass as sp
import mra_x_state as state
import mra_x_separator as sep


def corpus():
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in (12,40):
            d,fs=sep.instance(34100+i*100+n,n,kind); v=next(iter(d)); f=fs[0]; tab=dict(f[1]); row=next(iter(tab)); tab[row]+=5
            edits=[({str(j):x for j,x in enumerate(fs)},{}),({'0':(f[0],tab)},{}),({'0':f},{}),({'new':((v,'extra'),{(0,0):0})},{'extra':2}),({}, {'extra':3}),({'new':None},{'extra':None}),({}, {v:d[v]+1}),({}, {v:d[v]}),({'0':(f[0],{})},{}),({'0':f},{}),({'duplicate':f},{}),({'duplicate':None},{})]+[({}, {})]*6
            yield f'{kind}-{n}',d,edits


def child(path,stage):
    class Interrupted(sp.Store):
        def persist(self,db,snap,doc,receipt):
            super().persist(db,snap,doc,receipt)
            if stage=='before': os._exit(71)
    x=Interrupted(path); x.apply({'new':(('a',),{(0,):-7})})
    if stage=='after': os._exit(72)
    raise RuntimeError('bad stage')


def faults(root):
    path=root/'fault.sqlite'; x=sp.Store(path,{'a':2,'b':2}); x.apply({'f':(('a','b'),{(0,0):0,(1,1):2})}); before=state.snapshot(x.engine,x.version); receipts=copy.deepcopy(x._receipts); controls=0; crashes=[]
    def reject(fn,errors=(ValueError,)):
        nonlocal controls
        try: fn()
        except errors: controls+=1
        else: raise ValueError('bad result accepted')
    def unchanged():
        a.require(state.snapshot(x.engine,x.version)==before and x._receipts==receipts and state.snapshot(sp.Store(path).engine,x.version)==before)
    execute=s.t.execute
    for mode in ('objective','witness','trace_bool','count','factor_id','input_bool','message'):
        def faulty(*args):
            e,z=execute(*args); q=z['result']
            if mode=='objective': q['optimum']=99
            if mode=='witness': q['witness']['a']=1
            if mode=='trace_bool': q['trace'][0][2][0][1]=False
            if mode=='count': e.counts[0]+=1
            if mode=='factor_id': e.inputs['other']=e.inputs.pop('f')
            if mode=='input_bool': e.inputs['f'][1][(0,0)]=False
            if mode=='message': e.outputs[0][1][(0,)]=99
            return e,z
        with patch.object(s.t,'execute',faulty): reject(lambda:x.apply({}))
        unchanged()
    with sqlite3.connect(path) as db: db.execute("CREATE TRIGGER refuse BEFORE INSERT ON dense_versions BEGIN SELECT RAISE(ABORT,'injected'); END")
    reject(lambda:x.apply({}),(sqlite3.IntegrityError,)); unchanged()
    with sqlite3.connect(path) as db: db.execute('DROP TRIGGER refuse')
    # Identical on-disk schema: old reader opens new writer and vice versa.
    legacy=rel.Store(path); a.require(legacy.get(1)==x.get(1)); legacy.apply({}); x=sp.Store(path); a.require(x.version==2 and x.seed['hits']==0); controls+=1
    snap=state.snapshot(x.engine,x.version); doc=s.certificate(x.engine,x.engine.update({})['result']); reject(lambda:r.verify(snap,doc,{},shared=True))
    for stage,code in [('before',71),('after',72)]:
        p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child',str(path),stage],capture_output=True,timeout=20)
        a.require(p.returncode==code); y=sp.Store(path); q=y.get(y.version); a.require(y.version==2+(stage=='after') and q['optimum']==(-7 if stage=='after' else 0))
        with sqlite3.connect(path) as db: a.require(db.execute('PRAGMA integrity_check').fetchone()[0]=='ok')
        crashes.append(dict(stage=stage,version=y.version,optimum=q['optimum'])); controls+=1
    reject(lambda:x.apply({})); a.require(x.version==2)
    with sqlite3.connect(path) as db: v,h,blob,reads=db.execute('SELECT * FROM dense_versions ORDER BY version DESC LIMIT 1').fetchone()
    m=dense.unpack(blob,h)
    for mode in ('objective','count','truncated','trailing','digest'):
        bad=copy.deepcopy(m); bh=h; bb=blob
        if mode=='objective': bad['result']['optimum']=99
        if mode=='count': bad['snapshot']['counts'][0]+=1
        if mode in ('objective','count'):
            raw=a.canonical(bad); bh=r.sha(raw); bb=dense.compress(raw)
        if mode=='truncated': bb=blob[:-1]
        if mode=='trailing': bb=blob+b'x'
        if mode=='digest': bh='0'*64
        with sqlite3.connect(path) as db: db.execute('UPDATE dense_versions SET hash=?,manifest=? WHERE version=?',(bh,bb,v))
        reject(lambda:sp.Store(path))
    return controls,crashes


def audit(root):
    root=root.resolve(); root.mkdir(); rows=[]; timings=[]; methods={'full':s.Store,'routed':r.Store,'release':rel.Store,'singlepass':sp.Store}
    for i,(name,d,edits) in enumerate(corpus()):
        results={key:old.run(cls,root/f'{name}-{key}.sqlite',d,edits,True)[0] for key,cls in methods.items()}
        for key in methods:
            a.require(results[key]['history']==results['full']['history'])
            for x,y in zip(results[key]['rows'],results['full']['rows']): a.require(all(x[k]==y[k] for k in ('optimum','action','actual','full')))
        a.require(results['singlepass']['rows']==results['release']['rows']==results['routed']['rows']); rows.append(dict(name=name,**results))
        ns={key:[] for key in methods}; memory={}
        for rep in range(3):
            labels=list(methods); random.Random(i*19+rep).shuffle(labels)
            for key in labels:
                path=root/f'timing-{i}-{rep}-{key}.sqlite'; start=time.perf_counter_ns(); old.run(methods[key],path,d,edits); ns[key].append(time.perf_counter_ns()-start); path.unlink()
        if i in (0,1):
            for key in methods:
                path=root/f'memory-{i}-{key}.sqlite'; tracemalloc.start(); old.run(methods[key],path,d,edits); memory[key]=tracemalloc.get_traced_memory()[1]; tracemalloc.stop(); path.unlink()
        timings.append(dict(name=name,ns=ns,peak_traced_bytes=memory))
    controls,crashes=faults(root); ratios={key:[st.median(x['ns']['singlepass'])/st.median(x['ns'][key]) for x in timings] for key in ('full','routed','release')}
    geo={key:math.exp(st.mean(map(math.log,v))) for key,v in ratios.items()}; worst={key:max(v) for key,v in ratios.items()}; physical=sum(x['singlepass']['pages'] for x in rows)/sum(x['routed']['pages'] for x in rows)
    out=dict(rows=rows,controls=controls,crashes=crashes,timings=timings,geomean=geo,worst=worst,physical_ratio=physical,decision=rel.decide(geo,worst,physical,controls==18),scope='new synthetic seeds; four matched SQLite stores; 18 edits, reopen, four reads and page accounting; memory traced separately on first two streams, not RSS; no production promotion or formal proof')
    out['evidence_sha256']=a.digest(out); return out


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--child': child(Path(sys.argv[2]),sys.argv[3])
    p=argparse.ArgumentParser(); p.add_argument('--directory',type=Path,required=True); args=p.parse_args(); out=audit(args.directory); (args.directory/'evidence.json').write_bytes(a.canonical(out)); print(json.dumps({key:out[key] for key in ('controls','crashes','geomean','worst','physical_ratio','decision')},indent=2))
