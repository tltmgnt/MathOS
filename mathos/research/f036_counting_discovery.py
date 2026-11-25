"""Sound but incomplete global counting discovery for signed-integer CNF.

Only positive demands and negative-binary clique capacities are handled.
No unrestricted SAT-completeness or bit-machine cost theorem.
"""
from collections import deque
from dataclasses import dataclass
from itertools import combinations
from random import Random


@dataclass(frozen=True)
class Certificate:
    steps: tuple  # (left index, right index, positive pivot, sorted resolvent)
    demands: tuple  # indices in original + derived rows
    groups: tuple  # sorted positive-variable tuples


def canon(f):
    return [frozenset(c) for c in f]


def check(f, cert):
    """Check resolution, disjoint demands, clique evidence and Hall deficit."""
    rows = canon(f)
    original = set(rows)
    for i, j, v, c in cert.steps:
        if not (0 <= i < len(rows) and 0 <= j < len(rows) and v > 0):
            return False
        if v not in rows[i] or -v not in rows[j]:
            return False
        if frozenset(c) != (rows[i]-{v}) | (rows[j]-{-v}):
            return False
        rows.append(frozenset(c))
    used = set()
    for i in cert.demands:
        if not 0 <= i < len(rows):
            return False
        c = rows[i]
        if not c or any(v <= 0 for v in c) or used.intersection(c):
            return False
        used.update(c)
    covered = set()
    for g in cert.groups:
        if not g or len(set(g)) != len(g) or any(v <= 0 for v in g):
            return False
        if any(frozenset((-u, -v)) not in original
               for u, v in combinations(g, 2)):
            return False
        covered.update(g)
    return used <= covered and len(cert.demands) > len(cert.groups)


def discover(f):
    """Deterministic syntactic demand extraction + bipartite matching.

    Connected components of the negative-binary graph must be cliques
    to be used. Cyclic or missing gate definitions cause demand rejection.
    Every returned certificate is independently checked.
    """
    rows = canon(f)
    original = list(rows)
    adjacency = {}
    rules = {}
    for i, c in enumerate(original):
        if len(c) == 2 and all(v < 0 for v in c):
            u, v = sorted(-l for l in c)
            adjacency.setdefault(u, set()).add(v)
            adjacency.setdefault(v, set()).add(u)
        neg = [v for v in c if v < 0]
        pos = sorted(v for v in c if v > 0)
        if len(neg) == 1 and 1 <= len(pos) <= 2 and -neg[0] not in pos:
            rules.setdefault(-neg[0], []).append((tuple(pos), i))
    group_of, groups, seen = {}, [], set()
    for root in sorted(adjacency):
        if root in seen:
            continue
        seen.add(root)
        stack, group = [root], []
        while stack:
            u = stack.pop()
            group.append(u)
            for v in sorted(adjacency[u]):
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        group.sort()
        if any(len(adjacency[v]) != len(group)-1 for v in group):
            continue
        for v in group:
            group_of[v] = len(groups)
        groups.append(tuple(group))
    steps, demands, used = [], [], set()
    for i, c in enumerate(original):
        if not c or any(v <= 0 for v in c):
            continue
        # Derive a positive demand over recognized capacity groups.
        current, index, pivots = c, i, set()
        while any(v not in group_of for v in current):
            v = min(v for v in current if v not in group_of)
            if v in pivots or v not in rules:
                break
            pivots.add(v)
            _, j = min(rules[v])
            current = (current-{v}) | (original[j]-{-v})
            steps.append((index, j, v, tuple(sorted(current))))
            index = len(rows)
            rows.append(current)
        if (current and all(v in group_of for v in current)
                and not used.intersection(current)):
            demands.append(index)
            used.update(current)
    edges = [sorted({group_of[v] for v in rows[i]}) for i in demands]
    # Augment one demand at a time. If search fails, the reachable
    # demand/group sets exhibit a Hall deficit directly.
    owner = {}
    for start in range(len(demands)):
        queue = deque([start])
        reachable = {start}
        via = {}  # group -> predecessor demand
        incoming = {}  # matched demand -> matched group
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
                if j not in reachable:
                    reachable.add(j)
                    incoming[j] = g
                    queue.append(j)
        if free is None:
            cert = Certificate(tuple(steps), tuple(demands[i] for i in sorted(reachable)),
                               tuple(groups[g] for g in sorted(via)))
            assert check(f, cert)
            return cert
        g = free
        while True:
            i = via[g]
            owner[g] = i
            if i == start:
                break
            g = incoming[i]
    return None


def pigeon(pigeons, holes):
    def ident(p,kind,j):
        return 1+p*2*holes+(holes if kind=='s' else 0)+j
    rows=[]
    for p in range(pigeons):
        a,b=ident(p,'x',0),ident(p,'s',0)
        rows.extend([(-a,b),(a,-b)])
        for j in range(1,holes):
            u,v,t=ident(p,'s',j-1),ident(p,'x',j),ident(p,'s',j)
            rows.extend([(-u,t),(-v,t),(u,v,-t)])
        rows.append((ident(p,'s',holes-1),))
    for p,q in combinations(range(pigeons),2):
        for j in range(holes):
            rows.append((-ident(p,'x',j),-ident(q,'x',j)))
    return rows


def run():
    # Positive discovery without supplied demand groups or gate map.
    rng=Random(3601)
    cases=0
    for k in range(2,21):
        f=pigeon(k+1,k)
        for _ in range(3):
            rng.shuffle(f)
            c=discover(f)
            assert c is not None and check(f,c)
            assert len(c.demands)==k+1 and len(c.groups)==k
            cases+=1
        assert discover(pigeon(k,k)) is None
    # Hall subset deficit despite equal total group and demand counts.
    f=[(1,),(2,),(3,4),(-1,-2),(-3,-5),(-4,-6)]
    c=discover(f)
    assert c is not None and check(f,c)
    assert len(c.demands)==2 and len(c.groups)==1
    # Invalid proof evidence, absent group capacity, overlapping demands.
    p=pigeon(4,3)
    c=discover(p)
    assert c is not None
    i,j,v,row=c.steps[0]
    assert not check(p,Certificate(((i,j,v+10000,row),)+c.steps[1:],c.demands,c.groups))
    assert not check(p,Certificate(c.steps,c.demands,c.groups[:-1]))
    assert not check(p,Certificate(c.steps,c.demands+(c.demands[0],),c.groups))
    # An UNSAT formula not recognized by the syntactic fragment.
    assert discover([(1,),(-1,)]) is None
    print(f'F036_COUNTING_DISCOVERY_OK shuffled={cases} satisfiable=19 subset=1 rejection=3 unknown=1')

if __name__=='__main__':
    run()
