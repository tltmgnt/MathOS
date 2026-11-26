"""Matched end-to-end and stage-level comparison of private speculative forks."""
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
import mra_x_fork as f
import mra_x_indexed as idx
import mra_x_kernel as k
import mra_x_service as s
import mra_x_singlepass as sp
import mra_x_state as state
import mra_x_separator as sep
import mra_x_topology as ref


def corpus():
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in (16,64):
            d,fs=sep.instance(36100+i*100+n,n,kind); v=next(iter(d)); edits=[({str(j):x for j,x in enumerate(fs)}, {})]
            for j in (0,len(fs)//2,len(fs)-1):
                scope,table=fs[j]; tab=dict(table); row=next(iter(tab)); tab[row]+=5
                edits.extend([({str(j):(scope,tab)},{}),({str(j):fs[j]},{}),({}, {})])
            edits.extend([({'0':(fs[0][0],{})},{}),({'0':fs[0]},{}),({}, {v:d[v]+1}),({}, {v:d[v]}),({}, {}),({}, {})])
            yield f'{kind}-{n}',d,edits


def run(cls,path,d,edits,check=False):
    store=cls(path,d); rows=[]; profile={}
    for j,(es,ds) in enumerate(edits):
        old=store.engine; before=a.canonical(state.snapshot(old,store.version)) if check else None
        x=store.apply(es,ds); q=x['receipt']; e=store.engine
        if check:
            a.require(a.canonical(state.snapshot(old,x['version']-1))==before)
            rr=ref.solve(e.d,list(e.inputs.values()),e.order); receipt=k.check(s.certificate(e,rr))
            a.require(all(q[key]==receipt[key] for key in ('problem_sha256','certificate_sha256','optimum','variables','visits')) and store.get(store.version)==receipt)
        rows.append(dict(optimum=q['optimum'],action=x['action'],actual=x['actual'],full=q['visits'],fresh=q['fresh'],hits=q['hits'],forked=x.get('profile',{}).get('forked',False)))
        for key,val in x.get('profile',{}).items():
            if key!='forked': profile[key]=profile.get(key,0)+val
        if j==7:
            before=state.snapshot(e,store.version); store=cls(path); a.require(state.snapshot(store.engine,store.version)==before)
    reads=[store.get(v) for v in (1,8,16)]
    if check:
        versions,docs,demand=store.history(); a.require(versions==list(range(1,17)) and [k.check(docs[v-1]) for v in (1,8,16)]==reads)
    with sqlite3.connect(path) as db: pages=db.execute('PRAGMA page_count').fetchone()[0]*db.execute('PRAGMA page_size').fetchone()[0]
    return dict(rows=rows,reads=reads,pages=pages),profile


def controls(root):
    total=0; d={'a':2,'b':2}; e=idx.Indexed(d,['a','b']); e.update({'f':(('a','b'),{(0,0):0,(0,1):0})}); before=a.canonical(state.snapshot(e,0))
    p=s.t.prepare(e,{},{}); new,z,_=f.execute(e,{},p,'indexed'); a.require(new is not e and new.buckets[0] is e.buckets[0] and new.outputs[0] is e.outputs[0]); total+=1
    z['result']['trace'][0][2].clear(); a.require(a.canonical(state.snapshot(e,0))==before); total+=1
    edit={'f':(('a','b'),{(1,0):0,(1,1):0})}; p=s.t.prepare(e,edit,{}); new,z,_=f.execute(e,edit,p,'indexed'); a.require(z['result']['witness']['a']==1 and z['changed_messages']==0 and new.records[0] is not e.records[0] and a.canonical(state.snapshot(e,0))==before); total+=1
    def reject(fn,errors=(ValueError,)):
        nonlocal total
        try: fn()
        except errors: total+=1
        else: raise ValueError('invalid transaction accepted')
    e2=idx.Indexed({'a':2,'b':2,'c':2},['a','b','c'],budget=8); e2.update({}); old=a.canonical(state.snapshot(e2,0)); edit={'f':(('a','b','c'),{(0,0,0):0})}; p=s.t.prepare(e2,edit,{})
    reject(lambda:f.execute(e2,edit,p,'indexed')); a.require(a.canonical(state.snapshot(e2,0))==old)
    path=root/'fault.sqlite'; x=f.Store(path,d); x.apply({'f':(('a','b'),{(0,0):0,(0,1):0})}); before=a.canonical(state.snapshot(x.engine,x.version)); receipts=copy.deepcopy(x._receipts); old=x.engine
    def unchanged(): a.require(x.engine is old and a.canonical(state.snapshot(x.engine,x.version))==before and x._receipts==receipts and a.canonical(state.snapshot(f.Store(path).engine,x.version))==before)
    original=f.execute
    for mode in ('objective','trace','input'):
        def faulty(*args,**kwargs):
            candidate,z,p=original(*args,**kwargs)
            if mode=='objective': z['result']['optimum']=99
            if mode=='trace': z['result']['trace'][0][2][0][1]=False
            if mode=='input': candidate.inputs['wrong']=candidate.inputs.pop('f')
            return candidate,z,p
        with patch.object(f,'execute',faulty): reject(lambda:x.apply({}))
        unchanged()
    with sqlite3.connect(path) as db: db.execute("CREATE TRIGGER refuse BEFORE INSERT ON dense_versions BEGIN SELECT RAISE(ABORT,'injected'); END")
    reject(lambda:x.apply({'f':(('b',),{(1,):4})}),(sqlite3.IntegrityError,)); unchanged()
    with sqlite3.connect(path) as db: db.execute('DROP TRIGGER refuse')
    stale=f.Store(path); x.apply({}); reject(lambda:stale.apply({})); a.require(stale._receipts==receipts)
    supplied={(0,):4}; x.apply({'extra':(('a',),supplied)}); supplied[(0,)]=99; a.require(x.get(x.version)['optimum']==4); total+=1
    x.apply({}, {'b':3}); a.require(x.engine.d['b']==3 and f.Store(path).get(x.version)==x.get(x.version)); total+=1
    return total


def audit(root):
    root=root.resolve(); root.mkdir(); rows=[]; timings=[]; methods={'singlepass':sp.Store,'deep':f.Deep,'fork':f.Store}
    for i,(name,d,edits) in enumerate(corpus()):
        results={label:run(cls,root/f'{name}-{label}.sqlite',d,edits,True)[0] for label,cls in methods.items()}
        for label in methods:
            a.require(results[label]['reads']==results['deep']['reads'] and results[label]['pages']==results['deep']['pages'])
            for x,y in zip(results[label]['rows'],results['deep']['rows']): a.require(all(x[key]==y[key] for key in ('optimum','action','actual','full','fresh','hits')))
        rows.append(dict(name=name,**results)); ns={key:[] for key in methods}; profiles={key:[] for key in methods}
        for rep in range(3):
            labels=list(methods); random.Random(i*17+rep).shuffle(labels)
            for label in labels:
                path=root/f'timing-{i}-{rep}-{label}.sqlite'; start=time.perf_counter_ns(); _,p=run(methods[label],path,d,edits); ns[label].append(time.perf_counter_ns()-start); profiles[label].append(p); path.unlink()
        timings.append(dict(name=name,ns=ns,profiles=profiles))
    ratios={label:[st.median(x['ns']['fork'])/st.median(x['ns'][label]) for x in timings] for label in ('deep','singlepass')}; geo={key:math.exp(st.mean(map(math.log,v))) for key,v in ratios.items()}; worst={key:max(v) for key,v in ratios.items()}
    out=dict(rows=rows,controls=controls(root),timings=timings,geomean=geo,worst=worst,decision='REVIEW_CANDIDATE' if max(geo.values())<=.9 and max(worst.values())<=1.2 else 'NO_PROMOTION',scope='private trusted shallow fork for ordinary edits; existing copy-on-write update and full independent gate; migrations unchanged; timing includes create, 16 commits, reopen and three reads; no immutable API, hostile code isolation, RSS, power-loss or program proof')
    out['evidence_sha256']=a.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--directory',type=Path,required=True); args=p.parse_args(); r=audit(args.directory); (args.directory/'evidence.json').write_bytes(a.canonical(r)); print(json.dumps({key:r[key] for key in ('controls','geomean','worst','decision')},indent=2))
