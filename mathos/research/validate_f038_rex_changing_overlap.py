"""REX-017: independent global-variable and finite relational replay."""
import json
import sys
from itertools import product
if __package__:
    from .finite_relational_elimination import Factor, Solver
else:
    from finite_relational_elimination import Factor, Solver

PAIRS = ((0, 1), (0, 2), (1, 2))


def node(k, x, children=None):
    return [k, [(x >> i) & 1 for i in range(8)], [] if children is None else children]


def fixtures():
    for x in range(256):
        yield node(3, x), x % 51 == 0
    for k in range(3):
        for x in range(256):
            yield node(3, 255, [node(k, x)]), x % 85 == 0
    yield node(3, 255, [node(0, 195), node(1, 195), node(2, 60)]), True
    yield node(3, 32, [node(1, 64, [node(2, 32)]), node(0, 32)]), True
    seed = 0x52455817

    def rand():
        nonlocal seed
        seed = (1664525 * seed + 1013904223) & 0xffffffff
        return seed

    def plant(t, j):
        t[1][j] = 1
        d = ((j >> 2) & 1, (j >> 1) & 1, j & 1)
        for child in t[2]:
            x, y = PAIRS[child[0]]
            plant(child, 4*d[x]+2*d[y]+(rand() >> 31))

    for i in range(48):
        n = 3+i%5
        nodes = [node(3, rand() >> 24)]
        for j in range(1, n):
            k = (rand() >> 16)%3
            p = (rand() >> 16)%j
            nodes.append(node(k, rand() >> 24))
            nodes[p][2].append(nodes[j])
        if i%2:
            plant(nodes[0], rand() >> 29)
        yield nodes[0], i < 8


def encode(t):
    k, mask, children = t
    return '10'+'0'+str(k >> 1)+'0'+str(k & 1)+''.join('0'+str(b) for b in mask)+''.join(map(encode, children))+'11'


def flatten(t):
    bags = []
    n = 3

    def visit(t, scope):
        nonlocal n
        bags.append((scope, t[1]))
        for child in t[2]:
            i, j = PAIRS[child[0]]
            v = n
            n += 1
            visit(child, (scope[i], scope[j], v))

    visit(t, (0, 1, 2))
    return bags, n


def audit():
    cases = sat = physical_cases = physical_sat = stages = candidates = projected = 0
    digest = physical_digest = 2166136261
    for t, physical in fixtures():
        bags, n = flatten(t)
        names = tuple(map(str, range(n)))
        domains = {v: (0, 1) for v in names}
        fs = [Factor(tuple(names[i] for i in scope), tuple(row for j, row in enumerate(product(range(2), repeat=3)) if mask[j])) for scope, mask in bags]
        models = [a for a in product(range(2), repeat=n) if all(mask[4*a[s[0]]+2*a[s[1]]+a[s[2]]] for s, mask in bags)]
        solver = Solver(domains, batch_size=2)
        state = solver.initial_state(fs)
        for j in reversed(range(n)):
            state, trace = solver.stage(state, names[j])
            expected = tuple(sorted({a[:j] for a in models}))
            assert solver.relation(state).rows == expected
            assert trace.candidate_count == (8 if j >= 2 else 4 if j == 1 else 2)
            stages += 1
            candidates += trace.candidate_count
            projected += len(expected)
        assert bool(solver.relation(state).rows) == bool(models)
        witness = ''.join(map(str, min(models))) if models else '-'
        for ch in encode(t)+':'+witness+';':
            digest = ((digest ^ ord(ch))*16777619)&0xffffffff
            if physical:
                physical_digest = ((physical_digest ^ ord(ch))*16777619)&0xffffffff
        cases += 1
        sat += bool(models)
        physical_cases += physical
        physical_sat += physical and bool(models)
    return dict(cases=cases, sat=sat, unsat=cases-sat, physical_cases=physical_cases, physical_sat=physical_sat, stages=stages, candidates=candidates, projected=projected, digest=digest, physicalDigest=physical_digest)


if __name__ == '__main__':
    r = audit()
    assert (r['digest'], r['physicalDigest']) == (3514280781, 2515706306)
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            p = json.load(f)
        assert (p['digest'], p['physicalDigest']) == (r['digest'], r['physicalDigest'])
        assert (p['counts']['logicalCases'], p['counts']['physicalCases'], p['counts']['sat'], p['counts']['physicalSat']) == (r['cases'], r['physical_cases'], r['sat'], r['physical_sat'])
    print('REX_CHANGING_OVERLAP_REFERENCE_OK '+json.dumps(r,separators=(',',':')))
