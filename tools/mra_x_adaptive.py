"""Phase IX: bounded adaptive planning and cross-order bucket reuse after scope edits."""
import argparse
import copy
import hashlib
import itertools
import json
import math
import time
import tracemalloc
from pathlib import Path
import mra_x_topology as ref
import mra_x_upgrade as up
import mra_x_separator as sep
import mra_x_certify as cert
import mra_x_gap_agent as gap


def require(ok):
    if not ok: raise ValueError('adaptive audit failed')


def hierarchy(g, vs):
    vs=sorted(vs); parts=sep.components(g,vs)
    if len(parts)>1: return [v for p in parts for v in hierarchy(g,p)]
    if len(vs)<=4: return vs
    # Search width three only in small regions; avoid cubic search on large graphs.
    for k in range(1,4 if len(vs)<=20 else 3):
        best=None
        for s in itertools.combinations(vs,k):
            groups=sep.components(g,set(vs)-set(s))
            if len(groups)>1:
                key=(max(map(len,groups)),s)
                if best is None or key<best[0]: best=(key,groups)
        if best is not None: return [v for p in best[1] for v in hierarchy(g,p)]+list(best[0][1])
    return vs


def key(bucket):
    return tuple(sorted((s,tuple(sorted(t.items()))) for s,t in bucket))


class Adaptive:
    def __init__(self,d,budget=1000000):
        ref.validate(d,[])
        if len(d)>64 or any(not isinstance(v,str) or k>4 for v,k in d.items()) or type(budget) is not int or not 1<=budget<=10000000: raise ValueError('envelope')
        self.d=dict(d); self.budget=budget; self.cache={}; self.previous=None

    def estimate(self,f,o):
        # Unknown message values on a predicted miss: never assume a subsequent cache hit.
        active=list(f); upper=0; full=0
        for v in o:
            bucket=[(s,t) for s,t in active if v in s]; active=[(s,t) for s,t in active if v not in s]
            boundary=tuple(sorted({u for s,_ in bucket for u in s}-{v})); count=self.d[v]*math.prod(self.d[u] for u in boundary); full+=count
            old=self.cache.get(v)
            if old is not None and all(t is not None for _,t in bucket) and old[0]==key(bucket): table=old[1]
            else: table=None; upper+=count
            active.append((boundary,table))
        return upper,full

    def solve(self,f):
        d=self.d; f=[(tuple(s),dict(t)) for s,t in f]; ref.validate(d,f)
        if len(f)>1024: raise ValueError('factor budget')
        options=[('predictor',up.choose(d,f)[1]),('hierarchy',hierarchy(cert.graph(d,f),d))]
        if self.previous is not None: options.append(('previous',self.previous))
        candidates=[]
        for label,o in options:
            upper,full=self.estimate(f,o)
            if full<=self.budget: candidates.append((upper,full,label,o))
        if not candidates: return {'status':'BUDGET_EXHAUSTED'}
        upper,full,label,o=min(candidates); active=list(f); next_cache={}; trace=[]; visits=hits=width=0
        for v in o:
            bucket=[(s,t) for s,t in active if v in s]; active=[(s,t) for s,t in active if v not in s]
            k=key(bucket); boundary=tuple(sorted({u for s,_ in bucket for u in s}-{v})); width=max(width,len(boundary))
            old=self.cache.get(v)
            if old is not None and old[0]==k: _,table,rows=old; hits+=1
            else:
                table={}; rows=[]
                for row in ref.assignments(d,boundary):
                    a=dict(zip(boundary,row)); best=arg=None
                    for x in range(d[v]):
                        a[v]=x; visits+=1; val=ref.score(bucket,a)
                        if val is not None and (best is None or val<best): best,arg=val,x
                    if best is not None: table[row]=best; rows.append([list(row),arg])
            next_cache[v]=(k,table,rows); active.append((boundary,table)); trace.append([v,list(boundary),rows])
        opt=ref.score(active,{})
        result=dict(optimum=opt,witness=None if opt is None else ref.recover(trace),trace=copy.deepcopy(trace),order=list(o),induced_width=width,assignments_evaluated=full)
        require(visits<=upper<=full)
        self.cache=next_cache; self.previous=list(o)
        return dict(status='SOLVED',result=result,actual=visits,upper=upper,hits=hits,policy=label)


