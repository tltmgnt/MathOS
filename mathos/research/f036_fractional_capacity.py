"""Exact integer certificate checker; floating LP is only a candidate generator."""
from dataclasses import dataclass
from itertools import combinations, product
from math import ceil
from random import Random
from scipy.optimize import linprog
from scipy.sparse import csc_matrix

@dataclass(frozen=True)
class Certificate:
    demands: tuple
    weighted_groups: tuple
    scale: int


def check(f, cert):
    rows = [frozenset(c) for c in f]
    original = set(rows)
    if type(cert.scale) is not int or cert.scale <= 0 or any(0 in c for c in rows):
        return False
    used = set()
    for i in cert.demands:
        if not 0 <= i < len(rows) or not rows[i] or used & rows[i]:
            return False
        used.update(rows[i])
    covered = dict.fromkeys(used, 0)
    total = 0
    for g,w in cert.weighted_groups:
        if not g or len(set(g)) != len(g) or 0 in g or type(w) is not int or w <= 0:
            return False
        if any(frozenset((-u,-v)) not in original for u,v in combinations(g,2)):
            return False
        total += w
        for v in g:
            if v in covered:
                covered[v] += w
    return all(w >= cert.scale for w in covered.values()) and total < cert.scale*len(cert.demands)


def discover(f):
    rows = [frozenset(c) for c in f]
    if any(0 in c for c in rows):
        return None
    # A deterministic incomplete choice: literal-disjoint nonbinary demands.
    used, demands = set(), []
    for i,c in enumerate(rows):
        if len(c) >= 3 and not used & c:
            demands.append(i)
            used.update(c)
    if not demands:
        return None
    vs = sorted(used)
    adj = {v:set() for v in vs}
    for c in rows:
        if len(c) == 2:
            u,v = (-l for l in c)
            if u in adj and v in adj:
                adj[u].add(v)
                adj[v].add(u)
    groups = []
    def extend(g, rest):
        for j,v in enumerate(rest):
            h = (*g,v)
            groups.append(h)
            if len(h) < 4:
                extend(h, [u for u in rest[j+1:] if u in adj[v]])
    extend((),vs)
    index = {v:i for i,v in enumerate(vs)}
    pairs = [(index[v],j) for j,g in enumerate(groups) for v in g]
    a = csc_matrix(([1.0]*len(pairs),tuple(zip(*pairs))),shape=(len(vs),len(groups)))
    result = linprog([1.0]*len(groups),A_ub=-a,b_ub=[-1.0]*len(vs),bounds=(0,None),method='highs')
    if not result.success:
        return None
    q = 1000000
    weights = [max(0,ceil(float(w)*q)) for w in result.x]
    # Repair numerical undercoverage using singleton groups, then check exactly.
    single = {g[0]:j for j,g in enumerate(groups) if len(g)==1}
    cover = dict.fromkeys(vs,0)
    for g,w in zip(groups,weights):
        for v in g:
            cover[v]+=w
    for v,w in cover.items():
        weights[single[v]] += max(0,q-w)
    cert = Certificate(tuple(demands),tuple((g,w) for g,w in zip(groups,weights) if w),q)
    return cert if check(f,cert) else None


def family(t):
    f = []
    for p in range(t):
        vs = list(range(9*p+1,9*p+10))
        f.extend(tuple(vs[j:j+3]) for j in range(0,9,3))
        f.extend((-vs[i],-vs[j]) for i,j in combinations(range(9),2) if min(j-i,9-j+i)<=3)
    return f


def transform(f,rng):
    vs = sorted({abs(v) for c in f for v in c})
    perm = list(vs)
    rng.shuffle(perm)
    mp = {v:w*rng.choice((-1,1)) for v,w in zip(vs,perm)}
    g = [tuple(mp[abs(v)]*(1 if v>0 else -1) for v in c) for c in f]
    rng.shuffle(g)
    return g


def brute(f,n):
    return any(all(any(x[abs(l)-1]==(l>0) for l in c) for c in f) for x in product((False,True),repeat=n))


def run():
    rng=Random(3603)
    assert not brute(family(1),9)
    # Exact explicit overlapping certificate; no LP assumption.
    f=family(1)
    groups=tuple((tuple(1+(i+j)%9 for j in range(4)),1) for i in range(9))
    witness=Certificate((0,1,2),groups,4)
    assert check(f,witness)
    assert not check(f,Certificate(witness.demands,groups,5))
    assert not check(f,Certificate(witness.demands,groups[:-1],4))
    assert not check(f,Certificate(witness.demands,(((1,5),1),)+groups,4))
    unsat=sat=0
    for t in range(1,13):
        for _ in range(3):
            f=transform(family(t),rng)
            c=discover(f)
            assert c is not None and check(f,c),(t,c)
            unsat+=1
        # Keep only two demands per component. Select holes 1 and 5.
        f=[c for c in family(t) if not (len(c)==3 and min(c)%9==7)]
        assert all(any((abs(l)%9 in (1,5))==(l>0) for l in c) for c in f)
        assert discover(transform(f,rng)) is None
        sat+=1
    accepted=0
    for _ in range(256):
        f=[tuple(v*rng.choice((-1,1)) for v in rng.sample(range(1,7),rng.randrange(2,4))) for _ in range(rng.randrange(1,25))]
        c=discover(f)
        if c is not None:
            assert check(f,c) and not brute(f,6)
            accepted+=1
    assert discover([(1,),(-1,)]) is None
    print(f'random accepted={accepted}')
    print(f'F036_FRACTIONAL_CAPACITY_OK unsat={unsat} sat={sat} random=256 rejection=3 unknown=1')

if __name__=='__main__':
    run()
