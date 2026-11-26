"""REX-012: independent Python finite relational and predicate replay."""
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
    return [u, [1, 1, 1, 1], children]


def bits(x, n):
    return [(x >> i) & 1 for i in range(n)]


def fixtures():
    for u in range(4):
        yield root(bits(u, 2), [])
    for u, v, e in product(range(4), range(4), range(16)):
        yield root(bits(u, 2), [leaf(bits(v, 2), bits(e, 4))])
    for a, b in product(range(16), repeat=2):
        yield root([1, 1], [leaf([1, 1], bits(a, 4)), leaf([1, 1], bits(b, 4))])
    seed = 0x52455812

    def rand():
        nonlocal seed
        seed = (1664525 * seed + 1013904223) & 0xffffffff
        return seed

    for i in range(64):
        n = 3 + i % 6
        nodes = [leaf(bits(rand() >> 16, 2), bits(rand() >> 16, 4)) for _ in range(n)]
        parents = [-1]
        for j in range(1, n):
            p = (rand() >> 16) % j
            parents.append(p)
            nodes[p][2].append(nodes[j])
        if i % 2:
            a = [rand() >> 31 for _ in nodes]
            for j in range(n):
                nodes[j][0][a[j]] = 1
                if j:
                    nodes[j][1][2*a[j]+a[parents[j]]] = 1
        yield nodes[0]
    yield root([1, 1], [leaf([1, 0], [1, 0, 0, 0]), leaf([0, 1], [0, 0, 0, 1])])
    yield root([1, 1], [leaf([1, 0], [0, 1, 0, 0]), leaf([0, 1], [0, 0, 0, 1])])


def encode(t):
    u, e, children = t
    return '10' + ''.join('0'+str(b) for b in u+e) + ''.join(map(encode, children)) + '11'


def flatten(t):
    nodes = []
    def visit(t, p):
        u, e, children = t
        i = len(nodes)
        nodes.append((u, e, p))
        for c in children:
            visit(c, i)
    visit(t, -1)
    return nodes


def audit():
    cases = sat = stages = candidates = projected = 0
    digest = 2166136261
    for t in fixtures():
        nodes = flatten(t)
        n = len(nodes)
        names = tuple(map(str, range(n)))
        domains = {v: (0, 1) for v in names}
        fs = [Factor((names[i],), tuple((b,) for b in range(2) if u[b]))
              for i, (u, e, p) in enumerate(nodes)]
        fs += [Factor((names[i], names[p]), tuple((a,b) for a,b in product(range(2), repeat=2) if e[2*a+b]))
               for i, (u, e, p) in enumerate(nodes) if p >= 0]
        models = [a for a in product(range(2), repeat=n)
                  if all(u[a[i]] and (p < 0 or e[2*a[i]+a[p]])
                         for i, (u, e, p) in enumerate(nodes))]
        s = Solver(domains, batch_size=2)
        state = s.initial_state(fs)
        for i in reversed(range(n)):
            state, trace = s.stage(state, names[i])
            expected = tuple(sorted({a[:i] for a in models}))
            assert s.relation(state).rows == expected
            assert trace.candidate_count == (4 if i else 2)
            stages += 1
            candidates += trace.candidate_count
            projected += len(expected)
        assert bool(s.relation(state).rows) == bool(models)
        witness = ''.join(map(str, min(models))) if models else '-'
        for ch in encode(t)+':'+witness+';':
            digest = ((digest ^ ord(ch))*16777619)&0xffffffff
        cases += 1
        sat += bool(models)
    return dict(cases=cases,sat=sat,unsat=cases-sat,stages=stages,candidates=candidates,projected=projected,digest=digest)


if __name__ == '__main__':
    result = audit()
    assert result['digest'] == 3381327392
    if len(sys.argv)>1:
        with open(sys.argv[1]) as f:
            physical = json.load(f)
        assert physical['digest'] == result['digest']
        assert (physical['counts']['valid'],physical['counts']['sat'],physical['counts']['unsat']) == (result['cases'],result['sat'],result['unsat'])
    print('REX_BRANCHING_TREE_REFERENCE_OK '+json.dumps(result,separators=(',',':')))
