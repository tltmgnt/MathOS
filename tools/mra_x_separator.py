"""Phase VIII: recursive separator messages and content-keyed subtree reuse."""
import argparse
import copy
import itertools
import hashlib
import json
import random
from pathlib import Path
import mra_x_topology as ref
import mra_x_certify as cert
import mra_x_upgrade as up
import mra_x_gap_agent as gap
from mra_x_frontier import highs


def components(g, vertices):
    unseen=set(vertices); out=[]
    while unseen:
        stack=[min(unseen)]; group=set()
        while stack:
            v=stack.pop()
            if v in unseen:
                unseen.remove(v); group.add(v); stack.extend(g[v]&unseen)
        out.append(group)
    return out


def tree(g, vertices):
    vs=sorted(vertices); parts=components(g,vs)
    if len(parts)>1: return ((),tuple(tree(g,p) for p in parts))
    if len(vs)<=4: return (tuple(vs),())
    for k in (1,2):
        best=None
        for s in itertools.combinations(vs,k):
            groups=components(g,set(vs)-set(s))
            if len(groups)>1:
                key=(max(map(len,groups)),s)
                if best is None or key<best[0]: best=(key,groups)
        if best is not None: return (best[0][1],tuple(tree(g,p) for p in best[1]))
    return (tuple(vs),())


def order(node):
    own,children=node
    return [v for c in children for v in order(c)]+list(own)


def shape(node):
    own,children=node
    sub=[shape(c) for c in children]
    return (1+sum(x[0] for x in sub),1+max((x[1] for x in sub),default=0),max([len(own) if children else 0]+[x[2] for x in sub]))


class Engine:
    def __init__(self,d,f,budget=1000000):
        ref.validate(d,f)
        if len(d)>128 or any(not isinstance(v,str) or k>4 for v,k in d.items()) or len(f)>1024: raise ValueError('envelope')
        self.d=dict(d); self.scopes=tuple(s for s,_ in f); self.tree=tree(cert.graph(d,f),d); self.order=order(self.tree)
        self.predicted,self.width=up.predict(d,f,self.order)
        if not 1<=budget<=10000000 or self.predicted>budget: raise ValueError('enumeration budget')
        self.cache={}

    def solve(self,f):
        d=self.d; ref.validate(d,f)
        if tuple(s for s,_ in f)!=self.scopes: raise ValueError('scope edits require replanning')
        hits=work=0; next_cache={}
        def visit(node,fs):
            nonlocal hits,work
            key=tuple((s,tuple(sorted(t.items()))) for s,t in fs)
            if node in self.cache and self.cache[node][0]==key:
                hits+=1; item=self.cache[node]; next_cache[node]=item
                # Preserve descendant entries for future partial edits.
                def retain(n):
                    for child in n[1]:
                        if child in self.cache: next_cache[child]=self.cache[child]
                        retain(child)
                retain(node)
                return item[1],item[2]
            own,children=node; active=list(fs); trace=[]
            for child in children:
                private=set(order(child)); selected=[(s,t) for s,t in active if private.intersection(s)]
                active=[(s,t) for s,t in active if not private.intersection(s)]
                msg,tr=visit(child,selected); active.extend(msg); trace.extend(tr)
            for v in own:
                bucket=[(s,t) for s,t in active if v in s]; active=[(s,t) for s,t in active if v not in s]
                boundary=tuple(sorted({u for s,_ in bucket for u in s}-{v})); table={}; rows=[]
                for row in ref.assignments(d,boundary):
                    a=dict(zip(boundary,row)); best=arg=None
                    for x in range(d[v]):
                        a[v]=x; work+=1; value=ref.score(bucket,a)
                        if value is not None and (best is None or value<best): best,arg=value,x
                    if best is not None: table[row]=best; rows.append([list(row),arg])
                active.append((boundary,table)); trace.append([v,list(boundary),rows])
            next_cache[node]=(key,active,trace); return active,trace
        messages,trace=visit(self.tree,[(tuple(s),dict(t)) for s,t in f]); optimum=ref.score(messages,{})
        result=dict(optimum=optimum,witness=None if optimum is None else ref.recover(trace),trace=copy.deepcopy(trace),order=self.order[:],induced_width=self.width,assignments_evaluated=self.predicted)
        self.cache=next_cache
        return result,dict(actual_visits=work,subtree_hits=hits)