def workload(seed,n,kind):
    d,f=sep.instance(seed,n,kind); vs=list(d)
    bridge=((vs[0],vs[n//2],vs[-1]),{a:sum(a)-2 for a in ref.assignments(d,(vs[0],vs[n//2],vs[-1]))})
    unary=((vs[-1],),{})
    # Remove original edge (possibly disconnect), add higher-order bridge, duplicate it,
    # remove it, restore and repeat. Constants and infeasibility are also covered.
    cut=f[1:]; return d,[f,cut,cut+[bridge],cut+[bridge,bridge],cut, f+[unary],f+[ ((),{}) ],f,list(reversed(f)),f]


def audit():
    rows=[]; controls=0
    for i,kind in enumerate(('chain','cycle','triangles')):
        for j,n in enumerate((8,16,32,64)):
            d,seq=workload(9100+i*10+j,n,kind); e=Adaptive(d); fixed=up.Incremental(d,ref.min_fill(d,seq[0])); hfixed=up.Incremental(d,hierarchy(cert.graph(d,seq[0]),d))
            previous=None
            for step,f in enumerate(seq):
                a=e.solve(f); require(a['status']=='SOLVED'); r=a['result']; b=fixed.solve(f); h=hfixed.solve(f); fresh=ref.solve(d,f)
                require(cert.verify_solution(d,f,r)==r['assignments_evaluated'] and r==ref.solve(d,f,r['order']))
                require(r['optimum']==b['optimum']==h['optimum']==fresh['optimum'])
                if n==8: require(r['optimum']==ref.brute(d,f))
                for x in (b,h,fresh): require(x['witness'] is None if r['optimum'] is None else ref.score(f,x['witness'])==r['optimum'])
                rows.append(dict(kind=kind,n=n,step=step,actual=a['actual'],upper=a['upper'],full=r['assignments_evaluated'],hits=a['hits'],policy=a['policy'],order_changed=previous is not None and previous!=r['order'],fixed=b['assignments_evaluated'],fixed_hierarchy=h['assignments_evaluated'],fresh=fresh['assignments_evaluated'],feasible=r['optimum'] is not None))
                previous=r['order']
    # K(3,5) has no separator smaller than three; hierarchy must leave the 3 hubs last.
    d={str(i):2 for i in range(8)}; f=[((str(i),str(j)),{a:sum(a) for a in itertools.product(range(2),repeat=2)}) for i in range(3) for j in range(3,8)]
    require(hierarchy(cert.graph(d,f),d)[-3:]==['0','1','2']); controls+=1
    for d,f in (({},[]),({},[((),{})]),({'a':2},[])):
        e=Adaptive(d); a=e.solve(f); require(a['result']==ref.solve(d,f)); require(e.solve(f)['actual']==0); controls+=1
    d,f=workload(9199,8,'cycle'); e=Adaptive(d,budget=1); require(e.solve(f[0])=={'status':'BUDGET_EXHAUSTED'} and not e.cache and e.previous is None); controls+=1
    # Measure a separate workload; timings and Python heap peaks are not deterministic.
    d,seq=workload(9201,32,'cycle'); perf=[]
    for name in ('adaptive','fixed_min_fill','fresh_min_fill'):
        times=[]; peaks=[]
        for _ in range(3):
            tracemalloc.start(); start=time.perf_counter_ns()
            if name=='adaptive': e=Adaptive(d); results=[e.solve(f) for f in seq]
            elif name=='fixed_min_fill': e=up.Incremental(d,ref.min_fill(d,seq[0])); results=[e.solve(f) for f in seq]
            else: results=[ref.solve(d,f) for f in seq]
            times.append(time.perf_counter_ns()-start); peaks.append(tracemalloc.get_traced_memory()[1]); tracemalloc.stop()
        perf.append(dict(name=name,elapsed_ns=times,python_peak_bytes=peaks))
    out=dict(rows=rows,controls=controls,performance=perf,source_sha256={Path(p).name:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in (__file__,ref.__file__,up.__file__,sep.__file__,cert.__file__,gap.__file__)},scope='fixed domains; scope edits replan, not local tree repair; conservative cache-miss bounds; Python traced allocations and sequential timings, not native RSS or controlled benchmark; no mechanized proof')
    out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); r=audit()
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps(dict(cases=len(r['rows']),controls=r['controls'],**{k:sum(x[k] for x in r['rows']) for k in ('actual','upper','full','hits','fixed','fixed_hierarchy','fresh','order_changed')},performance=r['performance']),indent=2))
