"""Checked literal substitutions as model retractions.

A syntactic sufficient condition: every image clause is tautological
or subsumes an original witness in the sense of containing that witness.
No SAT oracle is used for discovery or replay.
"""
from itertools import combinations, permutations, product
from random import Random
from mathos.research.f037_log_backdoor import normalize, decide, satisfies
from mathos.research.f037_symmetry_selector import discover as symmetries


def image(c, mapping):
    return frozenset((1 if l>0 else -1)*mapping.get(abs(l),abs(l)) for l in c)


def check(f,mapping):
    vs={abs(l) for c in f for l in c}
    if not mapping or not set(mapping)<=vs:
        return False
    if any(type(v) is not int or abs(v) not in vs-set(mapping) for v in mapping.values()):
        return False
    originals={frozenset(c) for c in f}
    for c in f:
        if not any(abs(l) in mapping for l in c):
            continue
        d=image(c,mapping)
        if any(-l in d for l in d):
            continue
        # Width at most three in the intended input class.
        ls=sorted(d)
        if not any(frozenset(s) in originals
                   for k in range(len(ls)+1) for s in combinations(ls,k)):
            return False
    return True


def fold(f,mapping):
    assert check(f,mapping)
    return tuple(dict.fromkeys(normalize(tuple(tuple(sorted(image(c,mapping))) for c in f))))


def gadgets(f):
    rows={frozenset(c) for c in f}
    return sorted({tuple(sorted(c)) for c in f if len(c)==3 and
                   all(frozenset((-a,-b)) in rows for a,b in combinations(c,2))})


def find(f):
    # Recognize signed one-hot triples, then try every ordered pair
    # of disjoint gadgets and every permutation of three colors.
    gs=gadgets(f)
    for a in gs:
        for b in gs:
            if {abs(l) for l in a}&{abs(l) for l in b}:
                continue
            for p in permutations(b):
                m={abs(l):(1 if l>0 else -1)*r for l,r in zip(a,p)}
                if check(f,m):
                    return m
    return None


def reduce(raw):
    f=normalize(raw)
    trace=[]
    while True:
        m=find(f)
        if m is None:
            return f,tuple(trace)
        g=fold(f,m)
        assert len({abs(l) for c in g for l in c}) < len({abs(l) for c in f for l in c})
        trace.append(m)
        f=g


def replay(raw,trace):
    f=normalize(raw)
    for m in trace:
        if not check(f,m):
            return None
        f=fold(f,m)
    return f


def lift(x,trace):
    x=dict(x)
    for m in reversed(trace):
        for v,l in m.items():
            x[v]=(x.get(abs(l),False)==(l>0))
    return x


def solve(raw,k=4):
    raw=tuple(tuple(c) for c in raw)
    f,trace=reduce(raw)
    assert replay(raw,trace)==f
    status,evidence=decide(f,k)
    if status=='SAT':
        x=lift(evidence,trace)
        assert satisfies(raw,x)
        return status,x
    if status=='UNSAT':
        return status,(trace,evidence)
    return status,None


def check_unsat(raw,cert):
    from mathos.research.f037_log_backdoor import check_unsat as check_leaf
    trace,proof=cert
    f=replay(raw,trace)
    return f is not None and check_leaf(f,proof)


def multipartite(parts,t):
    n=parts*t
    f=[]
    for i in range(n):
        a,b,c=range(3*i+1,3*i+4)
        f.extend(((a,b,c),(-a,-b),(-a,-c),(-b,-c)))
    for i,j in combinations(range(n),2):
        if i//t!=j//t:
            f.extend((-3*i-c,-3*j-c) for c in (1,2,3))
    return tuple(f)


def transform(f,rng):
    vs=sorted({abs(l) for c in f for l in c})
    p=list(vs)
    rng.shuffle(p)
    m={v:w*rng.choice((-1,1)) for v,w in zip(vs,p)}
    g=[tuple(m[abs(l)]*(1 if l>0 else -1) for l in c) for c in f]
    rng.shuffle(g)
    return tuple(g)


def run():
    rng=Random(3708)
    maps=transports=0
    for _ in range(128):
        f=normalize(tuple(tuple(v*rng.choice((-1,1)) for v in rng.sample(range(1,5),rng.randrange(1,4)))
                          for _ in range(rng.randrange(1,12))))
        vs=sorted({abs(l) for c in f for l in c})
        xs=[dict(zip(vs,bits)) for bits in product((False,True),repeat=len(vs))]
        sat=any(satisfies(f,x) for x in xs)
        for v,w in permutations(vs,2):
            for sign in (-1,1):
                m={v:sign*w}
                if not check(f,m):
                    continue
                maps+=1
                h=fold(f,m)
                assert sat==any(satisfies(h,x) for x in xs)
                for x in xs:
                    if satisfies(f,x):
                        assert satisfies(f,lift(x,(m,)))
                        transports+=1
    for t in (2,4,8,12):
        for p in (3,4):
            f=transform(multipartite(p,t),rng)
            assert not symmetries(f)
            h,trace=reduce(f)
            assert len(trace)==p*(t-1)
            assert len({abs(l) for c in h for l in c})==3*p
            status,evidence=solve(f)
            assert status==('SAT' if p==3 else 'UNSAT')
            if status=='UNSAT':
                assert check_unsat(f,evidence)
    f=multipartite(3,2)
    assert not check(f,{1:1})
    assert not check(f,{1:7,2:8,3:9}) # adjacent vertices
    assert replay(f,({1:999},)) is None
    print(f"checked_maps={maps} model_transports={transports}")
    print("F037_CHECKED_FOLDING_OK random=128 multipartite=8 max_variables=144 rejection=3")


if __name__=="__main__":
    run()
