"""Disjoint NAE triple structural obstructions; finite regression."""
from itertools import combinations
from mathos.research.f038_horn_cover import orientation, orient, satisfies


def formula(t):
    return tuple(c for i in range(t) for c in (
        (3*i+1,3*i+2,3*i+3),(-3*i-1,-3*i-2,-3*i-3)))


def model(w,t):
    return all((w>>(3*i))&7 not in (0,7) for i in range(t))


def local():
    subsets=closed=caps=0
    for s in range(8):
        allowed=tuple(x for x in range(8) if x not in (s,s^7))
        maximum=0
        for mask in range(64):
            r={x for i,x in enumerate(allowed) if mask&(1<<i)}
            subsets+=1
            if all(a&b in r for a in r for b in r):
                closed+=1
                maximum=max(maximum,len(r))
        assert maximum==(3 if s in (0,7) else 5)
        caps+=1
    # Explicit five-word Horn component and all six omissions by symmetry.
    h=((-1,3),(1,-2,-3))
    assert all(sum(l>0 for l in c)<=1 for c in h)
    assert {x for x in range(8) if satisfies(h,x)}==set(range(8))-{1,3,6}
    assert {x^1 for x in range(8) if satisfies(h,x)}==set(range(1,7))-{2}
    assert (subsets,closed,caps)==(512,260,8)
    print(f'F038_HORN_OBSTRUCTION_LOCAL_OK subsets={subsets} closed={closed} caps={caps}')


def audit():
    local()
    orientations=meet_checks=model_checks=deletions=success=projection=upper=0
    for t in range(1,4):
        n=3*t
        f=formula(t)
        models=tuple(w for w in range(1<<n) if model(w,t))
        assert len(models)==6**t
        assert all(model(w,t)==satisfies(f,w) for w in range(1<<n))
        for s in range(1<<n):
            sf=orient(f,s)
            pairs=[]
            for i in range(t):
                u=(s>>(3*i))&7
                if u.bit_count()>1:
                    u^=7
                z=[j for j in range(3) if not u&(1<<j)]
                pairs.append((u|(1<<z[0]),u|(1<<z[1])))
            words=tuple(sum(p[(a>>i)&1]<<(3*i) for i,p in enumerate(pairs))
                        for a in range(1<<t))
            assert len(set(words))==1<<t
            for w in words:
                assert satisfies(sf,w) and model(w^s,t)
                model_checks+=1
            for a,b in combinations(words,2):
                assert not satisfies(sf,a&b) and not model((a&b)^s,t)
                meet_checks+=1
            orientations+=1
        for mask in range(1<<n):
            b={i+1 for i in range(n) if mask&(1<<i)}
            o=orientation(f,n,b)
            hit=all(mask&(7<<(3*i)) for i in range(t))
            assert (o is not None)==hit
            if o is not None:
                assert all(sum(l>0 for l in c if abs(l) not in b)<=1
                           for c in orient(f,o))
            deletions+=1
            success+=hit
        for x in range(1<<t):
            w=sum((((x>>i)&1)|2)<<(3*i) for i in range(t))
            assert satisfies(f,w)
            projection+=1
        # Common orientation: complement second variable, pin first.
        s=sum(2<<(3*i) for i in range(t))
        sf=orient(f,s)
        for w in models:
            v=w^s
            pins={3*i+1:bool(v&(1<<(3*i))) for i in range(t)}
            h=tuple(tuple(l for l in c if abs(l) not in pins)
                    for c in sf if not any(abs(l) in pins and
                    pins[abs(l)]==(l>0) for l in c))
            h+=tuple((i if b else -i,) for i,b in pins.items())
            assert all(sum(l>0 for l in c)<=1 for c in h)
            assert satisfies(h,v)
            upper+=1
    assert (orientations,model_checks,meet_checks,deletions,success,projection,upper)==(
        584,4368,14728,584,399,14,258)
    print(f'F038_HORN_OBSTRUCTION_OK orientations={orientations} models={model_checks} '
          f'meet_checks={meet_checks} deletions={deletions} successful={success} '
          f'projection_witnesses={projection} upper_cover_checks={upper}')


if __name__=='__main__':
    audit()
