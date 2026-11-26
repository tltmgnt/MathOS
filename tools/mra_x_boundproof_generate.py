"""Untrusted proof search. The independent checker is the acceptance boundary."""
import copy
import mra_x_boundproof as p


class NotProved(ValueError): pass


def generate(doc):
    problem=copy.deepcopy(doc['problem']); d,fs=p.problem(problem)
    c,groups=p.components(d,fs); optimum=doc['result']['optimum']; w=copy.deepcopy(doc['result']['witness'])
    budget=p.Budget(); proofs=[]
    def build(group,terms,target,partial):
        budget.node(); lower=budget.bound(terms,partial)
        if lower is None: return 0
        if target is not None and lower>=target: return 1
        rest=set(group)-set(partial)
        if not rest: raise NotProved('counterexample to claimed lower bound')
        v=min(rest,key=lambda v:(-sum(v in scope for scope,_ in terms),d[v],v))
        children=[]
        try:
            for x in range(d[v]):
                partial[v]=x; children.append(build(group,terms,target,partial))
        finally: del partial[v]
        return [v,children]
    if optimum is None:
        if p.score(c,{}) is not None:
            for i,(group,terms) in enumerate(groups):
                try: tree=build(group,terms,None,{})
                except NotProved: continue
                proofs=[[i,tree]]; break
            else: raise NotProved('no infeasible component')
    else:
        for i,(group,terms) in enumerate(groups):
            target=p.score(terms,w); p.require(target is not None)
            proofs.append([i,build(group,terms,target,{})])
    out=dict(schema=1,problem=problem,optimum=optimum,witness=w,proofs=proofs)
    p.require(len(p.canonical(out))<=p.MAX_BYTES)
    return out
