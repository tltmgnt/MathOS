"""Majority witness composition and mixed Horn/dual-Horn barrier: finite audit."""
from itertools import combinations
from mathos.research.f038_rule_certification import ROWS, satisfies

BI_ROWS = ((-1,2),(1,-2),(-2,3),(2,-3),(-3,4),(3,-4),
           (-4,5),(4,-5),(1,5),(-1,-5),(5,),(-5,))


def feasible(f, n):
    """2-SAT by bitset reachability (polynomial, not enumeration)."""
    r = [1<<i for i in range(2*n)]

    def idx(l):
        return 2*(abs(l)-1) + (l>0)

    for c in f:
        if not c:
            return False
        assert len(c)<=2
        a,b=idx(c[0]),idx(c[-1])
        r[a^1] |= 1<<b
        r[b^1] |= 1<<a
    for k in range(2*n):
        for i in range(2*n):
            if r[i] & (1<<k):
                r[i] |= r[k]
    return not any(r[i] & (1<<(i+1)) and r[i+1] & (1<<i)
                   for i in range(0,2*n,2))


def seed(f,n,pins):
    g=f+tuple((i+1 if b else -i-1,) for i,b in pins)
    if not feasible(g,n):
        return None
    mask=0
    for i in range(n):
        if feasible(g+((-i-1,),),n):
            g+=((-i-1,),)
        else:
            g+=((i+1,),)
            mask|=1<<i
    assert satisfies(g,mask)
    return mask


def seeds(f,n,m):
    table={}
    pairs=((0,0),) if m==1 else tuple(combinations(range(m),2))
    for i,j in pairs:
        for p in range(2 if i==j else 4):
            pins=((i,p&1),) if i==j else ((i,p&1),(j,p>>1))
            table[i,j,p]=seed(f,n,pins)
    return table


def compose(f,m,table,x):
    assert all(v is not None for v in table.values())

    def get(i,j):
        return table[i,j,((x>>i)&1)+(0 if i==j else 2*((x>>j)&1))]

    if m==1:
        return get(0,0),0
    prev={j:get(0,j) for j in range(1,m)}
    steps=0
    for t in range(1,m-1):
        nxt={}
        for j in range(t+1,m):
            a,b,c=prev[t],prev[j],get(t,j)
            v=(a&b)|(a&c)|(b&c)
            assert satisfies(f,v)
            assert not ((v^x)&(((1<<(t+1))-1)|(1<<j)))
            nxt[j]=v
            steps+=1
        prev=nxt
    return prev[m-1],steps


def positive():
    families=total=failed=probes=missing=outputs=majority=0
    for mask in range(1<<len(BI_ROWS)):
        f=tuple(c for i,c in enumerate(BI_ROWS) if mask&(1<<i))
        models=tuple(w for w in range(32) if satisfies(f,w))
        for m in range(1,5):
            families+=1
            table=seeds(f,5,m)
            for (i,j,p),v in table.items():
                match=lambda w: ((w>>i)&1)==(p&1) and (
                    i==j or ((w>>j)&1)==(p>>1))
                assert (v is not None)==any(match(w) for w in models)
                if v is not None:
                    assert match(v) and satisfies(f,v)
                probes+=1
                missing+=v is None
            valid=all(v is not None for v in table.values())
            assert valid==all(any(w&((1<<m)-1)==x for w in models)
                              for x in range(1<<m))
            if not valid:
                failed+=1
                continue
            total+=1
            for x in range(1<<m):
                w,steps=compose(f,m,table,x)
                assert satisfies(f,w) and w&((1<<m)-1)==x
                assert steps==(m-1)*(m-2)//2
                outputs+=1
                majority+=steps
    assert (families,total,failed,probes,missing,outputs,majority)==(
        16384,2484,13900,172032,91328,6686,1592)
    print(f'F038_MAJORITY_COMPOSITION_OK families={families} total={total} '
          f'failed={failed} seed_probes={probes} missing={missing} '
          f'outputs={outputs} majority={majority}')


def blocks(f,n,m):
    def copy(l):
        v=abs(l)
        return (n+v if v<=m else v)*(1 if l>0 else -1)
    return tuple((tuple(copy(l) for l in c),) for c in f)+tuple(
        ((-i,n+i),(i,-n-i)) for i in range(1,m+1))


def mixed():
    families=total=failed=params=local=global_checks=0
    for mask in range(1<<len(ROWS)):
        f=tuple(c for i,c in enumerate(ROWS) if mask&(1<<i))
        for m in (1,2):
            families+=1
            bs=blocks(f,3,m)
            joint=tuple(c for b in bs for c in b)
            for b in bs:
                assert all(sum(l>0 for l in c)<=1 for c in b) or all(
                    sum(l<0 for l in c)<=1 for c in b)
            valid=True
            for x in range(1<<m):
                params+=1
                for i,b in enumerate(bs):
                    w=x
                    if i<len(f):
                        l=b[0][0]
                        if l>0:
                            w|=1<<(l-1)
                    else:
                        j=i-len(f)
                        w|=((x>>j)&1)<<(3+j)
                    assert satisfies(b,w)
                    local+=1
                exists=False
                for y in range(1<<(3-m)):
                    w=x|(y<<m)
                    for c in range(1<<m):
                        got=satisfies(joint,w|(c<<3))
                        assert got==(c==x and satisfies(f,w))
                        exists|=got
                        global_checks+=1
                valid &= exists
            total+=valid
            failed+=not valid
    assert (families,total,failed,params,local,global_checks)==(
        8192,356,7836,24576,188416,196608)
    print(f'F038_MIXED_COMPOSITION_OK families={families} total={total} '
          f'failed={failed} parameters={params} local_witnesses={local} '
          f'global_checks={global_checks}')


if __name__=='__main__':
    positive()
    mixed()
