"""Phase X: compiled bucket routing, bounded plan cache and performance arbitration."""
import argparse
import copy
import hashlib
import json
import math
import random
import statistics
import time
import tracemalloc
from collections import OrderedDict
from pathlib import Path
import mra_x_topology as ref
import mra_x_adaptive as ad
import mra_x_upgrade as up
import mra_x_certify as cert
import mra_x_gap_agent as gap


def require(ok):
    if not ok: raise ValueError('meta audit failed')


def compile_plan(d,scopes,o):
    rank={v:i for i,v in enumerate(o)}; n=len(o); slots=[[] for _ in range(n+1)]
    def dest(s): return min((rank[v] for v in s),default=n)
    for i,s in enumerate(scopes): slots[dest(s)].append((i,s))
    steps=[]; full=width=0
    for i,v in enumerate(o):
        incoming=slots[i]; boundary=tuple(sorted({u for _,s in incoming for u in s}-{v}))
        layout=(v,)+boundary; index={u:j for j,u in enumerate(layout)}
        # Precompute coordinate maps, not assignment tuples or costs.
        terms=tuple((p,tuple(index[u] for u in s)) for p,s in incoming)
        output=len(scopes)+i; slots[dest(boundary)].append((output,boundary))
        count=d[v]*math.prod(d[u] for u in boundary); full+=count; width=max(width,len(boundary))
        steps.append((v,boundary,terms,output,count))
    return steps,tuple(p for p,_ in slots[n]),full,width


class Meta:
    def __init__(self,d,budget=1000000,plan_limit=8):
        ref.validate(d,[])
        if len(d)>64 or any(not isinstance(v,str) or k>4 for v,k in d.items()) or type(budget) is not int or not 1<=budget<=10000000 or type(plan_limit) is not int or not 1<=plan_limit<=32: raise ValueError('envelope')
        self.d=dict(d); self.budget=budget; self.plan_limit=plan_limit
        self.plans=OrderedDict(); self.cache={}; self.previous=None

    def plan(self,scopes):
        if scopes in self.plans:
            self.plans.move_to_end(scopes); return self.plans[scopes],True
        d=self.d; f=[(s,{}) for s in scopes]
        # Prefer stable orders. Replan only when the prior order exceeds the
        # enumeration budget or costs over twice the new min-fill order.
        new=ref.min_fill(d,f); pn=compile_plan(d,scopes,new)
        if self.previous is None: o,p=new,pn
        else:
            old=self.previous; po=compile_plan(d,scopes,old)
            o,p=(old,po) if po[2]<=self.budget and po[2]<=2*pn[2] else (new,pn)
        if p[2]>self.budget: return None,False
        self.plans[scopes]=(o,p)
        if len(self.plans)>self.plan_limit: self.plans.popitem(last=False)
        return (o,p),False

    def solve(self,f):
        d=self.d; f=sorted(((tuple(s),dict(t)) for s,t in f),key=lambda x:x[0]); ref.validate(d,f)
        if len(f)>1024: raise ValueError('factor budget')
        scopes=tuple(s for s,_ in f); chosen,plan_hit=self.plan(scopes)
        if chosen is None: return {'status':'BUDGET_EXHAUSTED'}
        o,(steps,terminal,full,width)=chosen
        tables=[t for _,t in f]+[None]*len(o); keys=[tuple(sorted(t.items())) for _,t in f]+[None]*len(o)
        trace=[]; next_cache={}; work=hits=0
        for v,boundary,terms,output,count in steps:
            # Coordinate maps identify original factor scope in this step's layout.
            k=(boundary,tuple(sorted((indices,keys[p]) for p,indices in terms)))
            old=self.cache.get(v)
            if old is not None and old[0]==k: _,table,rows,content=old; hits+=1
            else:
                table={}; rows=[]; work+=count
                inputs=[(tables[p],indices) for p,indices in terms]
                for row in ref.assignments(d,boundary):
                    best=arg=None
                    for x in range(d[v]):
                        a=(x,)+row; value=0
                        for t,indices in inputs:
                            c=t.get(tuple(a[j] for j in indices))
                            if c is None: break
                            value+=c
                        else:
                            if best is None or value<best: best,arg=value,x
                    if best is not None: table[row]=best; rows.append([list(row),arg])
                content=tuple(sorted(table.items()))
            tables[output]=table; keys[output]=content; next_cache[v]=(k,table,rows,content); trace.append([v,list(boundary),rows])
        vals=[tables[p].get(()) for p in terminal]; opt=None if None in vals else sum(vals)
        result=dict(optimum=opt,witness=None if opt is None else ref.recover(trace),trace=copy.deepcopy(trace),order=list(o),induced_width=width,assignments_evaluated=full)
        self.cache=next_cache; self.previous=list(o)
        return dict(status='SOLVED',result=result,actual=work,hits=hits,plan_hit=plan_hit)


