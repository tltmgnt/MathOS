"""Global GF(2) affine-hull propagation from bounded local CNF scopes.

All computations use exact integers. Failure to refute means UNKNOWN.
The trace records locally justified equations and an empty local scope.
"""
from dataclasses import dataclass
from mathos.research.f036_coloring_gap import graph, cnf


def insert(basis, row, n):
    """Return 1 for rank increase, 0 for redundancy, -1 for inconsistency."""
    while row & ((1 << n)-1):
        mask = row & ((1 << n)-1)
        p = (mask & -mask).bit_length()-1
        if basis[p]:
            row ^= basis[p]
        else:
            basis[p] = row
            return 1
    return -1 if row >> n else 0


def patterns(n, basis, scope, local):
    pos = {v:j for j,v in enumerate(scope)}
    out = []
    for a in range(1 << len(scope)):
        if not all(any(bool(a & (1 << pos[abs(l)-1])) == (l>0)
                       for l in c) for c in local):
            continue
        b = basis.copy()
        for j,v in enumerate(scope):
            if insert(b,(1 << v) | (((a>>j)&1)<<n),n)<0:
                break
        else:
            out.append(a)
    return out


def local_rows(f, scope):
    s = set(scope)
    return [c for c in f if all(abs(l)-1 in s for l in c)]


def equation(n, scope, mask, rhs):
    return sum(1 << v for j,v in enumerate(scope) if mask & (1<<j)) | (rhs<<n)


@dataclass(frozen=True)
class Result:
    refuted: bool
    rank: int
    trace: tuple
    empty_scope: tuple | None


def close(n,f):
    assert all(0 < abs(l) <= n for c in f for l in c)
    scopes = list(dict.fromkeys(tuple(sorted({abs(l)-1 for l in c})) for c in f))
    groups = [(s,local_rows(f,s)) for s in scopes]
    basis = [0]*n
    trace = []
    while True:
        before = len(trace)
        for s,local in groups:
            vals = patterns(n,basis,s,local)
            if not vals:
                return Result(True,len(trace),tuple(trace),s)
            for mask in range(1,1<<len(s)):
                rhs = (mask & vals[0]).bit_count()%2
                if any((mask&a).bit_count()%2 != rhs for a in vals):
                    continue
                row = equation(n,s,mask,rhs)
                status = insert(basis,row,n)
                # Every surviving pattern extends to the old global space,
                # and every learned equation is valid on ALL those patterns.
                assert status >= 0
                if status:
                    trace.append((s,mask,rhs))
        if len(trace)==before:
            return Result(False,len(trace),tuple(trace),None)


def check(n,f,result):
    """Replay every independent equation, then prove the final local void."""
    if not result.refuted or result.empty_scope is None or len(result.trace)>n:
        return False
    if any(not 0<abs(l)<=n for c in f for l in c):
        return False
    scopes = {tuple(sorted({abs(l)-1 for l in c})) for c in f}
    if result.empty_scope not in scopes or result.rank != len(result.trace):
        return False
    b = [0]*n
    for s,mask,rhs in result.trace:
        if s not in scopes or not 0<mask<(1<<len(s)) or rhs not in (0,1):
            return False
        vals = patterns(n,b,s,local_rows(f,s))
        if not vals or any((mask&a).bit_count()%2!=rhs for a in vals):
            return False
        if insert(b,equation(n,s,mask,rhs),n)!=1:
            return False
    s = result.empty_scope
    return not patterns(n,b,s,local_rows(f,s))


def chain(k,bad):
    f=[]
    n=k
    outputs=[]
    for _ in range(3):
        a=1
        for i in range(2,k+1):
            n+=1
            z=n
            for u in (0,1):
                for v in (0,1):
                    w=1-(u^v)
                    f.append((-a if u else a,-i if v else i,-z if w else z))
            a=z
        outputs.append(a)
    a,b,c=outputs
    f.extend([(a,b),(-b,-c) if bad else (b,c)])
    return n,f


def run():
    for k in range(2,17):
        n,f=chain(k,True)
        r=close(n,f)
        assert r.refuted and check(n,f,r)
        n,f=chain(k,False)
        assert not close(n,f).refuted
    n,f=chain(4,True)
    r=close(n,f)
    assert not check(n,f,Result(True,r.rank,r.trace[:-1],r.empty_scope))
    s,mask,rhs=r.trace[0]
    assert not check(n,f,Result(True,r.rank,((s,mask,1-rhs),)+r.trace[1:],r.empty_scope))
    assert not check(n,f,Result(True,r.rank,r.trace,None))
    for k in range(5,20,2):
        n,e=graph(k)
        r=close(3*n,cnf(n,e))
        assert not r.refuted and r.rank==n
        print(f"coloring cycle={k} rank={r.rank} variables={3*n} UNKNOWN")
    print("F036_GLOBAL_AFFINE_OK chains=15 controls=15 coloring_gap=8 rejection=3")


if __name__=="__main__":
    run()
