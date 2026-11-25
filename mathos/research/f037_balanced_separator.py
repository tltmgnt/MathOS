"""Balanced constant-size separators with logarithmic leaf backdoors.

This is a promise solver, not an unrestricted polynomial SAT algorithm.
Plan construction is independent of truth assignments; no exponential
backtracking over possible decompositions. Reuse checked 2-CNF leaves.
"""
from dataclasses import dataclass
from itertools import combinations, product
from mathos.research.f037_log_backdoor import normalize, hit, restrict, decide, satisfies


@dataclass(frozen=True)
class Plan:
    region: tuple
    separator: tuple
    children: tuple


def parts(vertices, adj, separator):
    unseen=set(vertices)-set(separator)
    out=[]
    while unseen:
        u=min(unseen)
        unseen.remove(u)
        q=[u]
        for v in q:
            for w in sorted(adj[v]&unseen):
                unseen.remove(w)
                q.append(w)
        out.append(tuple(sorted(q)))
    return tuple(out)


def build(f,k,s):
    # The structural graph is built before any assignment.
    adj={}
    for c in f:
        vs={abs(l) for l in c}
        for v in vs:
            adj.setdefault(v,set()).update(vs-{v})

    def visit(region,rows):
        # rows are projected structural supports, not semantic residuals.
        if hit(tuple(c for c in rows if len(c)==3),k) is not None:
            return Plan(region,(),())
        best=None
        for size in range(min(s,len(region))+1):
            for sep in combinations(region,size):
                ps=parts(region,adj,sep)
                maximum=max(map(len,ps),default=0)
                if 3*maximum>2*len(region):
                    continue
                key=(maximum,size,sep)
                if best is None or key<best[0]:
                    best=(key,ps)
        if best is None:
            return None
        (_,_,sep),ps=best
        remaining=[tuple(l for l in c if abs(l) not in sep) for c in rows]
        children=[]
        for p in ps:
            scope=set(p)
            child_rows=tuple(c for c in remaining if c and abs(c[0]) in scope)
            assert all(all(abs(l) in scope for l in c) for c in child_rows)
            child=visit(p,child_rows)
            if child is None:
                return None
            children.append(child)
        return Plan(region,sep,tuple(children))

    return visit(tuple(sorted(adj)),f)


def evaluate(plan,f,k):
    if () in f:
        return 'UNSAT',None
    if not plan.children and not plan.separator:
        return decide(f,k)
    for bits in product((False,True),repeat=len(plan.separator)):
        fixed=dict(zip(plan.separator,bits))
        g=restrict(f,fixed)
        if () in g:
            continue
        model=dict(fixed)
        for child in plan.children:
            scope=set(child.region)
            h=tuple(c for c in g if abs(c[0]) in scope)
            assert all(all(abs(l) in scope for l in c) for c in h)
            status,evidence=evaluate(child,h,k)
            if status=='UNKNOWN':
                return 'UNKNOWN',None
            if status=='UNSAT':
                break
            model.update(evidence)
        else:
            assert satisfies(f,model)
            return 'SAT',model
    return 'UNSAT',None


def solve(raw,k,s=2):
    assert k>=0 and s>=0
    raw=tuple(tuple(c) for c in raw)
    f=normalize(raw)
    if () in f:
        return 'UNSAT',None
    if any(len(c)>3 for c in f):
        return 'UNKNOWN',None
    plan=build(f,k,s)
    if plan is None:
        return 'UNKNOWN',None
    status,x=evaluate(plan,f,k)
    if status=='SAT':
        assert satisfies(raw,x)
    return status,x


def ladder(t):
    triples=[(3*i+1,3*i+2,3*i+3) for i in range(t)]
    links=[(3*i+j,3*(i+1)+j) for i in range(t-1) for j in (1,2)]
    return tuple(triples+links)


def stats(plan):
    return (1+sum(stats(c)[0] for c in plan.children),
            max((1+stats(c)[1] for c in plan.children),default=0))


def run():
    from mathos.research.f037_block_backdoor import solve as block_solve
    rows=((),(1,),(-1,),(2,3),(1,-1),(1,1,1),
          (-1,-2,-3),(-1,-2,3),(1,2,-3),(1,2,3),(2,1),(1,2))
    for mask in range(1<<len(rows)):
        f=tuple(c for i,c in enumerate(rows) if mask&(1<<i))
        sat=any(satisfies(f,dict(zip((1,2,3),bits)))
                for bits in product((False,True),repeat=3))
        status,x=solve(f,1)
        assert status==('SAT' if sat else 'UNSAT')
        if sat:
            assert satisfies(f,x)
    for t in (2,4,8,16,32,64):
        f=ladder(t)
        assert block_solve(f,1)[0]=='UNKNOWN'
        status,x=solve(f,1)
        assert status=='SAT' and satisfies(f,x)
        plan=build(normalize(f),1,2)
        nodes,depth=stats(plan)
        assert depth<=len(f).bit_length()*2
        print(f'ladder={t} nodes={nodes} depth={depth}')
    # Two nonunit regions communicate via a two-variable separator.
    # Left forces (1 or 2); right forces both false. Every original
    # clause contains a local variable so unit preprocessing alone
    # does not expose the contradiction.
    f=((1,2,3),(1,2,-3),(-1,4),(-1,-4),(-2,5),(-2,-5))
    assert solve(f,0,2)[0]=='UNSAT'
    assert solve(f,0,0)[0]=='UNKNOWN'
    # Force actual evaluation of many separator assignments on a ladder.
    f=ladder(8)+((-1,),(-2,),(-3,))
    assert solve(f,1)[0]=='UNSAT'
    print('F037_BALANCED_SEPARATOR_OK formulas=4096 ladders=6 max_variables=192 interface_conflict=1 rejection=1 ladder_unsat=1')


if __name__=='__main__':
    run()
