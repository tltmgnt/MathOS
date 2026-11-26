"""Matched durable transaction audit, including initialization and reopen timings."""
import argparse
import copy
import json
import random
import sqlite3
import statistics as st
import time
from pathlib import Path
from unittest.mock import patch
import mra_x_precommit as p
import mra_x_service as s
import mra_x_archive as a
import mra_x_kernel as k
import mra_x_state as state
import mra_x_separator as sep
import mra_x_topology as ref


def corpus():
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in (8,32,64):
            d,fs=sep.instance(29100+i*100+n,n,kind); v=next(iter(d)); f=fs[0]
            edits=[({str(j):x for j,x in enumerate(fs)},{}),({},{}),({'new':((v,'extra'),{(0,0):0})},{'extra':2}),({}, {'extra':3}),({'new':None},{'extra':None}),({}, {v:d[v]+1}),({}, {v:d[v]}),({'0':(f[0],{})},{}),({'0':f},{}),({},{}),({'duplicate':f},{}),({'duplicate':None},{})]
            yield f'{kind}-{n}',d,edits


def run(cls,path,d,edits,check=False):
    store=cls(path,d); rows=[]
    for j,(es,ds) in enumerate(edits):
        x=store.apply(es,ds); r=x['receipt']; e=store.engine
        if check:
            q=ref.solve(e.d,list(e.inputs.values()),e.order); a.require(q['optimum']==r['optimum'])
            doc=s.certificate(e,q); receipt=k.check(doc)
            a.require(all(r[key]==receipt[key] for key in ('problem_sha256','certificate_sha256','optimum','variables','visits')))
            a.require(store.get(store.version)==receipt)
        rows.append(dict(version=x['version'],action=x['action'],actual=x['actual'],optimum=r['optimum'],full=r['visits'],fresh=r.get('fresh',r['visits']),hits=r.get('hits',0),lookups=r['lookups']))
        if j==5:
            old=state.snapshot(e,store.version); store=cls(path); a.require(state.snapshot(store.engine,store.version)==old)
    return rows


def audit(root):
    root=root.resolve(); root.mkdir(); rows=[]; times=[]; controls=0
    for i,(name,d,edits) in enumerate(corpus()):
        base=run(s.Store,root/f'{name}-base.sqlite',d,edits,True)
        inc=run(p.Store,root/f'{name}-inc.sqlite',d,edits,True)
        for x,y in zip(base,inc):
            a.require(all(x[key]==y[key] for key in ('version','action','actual','optimum','full')) and y['fresh']<=x['full'])
        rows.append(dict(name=name,baseline=base,incremental=inc))
        elapsed={'baseline':[],'incremental':[]}
        for rep in range(3):
            labels=list(elapsed); random.Random(i*19+rep).shuffle(labels)
            for label in labels:
                path=root/f'timing-{i}-{rep}-{label}.sqlite'; start=time.perf_counter_ns()
                run(s.Store if label=='baseline' else p.Store,path,d,edits)
                elapsed[label].append(time.perf_counter_ns()-start); path.unlink()
        times.append(dict(name=name,ns=elapsed))
    path=root/'control.sqlite'; x=p.Store(path,{'a':2,'b':2},budget=16)
    x.apply({'f':(('a','b'),{(0,0):0,(0,1):0})}); r=x.apply({'f':(('a','b'),{(1,0):0,(1,1):0})})
    a.require(r['receipt']['hits']==1 and x.get(x.version)['optimum']==0); controls+=1
    old=state.snapshot(x.engine,x.version); receipts=copy.deepcopy(x._receipts)
    def unchanged():
        a.require(state.snapshot(x.engine,x.version)==old and x._receipts==receipts and state.snapshot(p.Store(path).engine,x.version)==old)
    def reject(fn,errors=(ValueError,)):
        nonlocal controls
        try: fn()
        except errors: controls+=1
        else: raise ValueError('invalid transaction accepted')
    execute=s.t.execute
    for mode in ('optimum','witness','trace','message','input'):
        def faulty(*args):
            e,r=execute(*args); q=r['result']
            if mode=='optimum': q['optimum']=99
            if mode=='witness': q['witness']['a']=0
            if mode=='trace': q['trace'][0][2][0][1]=0; e.records=copy.deepcopy(q['trace'])
            if mode=='message': e.outputs[0][1][(0,)]=99
            if mode=='input': e.inputs['f']=(('a','b'),{(0,0):0})
            return e,r
        with patch.object(s.t,'execute',faulty): reject(lambda:x.apply({}))
        unchanged()
    reject(lambda:x.apply({}, {'a':1})); unchanged()
    with sqlite3.connect(path) as db: db.execute("CREATE TRIGGER refuse BEFORE INSERT ON verified BEGIN SELECT RAISE(ABORT,'injected'); END")
    reject(lambda:x.apply({}), (sqlite3.IntegrityError,)); unchanged()
    with sqlite3.connect(path) as db: db.execute('DROP TRIGGER refuse')
    stale=p.Store(path); r=x.apply({}); a.require(r['receipt']['fresh']==0); controls+=1
    reject(lambda:stale.apply({})); a.require(stale._receipts==receipts and stale.version==old['version'])
    reopened=p.Store(path); a.require(reopened.seed['fresh']==reopened.seed['visits'] and reopened.seed['hits']==0); controls+=1
    for _ in range(17): reopened.apply({})
    versions,docs,demand=reopened.history(); a.require(len(versions)==16 and versions[-1]==reopened.version); controls+=1
    reject(lambda:reopened.get(0))
    with sqlite3.connect(path) as db: db.execute('UPDATE verified SET ch=? WHERE version=?',('0'*64,reopened.version))
    reject(lambda:p.Store(path))
    out=dict(rows=rows,controls=controls,timings=times,scope='matched local SQLite transactions; timing includes create, 12 commits and one reopen; excludes audit reads and reference verification; receipt seed work is additional at creation/reopen and excluded from edit visit totals; trusted in-process receipts; no formal proof or physical RE-X integration')
    out['evidence_sha256']=a.digest(out); return out


if __name__=='__main__':
    arg=argparse.ArgumentParser(); arg.add_argument('--directory',type=Path,required=True); args=arg.parse_args(); r=audit(args.directory); (args.directory/'evidence.json').write_bytes(a.canonical(r))
    for key in ('baseline','incremental'):
        print(key,{field:sum(x[field] for row in r['rows'] for x in row[key]) for field in ('actual','full','fresh','hits','lookups')})
    print('controls',r['controls'])
