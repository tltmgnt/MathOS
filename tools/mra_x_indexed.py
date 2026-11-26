"""Phase XII: dependency-indexed exact incremental elimination at fixed order."""
import argparse
import copy
import hashlib
import heapq
import json
import math
import random
import statistics
import time
from collections import defaultdict
from pathlib import Path
import mra_x_topology as ref
import mra_x_upgrade as up
import mra_x_meta as meta
import mra_x_dispatch as dispatch
import mra_x_certify as cert
import mra_x_gap_agent as gap


def require(ok):
    if not ok: raise ValueError('indexed audit failed')


class BudgetExceeded(ValueError):
    pass


class Indexed:
    def __init__(self,d,order,budget=1000000):
        ref.validate(d,[])
        if len(d)>128 or any(not isinstance(v,str) or k>4 for v,k in d.items()) or len(order)!=len(d) or set(order)!=set(d): raise ValueError('envelope or order')
        if type(budget) is not int or not 1<=budget<=10000000: raise ValueError('budget')
        self.d=dict(d); self.order=tuple(order); self.rank={v:i for i,v in enumerate(order)}
        self.n=len(order); self.budget=budget; self.inputs={}; self.buckets=[{} for _ in range(self.n+1)]; self.outputs=[None]*self.n; self.records=[None]*self.n; self.counts=[0]*self.n

    def dest(self,s): return min((self.rank[v] for v in s),default=self.n)

    def update(self,edits):
        """ID -> (scope, table) or None (delete); atomic on validation/budget failure."""
        d=self.d; n=self.n
        if len(edits)>2048: raise ValueError('edit limit')
        inputs=self.inputs.copy(); buckets=self.buckets[:]; outputs=self.outputs[:]; records=self.records[:]; counts=self.counts[:]
        copied=set(); dirty=set(); heap=[]
        def mark(i):
            if i<n and i not in dirty: dirty.add(i); heapq.heappush(heap,i)
        def mutable(i):
            if i not in copied: buckets[i]=buckets[i].copy(); copied.add(i)
            return buckets[i]
        for name,value in edits.items():
            if not isinstance(name,str) or not name or len(name)>128: raise ValueError('factor ID')
            old=inputs.get(name)
            if value is None:
                if old is None: raise ValueError('unknown factor')
            else:
                value=(tuple(value[0]),dict(value[1])); ref.validate(d,[value])
            if old==value: continue
            if old is not None:
                i=self.dest(old[0]); del mutable(i)[('input',name)]; mark(i); del inputs[name]
            if value is not None:
                i=self.dest(value[0]); mutable(i)[('input',name)]=value; mark(i); inputs[name]=value
        if len(inputs)>1024: raise ValueError('factor limit')
        for i,o in enumerate(outputs):
            if o is None: mark(i)
        visits=recomputed=changed=0
        while heap:
            i=heapq.heappop(heap); dirty.remove(i); v=self.order[i]; fs=list(buckets[i].values())
            boundary=tuple(sorted({u for s,_ in fs for u in s}-{v})); count=d[v]*math.prod(d[u] for u in boundary)
            if visits+count>self.budget: raise BudgetExceeded('work budget')
            layout=(v,)+boundary; index={u:j for j,u in enumerate(layout)}; terms=[(tuple(index[u] for u in s),t) for s,t in fs]
            table={}; rows=[]
            for row in ref.assignments(d,boundary):
                best=arg=None
                for x in range(d[v]):
                    a=(x,)+row; val=0
                    for idx,t in terms:
                        c=t.get(tuple(a[j] for j in idx))
                        if c is None: break
                        val+=c
                    else:
                        if best is None or val<best: best,arg=val,x
                if best is not None: table[row]=best; rows.append([list(row),arg])
            visits+=count; recomputed+=1; counts[i]=count; records[i]=[v,list(boundary),rows]; new=(boundary,table); old=outputs[i]
            if new!=old:
                changed+=1
                if old is not None:
                    j=self.dest(old[0]); del mutable(j)[('message',i)]; mark(j)
                j=self.dest(boundary); require(j>i); mutable(j)[('message',i)]=new; mark(j); outputs[i]=new
        full=sum(counts)
        if full>self.budget: raise BudgetExceeded('full enumeration budget')
        opt=ref.score(list(buckets[n].values()),{}); witness=None if opt is None else ref.recover(records)
        r=dict(optimum=opt,witness=witness,trace=copy.deepcopy(records),order=list(self.order),induced_width=max((len(o[0]) for o in outputs),default=0),assignments_evaluated=full)
        self.inputs,self.buckets,self.outputs,self.records,self.counts=inputs,buckets,outputs,records,counts
        return dict(result=r,actual=visits,recomputed=recomputed,changed_messages=changed,skipped=n-recomputed)


