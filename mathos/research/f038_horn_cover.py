"""Common-oriented Horn-cover compatibility; constructive algorithm and finite regression."""
from itertools import combinations, combinations_with_replacement
from mathos.research.f038_witness_composition import seed

ROWS = ((5,1,-6),(-5,2,-1),(5,-2,6),(-5,-3,4),(5,-4,-6),
        (-5,-6),(5,6),(-5,-1,-2),(5,-3,2),(-5,3,-4),(-5,6),(5,-1))


def satisfies(f, w):
    return all(any(bool(w & (1<<(abs(l)-1))) == (l>0)
                   for l in c) for c in f)


def orient(f, mask):
    return tuple(tuple(-l if mask & (1<<(abs(l)-1)) else l
                       for l in c) for c in f)


def orientation(f, n, backdoor):
    # f normalized; forbid two nonbackdoor literals remaining positive.
    clauses = tuple(pair for c in f for pair in
                    combinations(tuple(l for l in c if abs(l) not in backdoor),2))
    return seed(clauses,n,())


def horn_model(f):
    assert all(sum(l>0 for l in c)<=1 for c in f)
    w=0
    while True:
        nxt=w
        for c in f:
            if all(w & (1<<(-l-1)) for l in c if l<0):
                h=next((l for l in c if l>0),None)
                if h is None:
                    return None
                nxt|=1<<(h-1)
        if nxt==w:
            assert satisfies(f,w)
            return w
        w=nxt


def residual(f, backdoor, b):
    values = dict(zip(backdoor, (bool(b & (1<<i))
                                 for i in range(len(backdoor)))))
    g = tuple(tuple(l for l in c if abs(l) not in values)
              for c in f
              if not any(abs(l) in values and values[abs(l)]==(l>0)
                         for l in c))
    return g + tuple((v if value else -v,) for v,value in values.items())


def alternatives(f, backdoor):
    return tuple(residual(f,backdoor,b) for b in range(1<<len(backdoor)))


def pinned_model(f,m,x):
    return horn_model(f+tuple((i+1 if x & (1<<i) else -i-1,)
                              for i in range(m)))


def near_top(m,k):
    top=(1<<m)-1
    for j in range(min(m,k)+1):
        for zeros in combinations(range(m),j):
            yield top ^ sum(1<<i for i in zeros)


def certify(hs,m):
    # None means universal coverage, else an uncovered parameter vector.
    for x in near_top(m,len(hs)):
        if witness(hs,m,x) is None:
            return x
    return None


def witness(hs,m,x):
    for b,h in enumerate(hs):
        w=pinned_model(h,m,x)
        if w is not None:
            return b,w
    return None


def abstract():
    rels = tuple(r for r in range(256) if all(
        not ((r>>a)&1 and (r>>b)&1) or (r>>(a&b))&1
        for a in range(8) for b in range(8)))
    assert len(rels)==122
    for k, expected in ((1,(122,1,121,488,1)),
                        (2,(7503,551,6952,52521,2)),
                        (3,(310124,71609,238515,2480992,3))):
        high=tuple(near_top(3,k))
        highmask=sum(1<<x for x in high)
        cases=total=non=probes=worst=0
        for rs in combinations_with_replacement(rels,k):
            union=0
            for r in rs:
                union|=r
            full=union==255
            assert full==((union&highmask)==highmask)
            cases+=1
            total+=full
            non+=not full
            probes+=len(high)
            if not full:
                worst=max(worst,min(3-x.bit_count()
                                    for x in range(8) if not union & (1<<x)))
        assert (cases,total,non,probes,worst)==expected
        print(f'F038_HORN_COVER_ABSTRACT_OK k={k} cases={cases} total={total} '
              f'non_total={non} probes={probes} worst_min_zeros={worst}')


def concrete():
    families=total=non=probes=checks=outputs=missing=orientation_checks=0
    high=tuple(near_top(4,2))
    for mask in range(1<<len(ROWS)):
        f=tuple(c for i,c in enumerate(ROWS) if mask&(1<<i))
        hs=alternatives(f,(5,))
        covered=[]
        for x in range(16):
            found=False
            for b,h in enumerate(hs):
                w=pinned_model(h,4,x)
                want=any(satisfies(f,x|(b<<4)|(y<<5)) for y in (0,1))
                assert (w is not None)==want
                if w is not None:
                    assert satisfies(f,w) and w&31==x|(b<<4)
                found|=want
                checks+=1
            got=witness(hs,4,x)
            assert (got is not None)==found
            covered.append(found)
            outputs+=found
        bad=certify(hs,4)
        valid=all(covered)
        assert (bad is None)==valid
        if bad is not None:
            assert not covered[bad] and bad in high
        probes+=len(high)
        missing+=sum(not covered[x] for x in high)
        # Flip a deterministic sign pattern, recover any common orientation,
        # and check coverage and models after undoing the recovered flips.
        flip=(mask^(mask>>6))&63
        ff=orient(f,flip)
        o=orientation(ff,6,(5,))
        assert o is not None
        signed=orient(ff,o)
        sh=alternatives(signed,(5,))
        assert all(sum(l>0 for l in c)<=1 for h in sh for c in h)
        assert (certify(sh,4) is None)==valid
        for x in range(16):
            got=witness(sh,4,x^(o&15))
            assert (got is not None)==covered[x^(flip&15)]
            if got is not None:
                _,w=got
                assert satisfies(ff,w^o) and (w^o)&15==x
            orientation_checks+=1
        families+=1
        total+=valid
        non+=not valid
    assert (families,total,non,probes,checks,outputs,missing,orientation_checks)==(
        4096,736,3360,45056,131072,43728,17328,65536)
    print(f'F038_HORN_COVER_CONCRETE_OK families={families} total={total} '
          f'non_total={non} near_probes={probes} alternative_checks={checks} '
          f'outputs={outputs} missing_near={missing} orientation_checks={orientation_checks}')


if __name__=='__main__':
    abstract()
    concrete()
