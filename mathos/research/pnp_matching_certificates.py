"""Experimental signed matching-CNF recognizer; not a general SAT solver."""
from collections import deque
from itertools import combinations


def normalized(n, f):
    if type(n) is not int or n < 0:
        raise ValueError("variable count")
    out = set()
    for c in f:
        if any(type(x) is not int or not 0 < abs(x) <= n for x in c):
            raise ValueError("literal range")
        s = frozenset(c)
        if not any(-x in s for x in s):
            out.add(s)
    return out


def verify(n, f, r):
    known = normalized(n, f)
    if r["decision"] == "sat":
        a = r["model"]
        if len(a) != n or any(type(x) is not bool for x in a) or not all(
                any(a[abs(x)-1] == (x > 0) for x in c) for c in known):
            raise ValueError("invalid model")
    elif r["decision"] == "unsat":
        groups, buckets = r["groups"], r["buckets"]
        gs = [frozenset(c) for c in groups]
        flat = [x for c in groups for x in c]
        if (not gs or any(not c or c not in known for c in gs)
                or any(type(x) is not int or not 0 < abs(x) <= n for x in flat)
                or len({abs(x) for x in flat}) != len(flat)):
            raise ValueError("invalid disjoint required groups")
        bs = [x for b in buckets for x in b]
        if (len(buckets) >= len(groups) or any(not b for b in buckets)
                or any(type(x) is not int for x in bs)
                or len(bs) != len(flat) or set(bs) != set(flat)):
            raise ValueError("invalid deficient partition")
        for b in buckets:
            for x, y in combinations(b, 2):
                if frozenset((-x, -y)) not in known:
                    raise ValueError("missing original conflict premise")
    elif r != {"decision":"unknown"}:
        raise ValueError("uncredited verdict")
    return True


def solve(n, f):
    known = normalized(n, f)
    unknown = {"decision":"unknown"}
    # Wide clauses are disjoint choice groups; binary clauses are conflicts.
    # Width-two choice groups are intentionally outside this recognizer.
    groups = sorted(sorted(c) for c in known if len(c) >= 3)
    orient, owner = {}, {}
    for i, g in enumerate(groups):
        for x in g:
            v = abs(x)
            if v in owner:
                return unknown
            owner[v] = i
            orient[v] = x
    if not groups or any(len(c) < 2 for c in known):
        return unknown
    graph = {x:set() for g in groups for x in g}
    for c in known:
        if len(c) != 2:
            continue
        a, b = sorted(c)
        for x in (a, b):
            if abs(x) in orient and orient[abs(x)] != -x:
                return unknown
            orient[abs(x)] = -x
        if abs(a) in owner and abs(b) in owner:
            graph[-a].add(-b)
            graph[-b].add(-a)
    unseen = set(graph)
    buckets, location = [], {}
    while unseen:
        x = min(unseen)
        unseen.remove(x)
        q, comp = [x], []
        while q:
            v = q.pop()
            comp.append(v)
            nxt = graph[v] & unseen
            unseen.difference_update(nxt)
            q.extend(nxt)
        if any(len(graph[v]) != len(comp)-1 for v in comp):
            return unknown
        i = len(buckets)
        buckets.append(sorted(comp))
        location.update((v, i) for v in comp)
    adj = [sorted({location[x] for x in g}) for g in groups]
    left, right = {}, {}
    for root in range(len(groups)):
        seen, pred, queue, end = {root}, {}, deque([root]), None
        while queue and end is None:
            i = queue.popleft()
            for b in adj[i]:
                if b in pred:
                    continue
                pred[b] = i
                if b not in right:
                    end = b
                    break
                j = right[b]
                if j not in seen:
                    seen.add(j)
                    queue.append(j)
        if end is None:
            # No augmenting path: reachable left set has fewer neighbors.
            sel = [groups[i] for i in sorted(seen)]
            lits = {x for g in sel for x in g}
            r = {"decision":"unsat", "groups":sel,
                 "buckets":[[x for x in buckets[b] if x in lits] for b in sorted(pred)]}
            verify(n, f, r)
            return r
        while end is not None:
            i = pred[end]
            old = left.get(i)
            left[i], right[end] = end, i
            end = old
    a = [orient.get(v, v) < 0 for v in range(1, n+1)]
    for i, b in left.items():
        x = next(x for x in groups[i] if location[x] == b)
        a[abs(x)-1] = x > 0
    r = {"decision":"sat", "model":a}
    verify(n, f, r)
    return r