def instance(seed,n,kind):
    rng=random.Random(seed); vs=[f'{i:03d}' for i in range(n)]; d={v:rng.randint(2,3) for v in vs}; target={v:rng.randrange(d[v]) for v in vs}
    scopes=[(vs[i],vs[i+1]) for i in range(n-1)]
    if kind=='cycle': scopes.append((vs[-1],vs[0]))
    if kind=='triangles': scopes.extend(tuple(vs[i:i+3]) for i in range(0,n-2,2))
    f=[]
    for s in scopes:
        t={a:rng.randint(-5,8) for a in ref.assignments(d,s) if rng.random()<.8}; t.setdefault(tuple(target[v] for v in s),0); f.append((s,t))
    f.append(((),{():-2})); return d,f


def audit():
    rows=[]; controls=0
    for i,kind in enumerate(('chain','cycle','triangles')):
        for trial,n in enumerate((8,16,32,64)):
            d,f=instance(8100+i*10+trial,n,kind); e=Engine(d,f); r,stats=e.solve(f); assert cert.verify_solution(d,f,r)==e.predicted
            h,w,_=highs(d,f); assert h==r['optimum'] and ref.score(f,w)==h
            if n==8: assert ref.brute(d,f)==h
            base=ref.solve(d,f); assert base['optimum']==h
            flat=up.Incremental(d,e.order); flat.solve(f)
            flat_min=up.Incremental(d,base['order']); flat_min.solve(f)
            updates=actual=full=hits=flat_work=flat_min_work=0
            for changed in ([ (f[0][0],{}) ]+f[1:],f,f[:-1]+[((),{})],f,f):
                x,s=e.solve(changed); fresh=ref.solve(d,changed,e.order); assert x==fresh and cert.verify_solution(d,changed,x)==e.predicted
                a=flat.solve(changed); b=flat_min.solve(changed); assert a['optimum']==b['optimum']==x['optimum']
                flat_work+=a['assignments_evaluated']; flat_min_work+=b['assignments_evaluated']
                actual+=s['actual_visits']; hits+=s['subtree_hits']; full+=e.predicted; updates+=1
            assert s['actual_visits']==0
            rows.append(dict(kind=kind,n=n,nodes=shape(e.tree)[0],depth=shape(e.tree)[1],max_separator=shape(e.tree)[2],width=e.width,visits=e.predicted,min_fill=base['assignments_evaluated'],updates=updates,actual=actual,full=full,hits=hits,flat_same_order=flat_work,flat_min_fill=flat_min_work))
    d,f=instance(8199,8,'cycle'); e=Engine(d,f)
    for fn in (lambda: e.solve(f[1:]),lambda: Engine(d,f,1)):
        try: fn()
        except ValueError: controls+=1
        else: raise AssertionError('invalid input accepted')
    # Scope edits can be solved after a new plan is built.
    f=f+[(('000','004'),{(0,0):0})]; r,_=Engine(d,f).solve(f); assert r['optimum']==ref.brute(d,f); controls+=1
    for d,f in (({},[]),({},[((),{})]),({'x':2},[])):
        r,_=Engine(d,f).solve(f); assert r==ref.solve(d,f); controls+=1
    out={'rows':rows,'controls':controls,'source_sha256':{Path(p).name:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in (__file__,ref.__file__,cert.__file__,up.__file__,gap.__file__,__import__('mra_x_frontier').__file__)},'scope':'bounded recursive separators of width 1–2; leaves may be larger; exact solution trace, not globally optimal order; cache counts exclude overhead; no mechanized proof'}; out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); r=audit()
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps(r,indent=2))
