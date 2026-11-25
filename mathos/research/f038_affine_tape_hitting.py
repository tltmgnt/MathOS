"""Explicit small-bias affine-tape hitting list and finite regression."""
from itertools import product


def remainder(a,b):
    while a and a.bit_length()>=b.bit_length():
        a^=b<<(a.bit_length()-b.bit_length())
    return a


def irreducible(poly,r):
    return poly.bit_length()==r+1 and all(
        remainder(poly,d) for k in range(1,r//2+1)
        for d in range(1<<k,1<<(k+1)))


def field_poly(r):
    return next(p for p in range(1<<r,1<<(r+1)) if irreducible(p,r))


def mul(a,b,q,poly):
    c=0
    while b:
        if b&1:
            c^=a
        b>>=1
        a<<=1
        if a&q:
            a^=poly
    return c


def parameters(m,h):
    assert m>=1 and h>=0
    r=max(1,(max(1,(m-1)*(1<<h))).bit_length())
    return 1<<r,field_poly(r)


def tapes(m,h,poly=None):
    q,p=parameters(m,h) if poly is None else (
        1<<(poly.bit_length()-1),poly)
    assert q>max(1,(m-1)*(1<<h))
    assert irreducible(p,q.bit_length()-1)
    for y in range(q):
        powers=[1]
        for i in range(1,m):
            powers.append(mul(powers[-1],y,q,p))
        for x in range(q):
            yield sum((mul(x,z,q,p)&1)<<i for i,z in enumerate(powers))


def parity(x):
    return x.bit_count()&1


def matches(w,rows,rhs):
    return all(parity(w&a)==b for a,b in zip(rows,rhs))


def audit():
    fields=samples=characters=bias_checks=systems=consistent=inconsistent=hits=0
    min_hits=None
    for m,h,q,p in ((2,1,4,7),(3,2,16,19),(4,2,16,19),(5,2,32,37)):
        assert parameters(m,h)[0]==q
        assert irreducible(p,q.bit_length()-1)
        assert all(any(mul(x,y,q,p)==1 for y in range(1,q))
                   for x in range(1,q))
        ts=tuple(tapes(m,h,p))
        generated=tuple(tapes(m,h))
        assert len(ts)==len(generated)==q*q
        fields+=1
        samples+=len(ts)
        for a in range(1,1<<m):
            total=sum(1-2*parity(a&w) for w in ts)
            assert 0<=total*q<=(m-1)*len(ts)
            characters+=1
            bias_checks+=len(ts)
        for rows in product(range(1<<m),repeat=h):
            for rhs in product((0,1),repeat=h):
                exists=any(matches(w,rows,rhs) for w in range(1<<m))
                count=sum(matches(w,rows,rhs) for w in ts)
                assert exists==bool(count)
                assert exists==any(matches(w,rows,rhs) for w in generated)
                systems+=1
                consistent+=exists
                inconsistent+=not exists
                if exists:
                    hits+=count
                    min_hits=count if min_hits is None else min(min_hits,count)
    assert (fields,samples,characters,bias_checks,systems,consistent,
            inconsistent,hits,min_hits)==(
        4,1552,56,37424,5384,5056,328,1130560,6)
    print(f'F038_AFFINE_TAPE_HITTING_OK fields={fields} samples={samples} '
          f'characters={characters} bias_checks={bias_checks} systems={systems} '
          f'consistent={consistent} inconsistent={inconsistent} hits={hits} '
          f'min_hits={min_hits}')
    ts=tuple(tapes(32,2,131))
    assert len(ts)==16384 and len(set(ts))==2289
    checks=0
    for a,b in ((1,2),(1<<31,1<<30),(0xaaaaaaaa,0x55555555),
                (0xffffffff,0x80000000)):
        assert a and b and a!=b
        for rhs in product((0,1),repeat=2):
            assert any(matches(w,(a,b),rhs) for w in ts)
            checks+=1
    print(f'F038_AFFINE_TAPE_SCALE_OK bits=32 entries={len(ts)} '
          f'distinct={len(set(ts))} rank_two_checks={checks}')


if __name__=='__main__':
    audit()
