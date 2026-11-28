"""Bounded signed matching-CNF route. No unrestricted SAT claim.
Metered units are explicit algorithmic operations, not CPU instructions.
"""
from collections import deque
from itertools import combinations
import math
import time


class Limit(RuntimeError):
    pass


class Meter:
    def __init__(self, steps, seconds):
        if type(steps) is not int or not 1 <= steps <= 2_000_000:
            raise ValueError('step allowance')
        if type(seconds) not in (int, float) or not math.isfinite(seconds) or not 0 < seconds <= 60:
            raise ValueError('time allowance')
        self.limit = steps
        self.used = 0
        self.deadline = time.monotonic() + seconds

    def tick(self, k=1):
        if self.used + k > self.limit or time.monotonic() >= self.deadline:
            raise Limit('matching resource limit')
        self.used += k


def order(xs, b):
    # Charge a deterministic comparison-sort proxy before the sort.
    b.tick(1 + len(xs) * max(1, len(xs).bit_length()))
    return sorted(xs)


def normalize(n, f, b):
    if type(n) is not int or n < 0 or not isinstance(f, (list, tuple)):
        raise ValueError('input shape')
    if n > 512 or len(f) > 20_000:
        raise Limit('input dimensions')
    b.tick(1 + n + len(f))
    out = set()
    literals = 0
    for c in f:
        if not isinstance(c, (list, tuple)):
            raise ValueError('clause shape')
        literals += len(c)
        if literals > 100_000:
            raise Limit('literal cap')
        b.tick(1 + 3 * len(c))
        if any(type(x) is not int or not 0 < abs(x) <= n for x in c):
            raise ValueError('literal range')
        s = frozenset(c)
        if not any(-x in s for x in s):
            out.add(s)
    return out


def check(n, f, r, b):
    """Independent direct model or explicit Hall witness check, metered."""
    known = normalize(n, f, b)
    d = r['decision']
    if d == 'sat':
        if set(r) != {'decision', 'model'}:
            raise ValueError('model fields')
        a = r['model']
        b.tick(1 + len(a))
        if len(a) != n or any(type(x) is not bool for x in a):
            raise ValueError('invalid model')
        for c in known:
            b.tick(1 + len(c))
            if not any(a[abs(x)-1] == (x > 0) for x in c):
                raise ValueError('false model')
    elif d == 'unsat':
        if set(r) != {'decision', 'groups', 'buckets'}:
            raise ValueError('Hall fields')
        groups, buckets = r['groups'], r['buckets']
        b.tick(1 + len(groups) + len(buckets))
        if not groups or len(buckets) >= len(groups):
            raise ValueError('not deficient')
        flat, vars_seen = set(), set()
        for g in groups:
            b.tick(1 + len(g))
            if not g or frozenset(g) not in known:
                raise ValueError('missing group premise')
            for x in g:
                b.tick()
                if type(x) is not int or not 0 < abs(x) <= n or abs(x) in vars_seen:
                    raise ValueError('non-disjoint group')
                vars_seen.add(abs(x)); flat.add(x)
        seen = set()
        for bucket in buckets:
            b.tick(1 + len(bucket))
            if not bucket:
                raise ValueError('empty bucket')
            for x in bucket:
                b.tick()
                if type(x) is not int or x not in flat or x in seen:
                    raise ValueError('invalid partition')
                seen.add(x)
            for x, y in combinations(bucket, 2):
                b.tick()
                if frozenset((-x, -y)) not in known:
                    raise ValueError('missing conflict premise')
        if seen != flat:
            raise ValueError('incomplete partition')
    else:
        raise ValueError('not a positive certificate')
    b.tick()
    return True


def propose(n, f, b):
    known = normalize(n, f, b)
    groups = []
    for c in known:
        b.tick()
        if len(c) < 2:
            return None
        if len(c) >= 3:
            groups.append(order(c, b))
    # Group keys are disjoint at acceptance; charge size before comparisons.
    b.tick(1 + sum(map(len, groups)) * max(1, len(groups).bit_length()))
    groups.sort()
    orient, owner = {}, {}
    for i, g in enumerate(groups):
        for x in g:
            b.tick()
            if abs(x) in owner:
                return None
            owner[abs(x)] = i; orient[abs(x)] = x
    if not groups:
        return None
    graph = {x:set() for g in groups for x in g}
    b.tick(1 + len(graph))
    for c in known:
        b.tick()
        if len(c) != 2:
            continue
        a, z = c
        for x in (a, z):
            b.tick()
            if abs(x) in orient and orient[abs(x)] != -x:
                return None
            orient[abs(x)] = -x
        if abs(a) in owner and abs(z) in owner:
            graph[-a].add(-z); graph[-z].add(-a)
    seen, buckets, location = set(), [], {}
    for x in order(graph, b):
        b.tick()
        if x in seen:
            continue
        seen.add(x); stack = [x]; comp = []
        while stack:
            v = stack.pop(); comp.append(v)
            b.tick(1 + len(graph[v]))
            for y in graph[v]:
                if y not in seen:
                    seen.add(y); stack.append(y)
        b.tick(1 + len(comp))
        if any(len(graph[v]) != len(comp)-1 for v in comp):
            return None
        i = len(buckets); buckets.append(order(comp, b))
        for v in comp:
            b.tick(); location[v] = i
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
    b.tick(1+n)
    a = [orient.get(v,v)<0 for v in range(1,n+1)]
    for i,j in left.items():
        b.tick(1+len(groups[i])); x = next(x for x in groups[i] if location[x]==j)
        a[abs(x)-1] = x>0
    return {'decision':'sat','model':a}


def solve(n, f, *, steps, seconds):
    b = Meter(steps, seconds)
    try:
        c = propose(n, f, b)
        if c is None:
            return {'decision':'unknown','status':'unrecognized','work_steps':b.used,'certificate':None}
        check(n, f, c, b)
        return {'decision':c['decision'],'status':'verified','work_steps':b.used,'certificate':c}
    except Limit:
        return {'decision':'unknown','status':'resource_exhausted','work_steps':steps,'certificate':None}


def replay(n, f, r, *, steps):
    if set(r) != {'decision','status','work_steps','certificate'}:
        raise ValueError('report fields')
    w, c = r['work_steps'], r['certificate']
    if type(w) is not int or not 0 <= w <= steps:
        raise ValueError('work envelope')
    if r['status'] == 'verified':
        if r['decision'] not in ('sat','unsat') or not isinstance(c,dict) or c['decision'] != r['decision']:
            raise ValueError('decision mismatch')
        b = Meter(max(1,w), 15)
        check(n,f,c,b)
    elif (r['status'] not in ('unrecognized','resource_exhausted') or r['decision']!='unknown' or c is not None
          or (r['status']=='resource_exhausted' and w!=steps)):
        raise ValueError('uncredited result')
    return True
