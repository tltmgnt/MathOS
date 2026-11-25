"""F037: exact block-cut messages with a bounded backdoor in each block.

The primal graph is split at articulation variables. No assignment
enumeration across different blocks is required. UNKNOWN is preserved.
"""
from itertools import product
from mathos.research.f037_log_backdoor import normalize, decide, satisfies


def split_after(vertices, adj, removed):
    unseen = set(vertices) - {removed}
    parts = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        q = [root]
        for u in q:
            for v in sorted(adj[u] & unseen):
                unseen.remove(v)
                q.append(v)
        parts.append(frozenset(q))
    return parts


def decompose(f):
    adj = {}
    for c in f:
        vs = {abs(l) for l in c}
        for v in vs:
            adj.setdefault(v, set()).update(vs-{v})
    # Obtain connected nonempty pieces, including isolated vertices.
    pending = split_after(adj, adj, None)
    blocks = []
    while pending:
        s = pending.pop()
        if len(s) < 2:
            continue
        for a in sorted(s):
            parts = split_after(s, adj, a)
            if len(parts) > 1:
                pending.extend(p | {a} for p in parts)
                break
        else:
            blocks.append(s)
    # Each nonunit clause is a clique, hence lies in one block.
    rows = [[] for _ in blocks]
    unary = {v: {False,True} for v in adj}
    for c in f:
        if len(c) == 1:
            unary[abs(c[0])].intersection_update({c[0]>0})
        elif len(c) >= 2:
            vs = {abs(l) for l in c}
            owners = [i for i,b in enumerate(blocks) if vs<=b]
            assert len(owners)==1
            rows[owners[0]].append(c)
    return adj, blocks, rows, unary


def solve(raw,k):
    raw = tuple(tuple(c) for c in raw)
    f = normalize(raw)
    if () in f:
        return 'UNSAT',None
    if any(len(c)>3 for c in f):
        return 'UNKNOWN',None
    adj,blocks,rows,unary=decompose(f)
    # Variable nodes are positive integer IDs; block nodes are
    # negative IDs. Include all variables, not only articulation ones.
    tree={v:[] for v in adj}
    for i,s in enumerate(blocks):
        b=-i-1
        tree[b]=sorted(s)
        for v in s:
            tree[v].append(b)
    domain, local_model, seen, roots, parent = {}, {}, set(), [], {}
    for root in sorted(adj):
        if root in seen:
            continue
        roots.append(root)
        order=[root]
        seen.add(root)
        parent[root]=None
        for u in order:
            for v in tree[u]:
                if v==parent[u]:
                    continue
                assert v not in seen, "block incidence must be a forest"
                seen.add(v)
                parent[v]=u
                order.append(v)
        for u in reversed(order):
            children=[v for v in tree[u] if v!=parent[u]]
            if u>0:
                allowed=set(unary[u])
                for child in children:
                    allowed.intersection_update(domain[child])
                domain[u]=allowed
                continue
            # Block -> parent variable message. Child messages are
            # exact allowed-value sets, enforced as unary constraints.
            allowed=set()
            if all(domain[v] for v in children):
                g=tuple(rows[-u-1])+tuple(
                    (v if True in domain[v] else -v,)
                    for v in children if len(domain[v])==1)
                p=parent[u]
                for bit in (False,True):
                    result,evidence=decide(g+((p if bit else -p,),),k)
                    if result=='UNKNOWN':
                        return 'UNKNOWN',None
                    if result=='SAT':
                        allowed.add(bit)
                        local_model[u,bit]=evidence
            domain[u]=allowed
        if not domain[root]:
            return 'UNSAT',None
    # Reconstruct a model by choosing an allowed root value and
    # propagating local witness assignments down the block tree.
    x={}
    for root in roots:
        x[root]=min(domain[root])
        q=[root]
        for u in q:
            for v in tree[u]:
                if v==parent[u]:
                    continue
                q.append(v)
                if u<0:
                    witness=local_model[u,x[parent[u]]]
                    x[v]=witness.get(v,False)
                    assert x[v] in domain[v]
    assert satisfies(raw,x)
    return 'SAT',x


def chain(t):
    triples=[(3*i+1,3*i+2,3*i+3) for i in range(t)]
    bridges=[(3*i+1,3*(i+1)+1) for i in range(t-1)]
    return tuple(triples+bridges)


def run():
    rows=((),(1,),(-1,),(2,3),(1,-1),(1,1,1),
          (-1,-2,-3),(-1,-2,3),(1,2,-3),(1,2,3),(2,1),(1,2))
    counts={}
    for m in range(1<<len(rows)):
        f=tuple(c for j,c in enumerate(rows) if m&(1<<j))
        sat=any(satisfies(f,dict(zip((1,2,3),bits)))
                for bits in product((False,True),repeat=3))
        status,x=solve(f,1)
        assert status==('SAT' if sat else 'UNSAT')
        if sat:
            assert satisfies(f,x)
        counts[status]=counts.get(status,0)+1
    assert counts=={'SAT':1280,'UNSAT':2816}
    for t in (2,4,8,16,32,64,128):
        f=chain(t)
        assert decide(f,1)[0]=='UNKNOWN'
        status,x=solve(f,1)
        assert status=='SAT' and satisfies(f,x)
        assert solve(f,0)[0]=='UNKNOWN'
    # Two disjoint ternary blocks share variable 1 and require
    # opposite values. Each block alone is satisfiable.
    a=tuple((1,i*2,j*3) for i,j in product((-1,1),repeat=2))
    b=tuple((-1,i*4,j*5) for i,j in product((-1,1),repeat=2))
    assert solve(a,1)[0]=='SAT' and solve(b,1)[0]=='SAT'
    assert solve(a+b,1)[0]=='UNSAT'
    # Sparse identifiers, isolated units and tautology controls.
    assert solve(((10**12,),(-10**12,)),0)[0]=='UNSAT'
    assert solve(((10**12,),(-7,7)),0)[0]=='SAT'
    print('F037_BLOCK_BACKDOOR_OK formulas=4096 chains=7 max_blocks=255 articulation_conflict=1 sparse=2')


if __name__=='__main__':
    run()