class Snapshots:
    """Convenience adapter: stable factor IDs matched by exact content, retaining duplicates."""
    def __init__(self,d,order): self.engine=Indexed(d,order); self.serial=0
    def solve(self,f):
        pool=defaultdict(list)
        for name,(s,t) in self.engine.inputs.items(): pool[(s,tuple(sorted(t.items())))].append(name)
        edits={}; serial=self.serial
        for s,t in f:
            k=(tuple(s),tuple(sorted(t.items())))
            if pool[k]: pool[k].pop()
            else:
                serial+=1; edits[str(serial)]=(s,t)
        for names in pool.values():
            for name in names: edits[name]=None
        r=self.engine.update(edits); self.serial=serial; return r


def run(name,d,seq):
    if name=='indexed': e=Snapshots(d,ref.min_fill(d,seq[0])); return [e.solve(f) for f in seq]
    return meta.run(name,d,seq)


def audit():
    names=('indexed','fixed_min_fill','meta'); rows=[]; perf=[]; controls=0
    for i,kind in enumerate(('chain','cycle','triangles')):
        for j,n in enumerate((8,32,64)):
            for k,mode in enumerate(('structural','repeat','values')):
                seed=12100+i*100+j*10+k; d,seq=dispatch.workload(seed,n,kind,mode)
                a,b,c=[run(name,d,seq) for name in names]
                for f,x,y,z in zip(seq,a,b,c):
                    r=x['result']; require(r==ref.solve(d,f,r['order']) and cert.verify_solution(d,f,r)==r['assignments_evaluated'])
                    require(r['optimum']==y['optimum']==z['result']['optimum'] and x['actual']==y['assignments_evaluated'])
                    for q in (y,z['result']): require(q['witness'] is None if r['optimum'] is None else ref.score(f,q['witness'])==r['optimum'])
                    if n==8: require(r['optimum']==ref.brute(d,f))
                    rows.append(dict(kind=kind,n=n,mode=mode,actual=x['actual'],fixed=y['assignments_evaluated'],meta=z['actual'],full=r['assignments_evaluated'],recomputed=x['recomputed'],skipped=x['skipped'],changed_messages=x['changed_messages'],feasible=r['optimum'] is not None))
                times={name:[] for name in names}
                for repeat in range(5):
                    rotation=list(names); random.Random(seed+repeat).shuffle(rotation)
                    for name in rotation:
                        start=time.perf_counter_ns(); run(name,d,seq); times[name].append(time.perf_counter_ns()-start)
                perf.append(dict(kind=kind,n=n,mode=mode,times_ns=times))
    # Direct-ID witness-only update: output unchanged, upstream work not needed.
    e=Indexed({'a':2,'b':2},['a','b']); e.update({'f':(('a','b'),{(0,0):0,(0,1):0})})
    x=e.update({'f':(('a','b'),{(1,0):0,(1,1):0})}); require(x['result']['witness']=={'b':0,'a':1} and x['recomputed']==1 and x['changed_messages']==0); controls+=1
    # Budget rollback after a previously successful solve; old state remains reusable.
    d={v:2 for v in 'abc'}; e=Indexed(d,list(d),budget=8); e.update({}); old=e.update({})
    try: e.update({'f':(('a','b','c'),{(0,0,0):0})})
    except BudgetExceeded: require(e.update({})==old and not e.inputs); controls+=1
    else: raise ValueError('budget accepted')
    for d,f in (({},[]),({},[((),{})]),({'a':2},[])):
        e=Snapshots(d,list(d)); require(e.solve(f)['result']==ref.solve(d,f) and e.solve(f)['actual']==0); controls+=1
    e=Indexed({'a':2},['a']); e.update({'x':(('a',),{(0,):1})}); old=e.update({})
    for bad in ({'absent':None},{'x':(('a',),{(2,):1})}):
        try: e.update(bad)
        except ValueError: require(e.update({})==old); controls+=1
        else: raise ValueError('bad update accepted')
    e=Indexed({'a':2},['a']); r=e.update({}); r['result']['trace'].clear(); require(e.update({})['result']==ref.solve({'a':2},[])); controls+=1
    ratios={name:math.exp(statistics.mean(math.log(statistics.median(p['times_ns']['indexed'])/statistics.median(p['times_ns'][name])) for p in perf)) for name in names[1:]}
    worst={name:max(statistics.median(p['times_ns']['indexed'])/statistics.median(p['times_ns'][name]) for p in perf) for name in names[1:]}
    decision='REVIEW_CANDIDATE' if max(ratios.values())<=.9 and max(worst.values())<=1.2 else 'NO_PROMOTION'
    out=dict(rows=rows,performance=perf,ratios=ratios,worst=worst,decision=decision,controls=controls,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('mra_x_*.py'))},scope='fixed domains/order; direct ID edits or snapshot diff; dirty buckets only; output materialization still global; local sequential timings exclude verification; no external benchmark, mechanized proof or automatic promotion')
    out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); r=audit()
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps(dict(cases=len(r['rows']),controls=r['controls'],**{k:sum(x[k] for x in r['rows']) for k in ('actual','fixed','meta','full','recomputed','skipped','changed_messages','feasible')},ratios=r['ratios'],worst=r['worst'],decision=r['decision']),indent=2))