def run(name,d,seq):
    if name=='meta': e=Meta(d); return [e.solve(f) for f in seq]
    if name=='adaptive': e=ad.Adaptive(d); return [e.solve(f) for f in seq]
    if name=='fixed_min_fill': e=up.Incremental(d,ref.min_fill(d,seq[0])); return [e.solve(f) for f in seq]
    if name=='fixed_hierarchy': e=up.Incremental(d,ad.hierarchy(cert.graph(d,seq[0]),d)); return [e.solve(f) for f in seq]
    return [ref.solve(d,f) for f in seq]


def audit():
    names=('meta','adaptive','fixed_min_fill','fixed_hierarchy','fresh_min_fill'); rows=[]; perf=[]; controls=0
    for i,kind in enumerate(('chain','cycle','triangles')):
        for j,n in enumerate((8,16,32,64)):
            d,seq=ad.workload(10100+i*100+j,n,kind)
            results={name:run(name,d,seq) for name in names}
            for step,f in enumerate(seq):
                a=results['meta'][step]; r=a['result']; require(cert.verify_solution(d,f,r)==r['assignments_evaluated'] and r==ref.solve(d,f,r['order']))
                vals={}; work={}
                for name in names:
                    x=results[name][step]; y=x['result'] if 'result' in x else x
                    vals[name]=y['optimum']; work[name]=x.get('actual',y['assignments_evaluated'])
                    require(y['witness'] is None if r['optimum'] is None else ref.score(f,y['witness'])==r['optimum'])
                require(all(v==r['optimum'] for v in vals.values()))
                if n==8: require(r['optimum']==ref.brute(d,f))
                rows.append(dict(kind=kind,n=n,step=step,visits=work,plan_hit=a['plan_hit'],bucket_hits=a['hits'],feasible=r['optimum'] is not None))
            # Separate timing from allocation measurement; rotate repeat order deterministically.
            times={name:[] for name in names}; peaks={}
            for repeat in range(5):
                rotation=list(names); random.Random(11000+i*100+j*10+repeat).shuffle(rotation)
                for name in rotation:
                    start=time.perf_counter_ns(); result=run(name,d,seq); times[name].append(time.perf_counter_ns()-start); del result
            for name in names:
                tracemalloc.start(); result=run(name,d,seq); peaks[name]=tracemalloc.get_traced_memory()[1]; tracemalloc.stop(); del result
            perf.append(dict(kind=kind,n=n,times_ns=times,python_peak_bytes=peaks))
    for d,f in (({},[]),({},[((),{})]),({'a':2},[])):
        e=Meta(d); require(e.solve(f)['result']==ref.solve(d,f)); require(e.solve(f)['actual']==0); controls+=1
    d,seq=ad.workload(10999,8,'cycle'); e=Meta(d,budget=1); require(e.solve(seq[0])=={'status':'BUDGET_EXHAUSTED'} and not e.plans and not e.cache); controls+=1
    e=Meta(d,plan_limit=1)
    for f in seq: require(e.solve(f)['result']['optimum']==ref.brute(d,f) and len(e.plans)<=1)
    controls+=1
    e=Meta(d); a=e.solve(seq[0]); a['result']['trace'].clear(); require(e.solve(seq[0])['result']==ref.solve(d,seq[0],e.previous)); controls+=1
    medians={name:[statistics.median(p['times_ns'][name]) for p in perf] for name in names}
    ratios={name:math.exp(statistics.mean(math.log(a/b) for a,b in zip(medians['meta'],medians[name]))) for name in names if name!='meta'}
    # Predeclared: require >=10% geometric-mean speedup versus every baseline and no >20% slowdown in any workload.
    worst=max(a/b for name in ratios for a,b in zip(medians['meta'],medians[name]))
    decision='REVIEW_CANDIDATE' if max(ratios.values())<=.9 and worst<=1.2 else 'NO_PROMOTION'
    out=dict(rows=rows,controls=controls,performance=perf,geomean_time_ratio=ratios,worst_time_ratio=worst,decision=decision,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('mra_x_*.py'))},scope='fixed synthetic workloads; bounded plan cache; time includes setup and full output, excludes checker; separate Python allocation tracing, not RSS; local timing not independent replication; no automatic promotion')
    out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); r=audit()
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps(dict(cases=len(r['rows']),controls=r['controls'],plan_hits=sum(x['plan_hit'] for x in r['rows']),bucket_hits=sum(x['bucket_hits'] for x in r['rows']),visits={k:sum(x['visits'][k] for x in r['rows']) for k in r['rows'][0]['visits']},ratios=r['geomean_time_ratio'],worst=r['worst_time_ratio'],decision=r['decision']),indent=2))
