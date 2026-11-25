"""Low-degree tape hitting, exact sparse-list lower-bound fixtures, and quadratic gates."""
from collections import deque
from mathos.research.f038_rule_certification import satisfies


def sparse_points(r,d):
    from itertools import combinations
    for k in range(min(r,d)+1):
        for ids in combinations(range(r),k):
            yield sum(1<<i for i in ids)


def evaluate(monomials,coeff,x):
    return sum(bool(coeff&(1<<i)) and x&a==a
               for i,a in enumerate(monomials))&1


def degree_audit():
    polys=nonzero=zero=ev=sparse=deletions=0
    minimum=None
    for r in range(1,5):
        d=min(2,r)
        ms=tuple(sparse_points(r,d))
        assert set(ms)=={x for x in range(1<<r) if x.bit_count()<=d}
        for coeff in range(1<<len(ms)):
            vals=tuple(evaluate(ms,coeff,x) for x in range(1<<r))
            count=sum(vals)
            assert any(vals[x] for x in ms)==bool(coeff)
            assert bool(count)==bool(coeff)
            if coeff:
                assert count>=1<<(r-d)
                minimum=count if minimum is None else min(minimum,count)
            polys+=1
            nonzero+=bool(coeff)
            zero+=not coeff
            ev+=len(vals)
            sparse+=len(ms)
        for x in ms:
            coeff=sum(1<<i for i,a in enumerate(ms) if a&x==x)
            assert all(evaluate(ms,coeff,y)==(x==y) for y in ms)
            deletions+=1
    assert (polys,nonzero,zero,ev,sparse,minimum,deletions)==(
        2196,2192,4,33864,23496,1,24)
    print(f'F038_LOW_DEGREE_HITTING_OK polynomials={polys} nonzero={nonzero} '
          f'zero={zero} evaluations={ev} sparse_checks={sparse} '
          f'min_support={minimum} deletion_cases={deletions}')


def quadratic(w,m):
    return ((w&((1<<m)-1))&(w>>m)).bit_count()&1


def linear_spaces(r):
    seen={frozenset((0,))}
    queue=deque(seen)
    while queue:
        v=queue.popleft()
        yield v
        for a in range(1,1<<r):
            if a not in v:
                w=v|frozenset(x^a for x in v)
                if w not in seen:
                    seen.add(w)
                    queue.append(w)


def quadratic_audit():
    spaces=constant=0
    maxima=[]
    densities=[]
    for m in range(1,4):
        n=1<<(2*m)
        values=tuple(quadratic(x,m) for x in range(n))
        ones=sum(values)
        assert ones==((1<<m)-1)*(1<<(m-1))
        densities.append(ones)
        maximum=-1
        for v in linear_spaces(2*m):
            dim=len(v).bit_length()-1
            assert len(v)==1<<dim
            seen=set()
            for a in range(n):
                if a in seen:
                    continue
                coset=tuple(x^a for x in v)
                seen.update(coset)
                spaces+=1
                if all(values[x] for x in coset):
                    constant+=1
                    maximum=max(maximum,dim)
                    assert dim<m
                    assert all(values[a]^values[a^w]^values[a^z]^values[a^w^z]==0
                               for w in v for z in v)
            assert len(seen)==n
        assert maximum==m-1
        maxima.append(maximum)
    assert (spaces,constant,maxima,densities)==(26705,743,[0,1,2],[1,6,28])
    print(f'F038_QUADRATIC_AFFINE_BARRIER_OK dimensions=3 affine_spaces={spaces} '
          f'constant_one_spaces={constant} max_dimensions={",".join(map(str,maxima))} '
          f'one_counts={",".join(map(str,densities))}')


def gated_unit_solver(f,n,tape,m):
    if len(f)!=n or any(len(c)!=1 for c in f):
        return None
    if {abs(c[0]) for c in f}!=set(range(1,n+1)):
        return None
    w=sum(1<<(c[0]-1) for c in f if c[0]>0)
    return w if quadratic(tape,m) else None


def unit_audit():
    inputs=checks=valid=abstentions=0
    for mask in range(16):
        f=tuple((i+1 if mask&(1<<i) else -i-1,) for i in range(4))
        for tape in range(64):
            w=gated_unit_solver(f,4,tape,3)
            assert (w is not None)==bool(quadratic(tape,3))
            if w is not None:
                assert w==mask and satisfies(f,w)
                valid+=1
            else:
                abstentions+=1
            checks+=1
        inputs+=1
    assert (inputs,checks,valid,abstentions)==(16,1024,448,576)
    print(f'F038_GATED_UNIT_WITNESS_OK inputs={inputs} tape_checks={checks} '
          f'valid_outputs={valid} abstentions={abstentions}')


if __name__=='__main__':
    degree_audit()
    quadratic_audit()
    unit_audit()
