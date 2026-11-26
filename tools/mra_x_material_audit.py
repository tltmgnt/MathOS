"""Matched identity-bound materialization and release audit."""
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
import mra_x_owned as o
import mra_x_share as sh
import mra_x_material as m
import mra_x_routed as r
import mra_x_indexed as idx
import mra_x_kernel as k
import mra_x_service as s
import mra_x_singlepass as sp
import mra_x_state as state
import mra_x_separator as sep
import mra_x_topology as ref


def corpus():
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in (20,64):
            d,fs=sep.instance(39100+i*100+n,n,kind); v=next(iter(d)); edits=[({str(j):x for j,x in enumerate(fs)}, {})]
            for j in (0,len(fs)//2,len(fs)-1):
                scope,table=fs[j]; tab=dict(table); row=next(iter(tab)); tab[row]+=11
                edits.extend([({str(j):(scope,tab)},{}),({str(j):fs[j]},{}),({}, {})])
            edits.extend([({'0':(fs[0][0],{})},{}),({'0':fs[0]},{}),({}, {v:d[v]+1}),({}, {v:d[v]}),({}, {}),({}, {})])
            yield f'{kind}-{n}',d,edits


def run(cls,path,d,edits,check=False):
    store=cls(path,d); rows=[]; profile={}; sharing={}; material={}
    for j,(es,ds) in enumerate(edits):
        old=store.engine if check else None; before=a.canonical(state.snapshot(old,store.version)) if check else None
        prior=store._owned if check and isinstance(store,sh.Store) else None
        x=store.apply(es,ds); q=x['receipt']; e=store.engine if check or j==7 else None
        for key,value in x.get('sharing',{}).items(): sharing[key]=sharing.get(key,0)+value
        for key,value in x.get('material',{}).items(): material[key]=material.get(key,0)+value
        if prior is not None:
            now=store._owned; stats=x['sharing']
            a.require(stats['factors_reused']==sum(f is prior.inputs.get(name) for name,f in now.inputs.items())+sum(v in prior.rank and now.outputs[i] is prior.outputs[prior.rank[v]] for i,v in enumerate(now.order)))
            a.require(stats['records_reused']==sum(v in prior.rank and rec is prior.records[prior.rank[v]] for v,rec in zip(now.order,now.records)))
            a.require(stats['routes_reused']==(sum(x is y for x,y in zip(now.buckets,prior.buckets)) if now.order==prior.order else 0))
        if check:
            a.require(a.canonical(state.snapshot(old,x['version']-1))==before)
            rr=ref.solve(e.d,list(e.inputs.values()),e.order); receipt=k.check(s.certificate(e,rr))
            a.require(all(q[key]==receipt[key] for key in ('problem_sha256','certificate_sha256','optimum','variables','visits')) and store.get(store.version)==receipt)
        rows.append(dict(optimum=q['optimum'],action=x['action'],actual=x['actual'],full=q['visits'],fresh=q.get('fresh',q['visits']),hits=q.get('hits',0)))
        for key,val in x.get('profile',{}).items():
            if key!='forked': profile[key]=profile.get(key,0)+val
        if j==7:
            before=state.snapshot(e,store.version); store=cls(path); a.require(state.snapshot(store.engine,store.version)==before)
    reads=[store.get(v) for v in (1,8,16)]
    if check:
        versions,docs,demand=store.history(); a.require(versions==list(range(1,17)) and [k.check(docs[v-1]) for v in (1,8,16)]==reads)
    with sqlite3.connect(path) as db: pages=db.execute('PRAGMA page_count').fetchone()[0]*db.execute('PRAGMA page_size').fetchone()[0]
    return dict(rows=rows,reads=reads,pages=pages,sharing=sharing,material=material),profile


def ownership_controls(root):
    path=root/'control.sqlite'; x=sh.Store(path,{'a':2,'b':2}); supplied={(0,0):0,(0,1):0}; x.apply({'f':(('a','b'),supplied)})
    old=x._owned; receipts=x._receipts; version=x.version; before=a.canonical(state.snapshot(x.engine,version)); total=0
    def unchanged():
        a.require(x._owned is old and x._receipts is receipts and x.version==version and a.canonical(state.snapshot(x.engine,version))==before and a.canonical(state.snapshot(sh.Store(path).engine,version))==before)
    def reject(fn,errors=(ValueError,)):
        nonlocal total
        try: fn()
        except errors: total+=1
        else: raise ValueError('invalid operation accepted')
    for fn in (lambda:old.d.__setitem__('a',3),lambda:old.inputs['f'][1].__setitem__((0,0),99),lambda:old.buckets[0].clear(),lambda:old.records[0][2][0].__setitem__(1,1),lambda:setattr(old,'budget',9),lambda:receipts.clear(),lambda:setattr(x,'engine',x.engine),lambda:setattr(x,'_receipts',{})):
        reject(fn,(AttributeError,TypeError))
    supplied[(0,0)]=99; view=x.engine; view.inputs['f'][1][(0,0)]=99; view.records[0][2].clear(); view.d['a']=4; unchanged(); total+=1
    work=old.working(); a.require(work.outputs[0] is old.outputs[0] and work.buckets[0] is old.buckets[0]); work.update({'f':(('a','b'),{(1,0):0,(1,1):0})}); unchanged(); total+=1
    reject(lambda:x.apply({}, {'a':0})); unchanged()
    with patch.object(o.sp,'checked',side_effect=ValueError('gate refusal')): reject(lambda:x.apply({}))
    unchanged()
    with sqlite3.connect(path) as db: db.execute("CREATE TRIGGER refuse BEFORE INSERT ON dense_versions BEGIN SELECT RAISE(ABORT,'injected'); END")
    reject(lambda:x.apply({'f':(('b',),{(1,):4})}),(sqlite3.IntegrityError,)); unchanged()
    with sqlite3.connect(path) as db: db.execute('DROP TRIGGER refuse')
    stale=sh.Store(path); q=x.apply({'f':(('a','b'),{(1,0):0,(1,1):0})})['receipt']; a.require(q['optimum']==0 and q['hits']==1); total+=1
    reject(lambda:stale.apply({})); a.require(stale.version==version and a.canonical(state.snapshot(stale.engine,version))==before)
    x.apply({}, {'b':3}); a.require(x.engine.d['b']==3 and sh.Store(path).get(x.version)==x.get(x.version)); total+=1
    legacy=f.Store(path); legacy.apply({}); y=sh.Store(path); a.require(y.version==legacy.version and y.get(y.version)==legacy.get(legacy.version)); total+=1
    prior=y._owned; receipts=y._receipts; q=y.apply({})['sharing']; now=y._owned
    a.require(q['factors_new']==q['records_new']==q['routes_new']==0 and all(now.inputs[name] is prior.inputs[name] for name in now.inputs) and all(i is j for i,j in zip(now.records,prior.records)) and all(i is j for i,j in zip(now.buckets,prior.buckets)) and all(y._receipts[v] is receipts[v] for v in receipts)); total+=1
    prior=y._owned; view=y.engine; y.apply({'constant':((),{():-3})}); a.require(y.get(y.version)['optimum']==-3 and prior.working(detach=True).inputs==view.inputs); total+=1
    old=y._owned; receipt=y._receipts; version=y.version
    with patch.object(sh,'capture',side_effect=ValueError('capture refusal')): reject(lambda:y.apply({}))
    a.require(y._owned is old and y._receipts is receipt and y.version==version and sh.Store(path).version==version)
    return total


def controls(root):
    total=ownership_controls(root)
    path=root/'cache.sqlite'; x=m.Store(path,{'a':2,'b':2}); x.apply({'f':(('a','b'),{(0,0):0,(0,1):0})})
    old=x._packed; prior=x._owned; version=x.version
    q=x.apply({})['material']; a.require(q['packed_hits']==3 and q['packed_misses']==0 and all(x._packed[id(f)][1] is old[id(f)][1] for f in x._owned.outputs)); total+=1
    q=x.apply({'f':(('a','b'),{(1,0):0,(1,1):0})}); a.require(q['material']['packed_hits']==2 and q['material']['packed_misses']==1 and x.engine.records[0][2][0][1]==1); total+=1
    old=x._packed; prior=x._owned; version=x.version; receipts=x._receipts; before=a.canonical(state.snapshot(x.engine,version))
    def reject(fn,errors=(ValueError,)):
        nonlocal total
        try: fn()
        except errors: total+=1
        else: raise ValueError('bad material accepted')
    def unchanged():
        a.require(x._packed is old and x._owned is prior and x._receipts is receipts and x.version==version and a.canonical(state.snapshot(m.Store(path).engine,version))==before)
    with patch.object(m.sp,'checked',side_effect=ValueError('gate')): reject(lambda:x.apply({}))
    unchanged()
    with sqlite3.connect(path) as db: db.execute("CREATE TRIGGER fail BEFORE INSERT ON dense_versions BEGIN SELECT RAISE(ABORT,'injected'); END")
    reject(lambda:x.apply({'f':(('b',),{(1,):4})}),(sqlite3.IntegrityError,)); unchanged()
    with sqlite3.connect(path) as db: db.execute('DROP TRIGGER fail')
    # Equal-but-distinct factors must not hit; Boolean table value must be rejected.
    work=x._owned.working(detach=True); z=work.update({})['result']; snap,doc,q=m.materialize(work,z,version,work.d,work.inputs,work.budget,x._packed)
    a.require(q['packed_hits']==0 and q['packed_misses']==3); total+=1
    work.inputs['f'][1][(1,0)]=False
    snap,doc,_=m.materialize(work,z,version,work.d,work.inputs,work.budget,x._packed)
    reject(lambda:sp.checked(snap,doc,x._receipts)); unchanged()
    stale=m.Store(path); x.apply({}); reject(lambda:stale.apply({})); a.require(stale.version==version)
    x.apply({}, {'b':3}); y=m.Store(path); a.require(y.get(y.version)==x.get(x.version) and y.seed['hits']==0); total+=1
    legacy=f.Store(path); legacy.apply({}); y=m.Store(path); a.require(y.get(y.version)==legacy.get(legacy.version)); total+=1
    return total


def audit(root):
    root=root.resolve(); root.mkdir(); rows=[]; timings=[]; methods={'fork':f.Store,'owned':o.Store,'share':sh.Store,'material':m.Store}
    for i,(name,d,edits) in enumerate(corpus()):
        results={label:run(cls,root/f'{name}-{label}.sqlite',d,edits,True)[0] for label,cls in methods.items()}
        for label in methods:
            a.require(all(results[label][key]==results['fork'][key] for key in ('rows','reads','pages')))
        a.require(results['material']['sharing']==results['share']['sharing'])
        rows.append(dict(name=name,**results)); ns={key:[] for key in methods}
        for rep in range(3):
            labels=list(methods); random.Random(i*17+rep).shuffle(labels)
            for label in labels:
                path=root/f'timing-{i}-{rep}-{label}.sqlite'; start=time.perf_counter_ns(); run(methods[label],path,d,edits); ns[label].append(time.perf_counter_ns()-start); path.unlink()
        timings.append(dict(name=name,ns=ns))
    ratios={base:[st.median(x['ns']['material'])/st.median(x['ns'][base]) for x in timings] for base in ('owned','share','fork')}
    geo={base:math.exp(st.mean(map(math.log,v))) for base,v in ratios.items()}; worst={base:max(v) for base,v in ratios.items()}; ncontrols=controls(root)
    out=dict(rows=rows,controls=ncontrols,timings=timings,geomean=geo,worst=worst,decision='REVIEW_CANDIDATE' if ncontrols==29 and max(geo.values())<=.9 and max(worst.values())<=1.2 else 'NO_PROMOTION',scope='identity-bound private packed-factor cache; all mathematical certificate fields still independently checked; unchanged checkpoint format; timing includes create, 16 commits, reopen, three reads and page accounting; no RSS, hostile Python isolation, formal proof or original RE-X equivalence')
    out['evidence_sha256']=a.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--directory',type=Path,required=True); args=p.parse_args(); out=audit(args.directory); (args.directory/'evidence.json').write_bytes(a.canonical(out)); print({key:out[key] for key in ('controls','geomean','worst','decision')})
