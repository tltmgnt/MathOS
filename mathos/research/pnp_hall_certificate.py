"""Certified matching reduction for disjoint positive choice clauses."""
from collections import deque
from itertools import combinations
from .pnp_structural_kernel import Budget, Exhausted, validate


def eligible(f):
    return (sum(len(c) >= 2 and all(x > 0 for x in c) for c in f) >= 2
            and any(len(c) == 2 and c[0] < 0 and c[1] < 0 and c[0] != c[1] for c in f))


def _negative_pairs(f, b):
    pairs = set()
    for c in f:
        b.tick(1 + len(c))
        if len(c) == 2 and c[0] < 0 and c[1] < 0 and c[0] != c[1]:
            pairs.add(tuple(sorted((-c[0], -c[1]))))
    return pairs


def verify(n, clauses, result, b):
    f = validate(n, clauses)
    cert = result['certificate']
    if result['decision'] == 'sat':
        if (not isinstance(cert, list) or len(cert) != n
                or any(type(x) is not bool for x in cert)):
            raise ValueError('invalid model')
        for c in f:
            b.tick(1 + len(c))
            if not any(cert[abs(x)-1] == (x > 0) for x in c):
                raise ValueError('model falsifies input')
        return True
    if result['decision'] != 'unsat':
        raise ValueError('not a decision')
    ids, resources = cert['groups'], cert['resources']
    if (not isinstance(ids, list) or not isinstance(resources, list)
            or not ids or len(ids) > n or not 0 <= len(resources) < len(ids)):
        raise ValueError('no Hall deficiency')
    owner = {}
    for i in ids:
        if type(i) is not int or not 0 <= i < len(f):
            raise ValueError('bad group reference')
        c = f[i]
        b.tick(1 + len(c))
        if not c or any(x < 0 for x in c) or set(c) & owner.keys():
            raise ValueError('groups must be nonempty positive and disjoint')
        owner.update((v, i) for v in set(c))
    pairs = _negative_pairs(f, b)
    seen = set()
    for r in resources:
        if not isinstance(r, list) or not r or len(r) > n:
            raise ValueError('invalid resource')
        for v in r:
            b.tick()
            if type(v) is not int or v not in owner or v in seen:
                raise ValueError('resource partition mismatch')
            seen.add(v)
        for u, v in combinations(r, 2):
            b.tick()
            if owner[u] != owner[v] and tuple(sorted((u, v))) not in pairs:
                raise ValueError('missing cross-group incompatibility')
    if seen != set(owner):
        raise ValueError('incomplete resource partition')
    return True


def propose(n, clauses, b):
    f = validate(n, clauses)
    candidates = []
    for i, c in enumerate(f):
        b.tick(1 + len(c))
        if c and all(x > 0 for x in c):
            candidates.append((tuple(sorted(set(c))), i))
    groups, owner, indices = [], {}, []
    for vs, i in sorted(candidates, key=lambda p: (len(p[0]), p[0], p[1])):
        b.tick(1 + len(vs))
        if any(v in owner for v in vs):
            continue
        owner.update((v, len(groups)) for v in vs)
        groups.append(vs)
        indices.append(i)
    if len(groups) < 2:
        return None
    g = {v: set() for v in owner}
    for u, v in sorted(_negative_pairs(f, b)):
        b.tick()
        if u in owner and v in owner and owner[u] != owner[v]:
            g[u].add(v)
            g[v].add(u)
    # Each connected conflict component is a candidate resource. If it is
    # not complete between different groups, conservatively use singletons.
    unseen = set(g)
    resources = []
    for root in sorted(g):
        if root not in unseen:
            continue
        unseen.remove(root)
        todo, comp = [root], []
        while todo:
            v = todo.pop()
            comp.append(v)
            b.tick(1 + len(g[v]))
            new = g[v] & unseen
            unseen.difference_update(new)
            todo.extend(sorted(new))
        comp.sort()
        complete = True
        for u, v in combinations(comp, 2):
            b.tick()
            if owner[u] != owner[v] and v not in g[u]:
                complete = False
                break
        resources.extend([comp] if complete else [[v] for v in comp])
    resource_of = {v: r for r, vs in enumerate(resources) for v in vs}
    adj = [sorted({resource_of[v] for v in vs}) for vs in groups]
    gr, rg = {}, {}
    for root in range(len(groups)):
        # Iterative alternating-path search; no recursion/depth restriction.
        queue, seen, parent = deque([root]), {root}, {}
        free = None
        while queue and free is None:
            u = queue.popleft()
            b.tick()
            for r in adj[u]:
                b.tick()
                if r in parent:
                    continue
                parent[r] = u
                if r not in rg:
                    free = r
                    break
                v = rg[r]
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        if free is None:
            # All reachable resources matched to reachable groups, but the
            # root is unmatched. Export only this deficient subsystem.
            return {'decision': 'unsat', 'certificate': {
                'groups': [indices[u] for u in sorted(seen)],
                'resources': [[v for v in resources[r] if owner[v] in seen]
                              for r in sorted(parent)]}}
        while free is not None:
            b.tick()
            u = parent[free]
            old = gr.get(u)
            gr[u], rg[free] = free, u
            free = old
    model = [False] * n
    for u, vs in enumerate(groups):
        b.tick(1 + len(vs))
        v = next(v for v in vs if resource_of[v] == gr[u])
        model[v-1] = True
    # Matching is only necessary for general CNF. Additional clauses can
    # falsify this particular model; that produces UNKNOWN, not UNSAT.
    for c in f:
        b.tick(1 + len(c))
        if not any(model[abs(x)-1] == (x > 0) for x in c):
            return None
    return {'decision': 'sat', 'certificate': model}
