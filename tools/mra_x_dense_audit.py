"""Matched transactional object storage, recovery and corruption audit."""
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
import mra_x_cas as c
import mra_x_dense as dense
import mra_x_routed as r
import mra_x_service as s
import mra_x_state as state
import mra_x_kernel as k
import mra_x_topology as ref
import mra_x_separator as sep


def corpus():
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in (8,64):
            d,fs=sep.instance(32100+i*100+n,n,kind); v=next(iter(d)); f=fs[0]
            edits=[({str(j):x for j,x in enumerate(fs)},{}),({},{}),({'new':((v,'extra'),{(0,0):0})},{'extra':2}),({}, {'extra':3}),({'new':None},{'extra':None}),({}, {v:d[v]+1}),({}, {v:d[v]}),({'0':(f[0],{})},{}),({'0':f},{}),({},{}),({'duplicate':f},{}),({'duplicate':None},{})]
            yield f'{kind}-{n}',d,edits+[({}, {})]*6


def run(cls,path,d,edits,check=False):
    store=cls(path,d); rows=[]; reopen=0
    for j,(es,ds) in enumerate(edits):
        x=store.apply(es,ds); q=x['receipt']; e=store.engine
        if check:
            rr=ref.solve(e.d,list(e.inputs.values()),e.order); receipt=k.check(s.certificate(e,rr))
            a.require(all(q[key]==receipt[key] for key in ('problem_sha256','certificate_sha256','optimum','variables','visits')) and store.get(store.version)==receipt)
        rows.append(dict(optimum=q['optimum'],action=x['action'],actual=x['actual'],full=q['visits'],fresh=q['fresh'],hits=q['hits'],new_objects=q.get('new_objects',0),reused_objects=q.get('reused_objects',0),new_bytes=q.get('new_bytes',0),manifest_bytes=q.get('manifest_bytes',0)))
        if j==5:
            old=state.snapshot(e,store.version); start=time.perf_counter_ns(); store=cls(path); reopen=time.perf_counter_ns()-start; a.require(state.snapshot(store.engine,store.version)==old and store.seed['hits']==0)
    start=time.perf_counter_ns(); history=[store.get(v) for v in (3,6,12,18)]; reads=time.perf_counter_ns()-start
    if check:
        versions,docs,demand=store.history(); a.require(versions==list(range(3,19)) and all(k.check(docs[v-3])==h for v,h in zip((3,6,12,18),history)))
        a.require(demand==[3 if v in (3,6,12,18) else 2 for v in range(3,19)])
    with sqlite3.connect(path) as db:
        if cls is c.Store:
            payload=db.execute('SELECT coalesce(sum(length(payload)),0) FROM cas_objects').fetchone()[0]; manifest=db.execute('SELECT sum(length(manifest)) FROM cas_versions').fetchone()[0]; refs=db.execute('SELECT count(*) FROM cas_refs').fetchone()[0]; objects=db.execute('SELECT count(*) FROM cas_objects').fetchone()[0]
        elif cls in (dense.Store,dense.Compressed):
            manifest=db.execute('SELECT sum(length(manifest)) FROM dense_versions').fetchone()[0]; refs=objects=payload=0
            if cls is dense.Store:
                payload,objects=db.execute('SELECT coalesce(sum(length(payload)),0),count(*) FROM dense_objects').fetchone()
        else:
            payload=db.execute('SELECT sum(length(snapshot)+length(certificate)) FROM verified').fetchone()[0]; manifest=refs=objects=0
        physical=db.execute('PRAGMA page_count').fetchone()[0]*db.execute('PRAGMA page_size').fetchone()[0]
    return dict(rows=rows,history=history,payload=payload,manifest=manifest,refs=refs,objects=objects,physical=physical),dict(reopen=reopen,reads=reads)


