"""Metered signed Hall obstruction in a subsystem; never claims SAT.
A selected set of disjoint required clauses and a clique partition are
sufficient for UNSAT even if other clauses are arbitrary.
"""
from collections import deque
from .pnp_bounded_matching import Meter, Limit, normalize, order, check


def propose(n, f, b):
    known = normalize(n, f, b)
    candidates = []
    for c in known:
        b.tick()
        if len(c) >= 3:
            candidates.append(order(c, b))
    b.tick(1 + sum(map(len, candidates)) * max(1, len(candidates).bit_length()))
    candidates.sort(key=lambda c: (len(c), c))
    groups, owner = [], {}
    for g in candidates:
        b.tick(1 + len(g))
        if any(abs(x) in owner for x in g):
            continue
        i = len(groups); groups.append(g)
        for x in g:
            owner[abs(x)] = i
    if len(groups) < 2:
        return None
    graph = {x: set() for g in groups for x in g}
    b.tick(1 + len(graph))
    for c in known:
        b.tick()
        if len(c) == 2:
            a, z = c
            if -a in graph and -z in graph:
                graph[-a].add(-z); graph[-z].add(-a)
    # Deterministic greedy clique partition; extra edges between buckets
    # are ignored, never used as evidence of a missing conflict.
    buckets, location = [], {}
    for x in order(graph, b):
        b.tick()
        if x in location:
            continue
        bucket = [x]; i = len(buckets); location[x] = i
        for y in order(graph[x], b):
            b.tick()
            if y in location:
                continue
            b.tick(len(bucket))
            if all(z in graph[y] for z in bucket):
                location[y] = i; bucket.append(y)
        buckets.append(bucket)
    adj = []
    for g in groups:
        b.tick(1 + len(g)); adj.append(order({location[x] for x in g}, b))
    left, right = {}, {}
    for root in range(len(groups)):
        b.tick(); seen = {root}; pred = {}; queue = deque([root]); end = None
        while queue and end is None:
            i = queue.popleft(); b.tick()
            for j in adj[i]:
                b.tick()
                if j in pred:
                    continue
                pred[j] = i
                if j not in right:
                    end = j; break
                k = right[j]
                if k not in seen:
                    seen.add(k); queue.append(k)
        if end is None:
            sel = [groups[i] for i in order(seen, b)]
            b.tick(1 + sum(map(len, sel)))
            lits = {x for g in sel for x in g}; bs = []
            for j in order(pred, b):
                b.tick(1 + len(buckets[j])); bs.append([x for x in buckets[j] if x in lits])
            return {'decision':'unsat', 'groups':sel, 'buckets':bs}
        while end is not None:
            b.tick(); i = pred[end]; old = left.get(i)
            left[i] = end; right[end] = i; end = old
    return None


def solve(n, f, *, steps=25_000, seconds=1.25):
    b = Meter(steps, seconds)
    try:
        c = propose(n, f, b)
        if c is None:
            return {'decision':'unknown','status':'not_found','work_steps':b.used,'certificate':None}
        check(n, f, c, b)
        return {'decision':'unsat','status':'verified','work_steps':b.used,'certificate':c}
    except Limit:
        return {'decision':'unknown','status':'resource_exhausted','work_steps':steps,'certificate':None}


def replay(n, f, r, *, steps=25_000):
    if set(r) != {'decision','status','work_steps','certificate'}:
        raise ValueError('report fields')
    w, c = r['work_steps'], r['certificate']
    if type(w) is not int or not 0 <= w <= steps:
        raise ValueError('work envelope')
    if r['status'] == 'verified':
        if r['decision'] != 'unsat' or not isinstance(c,dict) or c['decision'] != 'unsat':
            raise ValueError('decision mismatch')
        check(n,f,c,Meter(max(1,w),15))
    elif (r['status'] not in ('not_found','resource_exhausted') or r['decision'] != 'unknown' or c is not None
          or (r['status']=='resource_exhausted' and w != steps)):
        raise ValueError('uncredited result')
    return True
