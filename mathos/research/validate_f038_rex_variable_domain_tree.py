"""REX-013: independent finite relational replay of variable-domain trees."""
import json
import sys
from itertools import product

if __package__:
    from .finite_relational_elimination import Factor, Solver
else:
    from finite_relational_elimination import Factor, Solver


def leaf(u, e):
    return [u, e, []]


def root(u, children):
    return [u, [], children]


def bits(x, n):
    return [(x >> i) & 1 for i in range(n)]


def fixtures():
    for m in range(1, 5):
        for x in range(2**m):
            yield root(bits(x, m), [])
    for m, n in ((1,1),(1,2),(2,1),(1,3),(3,1),(2,2)):
        for x in range(2**(m+n+m*n)):
            b = bits(x, m+n+m*n)
            yield root(b[:m], [leaf(b[m:m+n], [b[m+n+j*n:m+n+(j+1)*n] for j in range(m)])])
    for x, y in product(range(8), repeat=2):
        yield root([1,1,1], [leaf([1], [[b] for b in bits(x,3)]), leaf([1], [[b] for b in bits(y,3)])])
    seed = 0x52455813
    def rand():
        nonlocal seed
        seed = (1664525*seed+1013904223)&0xffffffff
        return seed
    for i in range(32):
        n = 3+i%4
        nodes, parents = [], [-1]
        for j in range(n):
            d = 1+(rand() >> 28)%3
            u = [rand() >> 31 for _ in range(d)]
            p = (rand() >> 16)%j if j else -1
            if j:
                parents.append(p)
            e = [] if p < 0 else [[rand() >> 31 for _ in range(d)] for _ in nodes[p][0]]
            nodes.append(leaf(u,e))
            if j:
                nodes[p][2].append(nodes[j])
        if i%2:
            a = [(rand() >> 16)%len(v[0]) for v in nodes]
            for j in range(n):
                nodes[j][0][a[j]] = 1
                if j:
                    nodes[j][1][a[parents[j]]][a[j]] = 1
        yield nodes[0]
    yield root([1,1], [leaf([1],[[1],[0]]),leaf([1],[[0],[1]])])
    yield root([1,1,1], [[[1,1],[[0,0],[0,0],[0,1]],[leaf([0,0,1],[[0,0,0],[0,0,1]])]],leaf([1],[[0],[0],[1]])])


def encode(t):
    u,e,children = t
    def b(x):
        return '0'+str(x)
    return '10'+''.join(map(b,u))+'11'+''.join(''.join(map(b,c))+'10' for c in e)+'11'+''.join(map(encode,children))+'11'


def flatten(t):
    nodes = []
    def visit(t,p):
        i = len(nodes)
        nodes.append((t[0],t[1],p))
        for c in t[2]:
            visit(c,i)
    visit(t,-1)
    return nodes


def audit():
    digest = 2166136261
    cases = sat = stages = candidates = projected = 0
    for t in fixtures():
        nodes = flatten(t)
        n = len(nodes)
        names = tuple(map(str,range(n)))
        domains = {v: tuple(range(len(nodes[i][0]))) for i,v in enumerate(names)}
        fs = [Factor((names[i],),tuple((a,) for a,x in enumerate(u) if x)) for i,(u,e,p) in enumerate(nodes)]
        fs += [Factor((names[p],names[i]),tuple((b,a) for b,col in enumerate(e) for a,x in enumerate(col) if x)) for i,(u,e,p) in enumerate(nodes) if p>=0]
        models = [a for a in product(*domains.values()) if all(u[a[i]] and (p<0 or e[a[p]][a[i]]) for i,(u,e,p) in enumerate(nodes))]
        s = Solver(domains,batch_size=2)
        state = s.initial_state(fs)
        for i in reversed(range(n)):
            state,trace = s.stage(state,names[i])
            expected = tuple(sorted({a[:i] for a in models}))
            assert s.relation(state).rows == expected
            p = nodes[i][2]
            assert trace.candidate_count == len(nodes[i][0])*(len(nodes[p][0]) if p>=0 else 1)
            stages += 1
            candidates += trace.candidate_count
            projected += len(expected)
        assert bool(s.relation(state).rows) == bool(models)
        a = min(models) if models else None
        witness = '-' if a is None else ''.join(str(int(j==a[i])) for i,(u,e,p) in enumerate(nodes) for j in range(len(u)))
        for ch in encode(t)+':'+witness+';':
            digest = ((digest^ord(ch))*16777619)&0xffffffff
        cases += 1
        sat += bool(models)
    return dict(cases=cases,sat=sat,unsat=cases-sat,stages=stages,candidates=candidates,projected=projected,digest=digest)


if __name__ == '__main__':
    result = audit()
    assert result['digest'] == 2490725291
    if len(sys.argv)>1:
        with open(sys.argv[1]) as f:
            physical = json.load(f)
        assert physical['digest']==result['digest']
        assert (physical['counts']['valid'],physical['counts']['sat'],physical['counts']['unsat'])==(result['cases'],result['sat'],result['unsat'])
    print('REX_VARIABLE_DOMAIN_TREE_REFERENCE_OK '+json.dumps(result,separators=(',',':')))