def controls(root):
    total=0; path=root/'control.sqlite'; x=dense.Store(path,{'a':2,'b':2},budget=16)
    x.apply({'f':(('a','b'),{(0,0):0,(0,1):0})}); old=state.snapshot(x.engine,x.version); receipts=copy.deepcopy(x._receipts)
    def reject(fn,errors=(ValueError,)):
        nonlocal total
        try: fn()
        except errors: total+=1
        else: raise ValueError('bad state accepted')
    def unchanged():
        a.require(state.snapshot(x.engine,x.version)==old and x._receipts==receipts and state.snapshot(dense.Store(path).engine,x.version)==old)
    execute=s.t.execute
    for mode in ('objective','count','factor_id'):
        def faulty(*args):
            e,z=execute(*args)
            if mode=='objective': z['result']['optimum']=99
            if mode=='count': e.counts[0]+=1
            if mode=='factor_id': e.inputs['other']=e.inputs.pop('f')
            return e,z
        with patch.object(s.t,'execute',faulty): reject(lambda:x.apply({}))
        unchanged()
    def tables():
        with sqlite3.connect(path) as db: return [db.execute('SELECT * FROM '+t+' ORDER BY 1').fetchall() for t in ('dense_objects','dense_versions')]
    with sqlite3.connect(path) as db: db.execute("CREATE TRIGGER refuse BEFORE INSERT ON dense_versions BEGIN SELECT RAISE(ABORT,'injected'); END")
    before=tables(); reject(lambda:x.apply({'new':(('a',),{(0,):9})}),(sqlite3.IntegrityError,)); a.require(tables()==before); unchanged()
    with sqlite3.connect(path) as db: db.execute('DROP TRIGGER refuse')
    stale=dense.Store(path); q=x.apply({})['receipt']; a.require(q['new_objects']==q['fresh']==0 and q['reused_objects']>0); total+=1
    reject(lambda:stale.apply({})); a.require(stale._receipts==receipts and stale.version==old['version'])
    reject(lambda:x.apply({}, {'a':0}))
    x.apply({'duplicate':x.engine.inputs['f']}); a.require(len(x.history()[1][-1]['problem']['factors'])==2); total+=1
    x.apply({'duplicate':None,'temporary':(('a',),{(0,):12345})}); temp=bytes.fromhex(r.sha(a.canonical(state.pack(x.engine.inputs['temporary'])))); x.apply({'temporary':None})
    for _ in range(17): x.apply({})
    versions,_,_=x.history(); a.require(len(versions)==16 and versions[-1]==x.version)
    with sqlite3.connect(path) as db:
        a.require(db.execute('SELECT count(*) FROM dense_objects WHERE hash=?',(temp,)).fetchone()[0]==0); total+=1
    reject(lambda:x.get(0))
    with sqlite3.connect(path) as db:
        i,h,payload=db.execute('SELECT * FROM dense_objects LIMIT 1').fetchone(); db.execute('UPDATE dense_objects SET payload=? WHERE id=?',(b'[]',i))
    reject(lambda:dense.Store(path))
    with sqlite3.connect(path) as db:
        db.execute('UPDATE dense_objects SET payload=? WHERE id=?',(payload,i)); row=db.execute('SELECT * FROM dense_versions ORDER BY version DESC LIMIT 1').fetchone(); v,h,blob,reads=row; m=dense.manifest(row)
    for mode in ('objective','missing','bool'):
        bad=copy.deepcopy(m)
        if mode=='objective': bad['result']['optimum']=99
        if mode=='missing': bad['proofs'][0]=999999
        if mode=='bool': bad['proofs'][0]=True
        raw=a.canonical(bad)
        with sqlite3.connect(path) as db: db.execute('UPDATE dense_versions SET hash=?,manifest=? WHERE version=?',(r.sha(raw),dense.compress(raw),v))
        reject(lambda:dense.Store(path))
    reject(lambda:dense.unpack(blob+b'extra',h)); reject(lambda:dense.unpack(blob[:-1],h)); reject(lambda:dense.unpack(dense.zlib.compress(b'x'*(k.MAX_BYTES+1)),h))
    return total


def audit(root):
    root=root.resolve(); root.mkdir(); rows=[]; timings=[]; methods={'routed':r.Store,'cas':c.Store,'dense':dense.Store,'compressed':dense.Compressed}
    for i,(name,d,edits) in enumerate(corpus()):
        results={label:run(cls,root/f'{name}-{label}.sqlite',d,edits,True)[0] for label,cls in methods.items()}
        for label in methods:
            for x,y in zip(results['routed']['rows'],results[label]['rows']): a.require(all(x[key]==y[key] for key in ('optimum','action','actual','full','fresh','hits')))
            a.require(results['routed']['history']==results[label]['history'])
        rows.append(dict(name=name,**results))
        elapsed={key:[] for key in methods}; profile={key:[] for key in methods}
        for rep in range(3):
            labels=list(methods); random.Random(i*19+rep).shuffle(labels)
            for label in labels:
                path=root/f'timing-{i}-{rep}-{label}.sqlite'; start=time.perf_counter_ns(); _,p=run(methods[label],path,d,edits); elapsed[label].append(time.perf_counter_ns()-start); profile[label].append(p); path.unlink()
        timings.append(dict(name=name,ns=elapsed,profile=profile))
    ratios={label:[st.median(x['ns']['dense'])/st.median(x['ns'][label]) for x in timings] for label in ('routed','cas','compressed')}
    geo={label:math.exp(st.mean(map(math.log,v))) for label,v in ratios.items()}; worst={label:max(v) for label,v in ratios.items()}
    out=dict(rows=rows,controls=controls(root),timings=timings,geomean=geo,worst=worst,decision='REVIEW_CANDIDATE' if max(geo.values())<=.9 and max(worst.values())<=1.2 and all(sum(x['dense']['physical'] for x in rows)<=sum(x[label]['physical'] for x in rows) for label in ('routed','cas','compressed')) else 'NO_PROMOTION',scope='new synthetic streams; four matched SQLite stores; timing includes create, 18 edits crossing retention, reopen, four verified historical reads and storage accounting; audit reads excluded; logical and allocated page bytes; no RSS, cold-cache, authentication or program proof')
    out['evidence_sha256']=a.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--directory',type=Path,required=True); args=p.parse_args(); r=audit(args.directory); (args.directory/'evidence.json').write_bytes(a.canonical(r)); print(json.dumps({key:r[key] for key in ('controls','geomean','worst','decision')},indent=2))
