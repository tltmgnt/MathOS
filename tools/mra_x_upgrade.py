"""Evidence-driven upgrade: structural order selection, incremental bucket reuse, DAG validation."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import mra_x_topology as ref
import mra_x_gap_agent as gap
import mra_x_curriculum_agent as curriculum


def require(condition):
    if not condition:
        raise ValueError('acceptance check failed')


def schedule(modules):
    registry = {m[0]:m for m in modules}
    if len(registry)!=len(modules): raise ValueError('duplicate module')
    if any(d not in registry for m in modules for d in m[3]): raise ValueError('unknown prerequisite')
    done=[]; seen=set()
    while len(done)<len(modules):
        ready=sorted(k for k,m in registry.items() if k not in seen and set(m[3])<=seen)
        if not ready: raise ValueError('dependency cycle')
        done.extend(registry[k] for k in ready); seen.update(ready)
    return done


def predict(domains, factors, order):
    """Exact candidate enumeration count for this dense-table kernel, without solving."""
    if len(order)!=len(domains) or set(order)!=set(domains): raise ValueError('bad order')
    scopes=[set(s) for s,_ in factors]; visits=width=0
    for v in order:
        bucket=[s for s in scopes if v in s]
        scopes=[s for s in scopes if v not in s]
        boundary=set().union(*bucket)-{v}
        scopes.append(boundary)
        visits+=domains[v]*math.prod(domains[u] for u in boundary)
        width=max(width,len(boundary))
    return visits,width


def choose(domains,factors):
    candidates=[(s,gap.order_for(s,domains,factors)) for s in gap.STRATEGIES]
    return min(candidates,key=lambda p:predict(domains,factors,p[1]))


class Incremental:
    """Reuse exact bucket results when complete input factors and fixed domains match."""
    def __init__(self,domains,order):
        self.domains=dict(domains); self.order=tuple(order); self.cache={}
        ref.validate(self.domains,[]); predict(self.domains,[],self.order)

    def solve(self,factors):
        d=self.domains; active=[(tuple(s),dict(t)) for s,t in factors]; ref.validate(d,active)
        predict(d,active,self.order)
        domain_key=tuple(sorted(d.items()))
        trace=[]; visits=reused=width=0; next_cache={}
        for v in self.order:
            bucket=[(s,t) for s,t in active if v in s]
            active=[(s,t) for s,t in active if v not in s]
            # Canonical multiset, retaining multiplicity and all integer costs.
            key=(domain_key,tuple(sorted((s,tuple(sorted(t.items()))) for s,t in bucket)))
            boundary=tuple(sorted({u for s,_ in bucket for u in s if u!=v}))
            width=max(width,len(boundary))
            if v in self.cache and self.cache[v][0]==key:
                _,table,rows=self.cache[v]; reused+=1
            else:
                table={}; rows=[]
                for row in ref.assignments(d,boundary):
                    a=dict(zip(boundary,row)); best=arg=None
                    for x in range(d[v]):
                        a[v]=x; visits+=1; cost=ref.score(bucket,a)
                        if cost is not None and (best is None or cost<best): best,arg=cost,x
                    if best is not None: table[row]=best; rows.append([list(row),arg])
            next_cache[v]=(key,table,rows); active.append((boundary,table))
            trace.append([v,list(boundary),rows])
        optimum=ref.score(active,{})
        witness=None if optimum is None else ref.recover(trace)
        self.cache=next_cache
        return dict(optimum=optimum,witness=witness,trace=copy.deepcopy(trace),induced_width=width,
                    assignments_evaluated=visits,reused_buckets=reused,order=list(self.order))


def audit(seeds=12):
    if not 1<=seeds<=32: raise ValueError('seed count outside bounded range')
    order=schedule(list(reversed(curriculum.MODULES)))
    require(len(order)==24)
    for bad in [[('a','a',None,('b',),None)], [('a','a',None,('a',),None)], [order[0],order[0]]]:
        try: schedule(bad)
        except ValueError: pass
        else: raise ValueError('invalid registry accepted')
    selected=baseline=old_policy=checks=0; families={}
    old=curriculum.campaign()
    require(old['summary']['LAB_FAIL']==0 and old['summary']['BLOCKED']==0)
    frozen=old['modules']['OPT-702']['evidence']['frozen_strategy']
    for i,f in enumerate(gap.FAMILIES):
        stats=dict(cases=0,selected=0,baseline=0,old_policy=0)
        for trial in range(seeds):
            d, variants=gap.build(f,920000+i*100+trial,trial)
            for _,factors in variants:
                expected=gap.oracle(d,factors)
                strategy,o=choose(d,factors); b=ref.min_fill(d,factors)
                r=ref.solve(d,factors,o); base=ref.solve(d,factors,b)
                prev=ref.solve(d,factors,gap.order_for(frozen[f],d,factors))
                for candidate in (r,base,prev):
                    require(gap.check_result(d,factors,expected,candidate)); checks+=1
                require(predict(d,factors,o)==(r['assignments_evaluated'],r['induced_width']))
                require(r['assignments_evaluated']<=base['assignments_evaluated'])
                stats['cases']+=1; stats['selected']+=r['assignments_evaluated']; stats['baseline']+=base['assignments_evaluated']; stats['old_policy']+=prev['assignments_evaluated']
        families[f]=stats; selected+=stats['selected']; baseline+=stats['baseline']; old_policy+=stats['old_policy']
    updates=incremental_visits=full_visits=reuse=0
    for i,f in enumerate(gap.FAMILIES):
        for trial in range(seeds):
            d,variants=gap.build(f,930000+i*100+trial,trial)
            factors=variants[0][1]; o=ref.min_fill(d,factors); engine=Incremental(d,o)
            initial=engine.solve(factors); require(gap.check_result(d,factors,gap.oracle(d,factors),initial))
            v=list(d)[-1]; extra=((v,),{(x,):x-2 for x in range(d[v])})
            scope=tuple(list(d)[:2])+tuple(list(d)[-1:])
            joint=(scope,{a:sum(a)-2 for a in ref.assignments(d,scope) if sum(a)%2==0})
            edits=[factors+[extra],factors, factors[1:],factors+[joint],factors+[joint,joint],factors+[ ((), {}) ], factors, factors]
            for edited in edits:
                r=engine.solve(edited); fresh=ref.solve(d,edited,o)
                require(gap.check_result(d,edited,gap.oracle(d,edited),r))
                require((r['optimum'],r['witness'],r['trace'])==(fresh['optimum'],fresh['witness'],fresh['trace']))
                require(r['assignments_evaluated']<=fresh['assignments_evaluated'])
                updates+=1; incremental_visits+=r['assignments_evaluated']; full_visits+=fresh['assignments_evaluated']; reuse+=r['reused_buckets']
            require(r['assignments_evaluated']==0 and r['reused_buckets']==len(d))
    result={'baseline_curriculum':old['summary'],'dependency_schedule': [m[0] for m in order],
            'invalid_registry_controls':3,'predictive':{'cases':sum(s['cases'] for s in families.values()),'candidate_checks':checks,'selected':selected,'min_fill':baseline,'previous_learned':old_policy,'families':families},
            'incremental':{'initial_checks':len(gap.FAMILIES)*seeds,'updates':updates,'incremental_visits':incremental_visits,'full_visits':full_visits,'reused_buckets':reuse},
            'remaining_gates':{'REX-402':'physical machine not integrated','REX-403':'physical equivalence not proved','VER-603':'Lean kernel proof not run','OPT-703':'bounded fixed-order reuse demonstrated; general formal proof and performance open','RES-802':'external matched benchmarks not run','RES-803':'governed autonomous code generation not implemented'},
            'scope':'synthetic exact checks; logical counts exclude planning, cache keys, copying, oracle and other overhead; no general runtime claim',
            'source_sha256':{Path(p).name:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in (__file__,ref.__file__,gap.__file__,curriculum.__file__)}}
    result['evidence_sha256']=gap.digest(result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--seeds',type=int,default=12); p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); result=audit(a.seeds)
    with a.output.open('x') as f: json.dump(result,f,indent=2)
    print(json.dumps({k:v for k,v in result.items() if k!='dependency_schedule'},indent=2))
