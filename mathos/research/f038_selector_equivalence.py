"""Universal selector witness extraction; exhaustive finite adversarial regression."""
from itertools import combinations, product


def satisfies(f, mask):
    return all(any(bool(mask & (1 << (abs(l)-1))) == (l > 0)
                   for l in c) for c in f)


def rows(n):
    return ((),) + tuple((s*i,) for i in range(1,n+1) for s in (-1,1)) + tuple(
        (a*i,b*j) for i,j in combinations(range(1,n+1),2)
        for a,b in product((-1,1),repeat=2))


def rename(f,i):
    def swap(l):
        v = abs(l)
        w = i if v == 1 else 1 if v == i else v
        return w if l > 0 else -w
    return tuple(tuple(swap(l) for l in c) for c in f)


def extract(f,n,selector):
    """A total selector callback; acceptance always uses original F."""
    g = tuple(f)
    mask = 0
    for i in range(1,n+1):
        b = selector(rename(g,i),n)
        assert b in (0,1)
        mask |= b << (i-1)
        g += ((i if b else -i,),)
    return mask if satisfies(f,mask) else None


def audit():
    totals = dict(formulas=0,sat=0,unsat=0,states=0,branch_checks=0,
                  leaves=0,accepted=0,rejected=0,off_promise=0)
    for n,clauses in ((1,rows(1)),(2,rows(2)),(3,(
            (-1,),(1,),(-2,),(2,),(-3,),(3,),(-1,-2),(2,3),
            (-1,-2,-3),(-1,2,3),(1,-2,3),(1,2,-3)))):
        domain = tuple(range(1<<n))
        for m in range(1<<len(clauses)):
            f = tuple(c for i,c in enumerate(clauses) if m & (1<<i))
            models = tuple(x for x in domain if satisfies(f,x))
            totals['formulas'] += 1
            totals['sat' if models else 'unsat'] += 1

            def walk(g,i,p):
                totals['states'] += 1
                remaining = tuple(x for x in models if
                                  x & ((1<<(i-1))-1) == p)
                assert remaining == tuple(x for x in domain if satisfies(g,x))
                if i == n+1:
                    totals['leaves'] += 1
                    ok = satisfies(f,p)
                    assert ok == bool(models)
                    totals['accepted' if ok else 'rejected'] += 1
                    return
                h = rename(g,i)
                good = []
                for b in (0,1):
                    s = any(bool(x&1) == bool(b) and satisfies(h,x) for x in domain)
                    assert s == any(bool(x&(1<<(i-1))) == bool(b) for x in remaining)
                    good.append(s)
                    totals['branch_checks'] += 1
                totals['off_promise'] += not any(good)
                for b in (0,1):
                    if good[b] or not any(good):
                        walk(g+((i if b else -i,),),i+1,p | (b<<(i-1)))

            walk(f,1,0)
            # Exercise concrete total callbacks choosing either preference.
            for pref in (0,1):
                def select(h,n):
                    return pref if any((x&1)==pref and satisfies(h,x)
                                       for x in range(1<<n)) else 1-pref
                found = extract(f,n,select)
                assert (found is not None) == bool(models)
            # Arbitrary incorrect advice is never a false-positive witness.
            for b in (0,1):
                found = extract(f,n,lambda h,n: b)
                assert found is None or satisfies(f,found)
    assert tuple(totals.values()) == (4616,1458,3158,51644,51284,
                                      26002,2436,23566,20408)
    print('F038_SELECTOR_EQUIVALENCE_OK ' +
          ' '.join(f'{k}={v}' for k,v in totals.items()))


if __name__ == '__main__':
    audit()
