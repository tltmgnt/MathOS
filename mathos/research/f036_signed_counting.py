"""F036: signed Hall discovery with triangle-filtered capacity groups.

A sufficient UNSAT certificate, never a SAT decision on failure.
All ranks and graph groups are discovered from the raw CNF.
"""
from collections import deque
from itertools import combinations, product
from random import Random
from mathos.research.f036_counting_discovery import Certificate, pigeon


def check(f, cert):
    rows = [frozenset(c) for c in f]
    if any(0 in c for c in rows):
        return False
    original = set(rows)
    for i,j,p,c in cert.steps:
        if not (p and 0 <= i < len(rows) and 0 <= j < len(rows)):
            return False
        if p not in rows[i] or -p not in rows[j]:
            return False
        if frozenset(c) != (rows[i]-{p}) | (rows[j]-{-p}):
            return False
        rows.append(frozenset(c))
    used = set()
    for i in cert.demands:
        if not 0 <= i < len(rows):
            return False
        c = rows[i]
        if not c or used & c:
            return False
        used.update(c)
    covered = set()
    for g in cert.groups:
        if not g or 0 in g or len(set(g)) != len(g):
            return False
        if any(frozenset((-u,-v)) not in original for u,v in combinations(g,2)):
            return False
        covered.update(g)
    return used <= covered and len(cert.demands) > len(cert.groups)


def discover(f):
    original = [frozenset(c) for c in f]
    if any(0 in c for c in original):
        return None
    rows = list(original)
    graph = {}
    for c in original:
        if len(c) == 2:
            u,v = sorted(-l for l in c)
            graph.setdefault(u,set()).add(v)
            graph.setdefault(v,set()).add(u)
    # Retain edges lying in a triangle. Binary gate constraints and
    # isolated cross-clique bridges need not contaminate the groups.
    core = {u: {v for v in ns if ns & graph[v]}
            for u,ns in graph.items()}
    seen, groups, group_of = set(), [], {}
    for u in sorted(core):
        if u in seen or not core[u]:
            continue
        seen.add(u)
        todo, g = [u], []
        while todo:
            v = todo.pop()
            g.append(v)
            for w in sorted(core[v]):
                if w not in seen:
                    seen.add(w)
                    todo.append(w)
        g.sort()
        if not all(v == w or w in graph[v] for v in g for w in g):
            continue
        for v in g:
            group_of[v] = len(groups)
        groups.append(tuple(g))
    # Ground signed-literal implications in the discovered groups.
    # A new rank can use only literals from strictly earlier rounds.
    rank = {v:0 for v in group_of}
    rule = {}
    level = 0
    while True:
        new = {}
        for i,c in enumerate(original):
            if len(c) < 2:
                continue
            for l in sorted(c):
                p = -l
                if p not in rank and all(v in rank for v in c-{l}):
                    new.setdefault(p,i)
        if not new:
            break
        level += 1
        for p,i in new.items():
            rank[p] = level
            rule[p] = i
    steps, demands, used = [], [], set()
    for i in sorted(range(len(original)),key=lambda i:(len(original[i]),i)):
        c = original[i]
        if not c or any(v not in rank for v in c):
            continue
        index = i
        while any(rank[v] > 0 for v in c):
            p = max(c,key=lambda v:(rank[v],v))
            j = rule[p]
            c = (c-{p}) | (original[j]-{-p})
            steps.append((index,j,p,tuple(sorted(c))))
            index = len(rows)
            rows.append(c)
        if not used & c:
            demands.append(index)
            used.update(c)
    edges = [sorted({group_of[v] for v in rows[i]}) for i in demands]
    owner = {}
    for start in range(len(demands)):
        queue = deque([start])
        reach, via, incoming = {start}, {}, {}
        free = None
        while queue and free is None:
            i = queue.popleft()
            for g in edges[i]:
                if g in via:
                    continue
                via[g] = i
                if g not in owner:
                    free = g
                    break
                j = owner[g]
                if j not in reach:
                    reach.add(j)
                    incoming[j] = g
                    queue.append(j)
        if free is None:
            cert = Certificate(tuple(steps),tuple(demands[i] for i in sorted(reach)),
                               tuple(groups[g] for g in sorted(via)))
            assert check(f,cert)
            return cert
        g = free
        while True:
            i = via[g]
            owner[g] = i
            if i == start:
                break
            g = incoming[i]
    return None


def transform(f,rng):
    vs = sorted({abs(v) for c in f for v in c})
    perm = list(vs)
    rng.shuffle(perm)
    mp = {v:w*rng.choice((-1,1)) for v,w in zip(vs,perm)}
    g = [tuple(mp[abs(v)]*(1 if v>0 else -1) for v in c) for c in f]
    rng.shuffle(g)
    return g


def brute(f):
    vs = sorted({abs(v) for c in f for v in c})
    for bits in product((False,True),repeat=len(vs)):
        x = dict(zip(vs,bits))
        if all(any(x[abs(v)]==(v>0) for v in c) for c in f):
            return True
    return False


def run():
    rng = Random(3602)
    unsat = sat = bridges = accepted = 0
    for k in range(2,21):
        for j in range(3):
            f = pigeon(k+1,k)
            if j == 2:
                f.append((-1,-2))
                bridges += 1
            g = transform(f,rng)
            cert = discover(g)
            assert cert is not None and check(g,cert),(k,j)
            unsat += 1
        assert discover(transform(pigeon(k,k),rng)) is None
        sat += 1
    # Signed ground truth controls: never accept a satisfiable formula.
    for _ in range(512):
        f = [tuple(v*rng.choice((-1,1)) for v in
                   rng.sample(range(1,7),rng.randrange(1,4)))
             for _ in range(rng.randrange(1,30))]
        cert = discover(f)
        if cert is not None:
            assert check(f,cert) and not brute(f)
            accepted += 1
    assert discover([(1,),(-1,)]) is None
    print(f"random accepted={accepted}")
    print(f"F036_SIGNED_COUNTING_OK unsat={unsat} sat={sat} bridges={bridges} random=512 unknown=1")

if __name__=="__main__":
    run()
