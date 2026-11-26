"""Matched ownership hardening and held-out release audit."""
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
        for n in (20,72):
            d,fs=sep.instance(37100+i*100+n,n,kind); v=next(iter(d)); edits=[({str(j):x for j,x in enumerate(fs)}, {})]
            for j in (0,len(fs)//2,len(fs)-1):
                scope,table=fs[j]; tab=dict(table); row=next(iter(tab)); tab[row]+=7
                edits.extend([({str(j):(scope,tab)},{}),({str(j):fs[j]},{}),({}, {})])
            edits.extend([({'0':(fs[0][0],{})},{}),({'0':fs[0]},{}),({}, {v:d[v]+1}),({}, {v:d[v]}),({}, {}),({}, {})])
            yield f'{kind}-{n}',d,edits


def run(cls,path,d,edits,check=False):
    store=cls(path,d); rows=[]; profile={}
    for j,(es,ds) in enumerate(edits):
        old=store.engine if check else None; before=a.canonical(state.snapshot(old,store.version)) if check else None
        x=store.apply(es,ds); q=x['receipt']; e=store.engine if check or j==7 else None
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
    return dict(rows=rows,reads=reads,pages=pages),profile


def controls(root):
    path=root/'control.sqlite'; x=o.Store(path,{'a':2,'b':2}); supplied={(0,0):0,(0,1):0}; x.apply({'f':(('a','b'),supplied)})
    old=x._owned; receipts=x._receipts; version=x.version; before=a.canonical(state.snapshot(x.engine,version)); total=0
    def unchanged():
        a.require(x._owned is old and x._receipts is receipts and x.version==version and a.canonical(state.snapshot(x.engine,version))==before and a.canonical(state.snapshot(o.Store(path).engine,version))==before)
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
    stale=o.Store(path); q=x.apply({'f':(('a','b'),{(1,0):0,(1,1):0})})['receipt']; a.require(q['optimum']==0 and q['hits']==1); total+=1
    reject(lambda:stale.apply({})); a.require(stale.version==version and a.canonical(state.snapshot(stale.engine,version))==before)
    x.apply({}, {'b':3}); a.require(x.engine.d['b']==3 and o.Store(path).get(x.version)==x.get(x.version)); total+=1
    legacy=f.Store(path); legacy.apply({}); y=o.Store(path); a.require(y.version==legacy.version and y.get(y.version)==legacy.get(legacy.version)); total+=1
    return total


def audit(root):
    root=root.resolve(); root.mkdir(); rows=[]; timings=[]; methods={'full':s.Store,'routed':r.Store,'fork':f.Store,'owned':o.Store}
    for i,(name,d,edits) in enumerate(corpus()):
        results={label:run(cls,root/f'{name}-{label}.sqlite',d,edits,True)[0] for label,cls in methods.items()}
        for label in methods:
            a.require(results[label]['reads']==results['fork']['reads'])
            for x,y in zip(results[label]['rows'],results['fork']['rows']): a.require(all(x[key]==y[key] for key in ('optimum','action','actual','full')))
        a.require(results['owned']==results['fork']); rows.append(dict(name=name,**results)); ns={key:[] for key in methods}
        for rep in range(3):
            labels=list(methods); random.Random(i*17+rep).shuffle(labels)
            for label in labels:
                path=root/f'timing-{i}-{rep}-{label}.sqlite'; start=time.perf_counter_ns(); run(methods[label],path,d,edits); ns[label].append(time.perf_counter_ns()-start); path.unlink()
        timings.append(dict(name=name,ns=ns))
    ratios={label:{base:[st.median(x['ns'][label])/st.median(x['ns'][base]) for x in timings] for base in ('full','routed','fork') if base!=label} for label in ('owned','fork')}
    geo={label:{base:math.exp(st.mean(map(math.log,v))) for base,v in rr.items()} for label,rr in ratios.items()}; worst={label:{base:max(v) for base,v in rr.items()} for label,rr in ratios.items()}
    physical=sum(x['owned']['pages'] for x in rows)/sum(x['routed']['pages'] for x in rows); ncontrols=controls(root)
    decisions={label:'REVIEW_CANDIDATE' if ncontrols==17 and max(geo[label].values())<=.9 and max(worst[label].values())<=1.2 and physical<=.5 else 'NO_PROMOTION' for label in ('owned','fork')}
    out=dict(rows=rows,controls=ncontrols,timings=timings,geomean=geo,worst=worst,physical_ratio=physical,decisions=decisions,scope='new synthetic seeds; 16 edits, reopen, three historical reads and page accounting; read-only owned state, detached inspection, unchanged verification and disk format; no arbitrary Python bypass protection, thread safety, RSS, power-loss or formal program proof')
    out['evidence_sha256']=a.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--directory',type=Path,required=True); args=p.parse_args(); out=audit(args.directory); (args.directory/'evidence.json').write_bytes(a.canonical(out)); print({key:out[key] for key in ('controls','geomean','worst','physical_ratio','decisions')})
