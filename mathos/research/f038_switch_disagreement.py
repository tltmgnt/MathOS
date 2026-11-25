"""Switch disagreement theorem and middle-layer point-query barrier."""
from itertools import product
from mathos.research.f038_monotone_choice import sat, restrict


def bits(mask):
    while mask:
        bit=mask&-mask
        mask^=bit
        yield bit


def submasks(mask):
    v=mask
    while True:
        yield v
        if v==0:
            return
        v=(v-1)&mask


def seeds(formulas,u,solve):
    """solve(i, pins) returns an existential witness or None, total callback."""
    pos=neg=0
    for f in formulas:
        for c in f:
            for l in c:
                bit=1<<(abs(l)-1)
                if l>0:
                    pos|=bit
                else:
                    neg|=bit
    d=u&pos&neg
    worst=u&neg&~pos
    table={}
    for a in submasks(d):
        x=a|worst
        pins={bit.bit_length():bool(x&bit) for bit in bits(u)}
        for i in range(len(formulas)):
            w=solve(i,pins)
            if w is not None:
                table[a]=(i,w)
                break
        else:
            table[a]=None
    return d,table


def abstract():
    mons=tuple(r for r in range(256) if all(
        not (x&y==x and r&(1<<x)) or r&(1<<y)
        for x in range(8) for y in range(8)))
    assert len(mons)==20

    def flip(r,s):
        return sum(((r>>(x^s))&1)<<x for x in range(8))

    cases=total=probes=failed=reuse=0
    by_d=[0]*4
    for a,b,s,t in product(mons,mons,range(8),range(8)):
        d=s^t
        common=s&~d
        ra,rb=flip(a,s),flip(b,t)
        union=ra|rb
        good=True
        for v in submasks(d):
            x=v|common
            covered=bool(union&(1<<x))
            good &= covered
            probes+=1
            if covered:
                selected=ra if ra&(1<<x) else rb
                for y in range(8):
                    if y&d==x&d:
                        assert selected&(1<<y)
                        reuse+=1
            else:
                failed+=1
        assert good==(union==255)
        cases+=1
        total+=good
        by_d[d.bit_count()]+=1
    assert (cases,total,probes,failed,reuse,by_d)==(
        25600,5712,86400,34872,96528,[3200,9600,9600,3200])
    print(f'F038_SWITCH_DISAGREEMENT_OK relations={len(mons)} cases={cases} '
          f'total={total} probes={probes} failed={failed} reuse_checks={reuse} '
          f'disagreement_counts={",".join(map(str,by_d))}')


def threshold(d,r,negative=False,hole=None):
    assert 1<=r<=d
    top=d
    f=[]

    def fresh():
        nonlocal top
        top+=1
        return top

    def gate(op,a,b):
        c=fresh()
        if op=='and':
            f.extend(((-c,a),(-c,b)))
        else:
            assert op=='or'
            f.append((-c,a,b))
        return c

    yes,no=fresh(),fresh()
    f.append((-no,))
    row=[yes]+[no]*r
    for i in range(1,d+1):
        x=-i if negative else i
        row=[yes]+[gate('or',row[j],gate('and',x,row[j-1]))
                   for j in range(1,r+1)]
    out=row[r]
    if hole is not None:
        assert not negative and hole.bit_count()==r<d
        xs=[i for i in range(1,d+1) if not hole&(1<<(i-1))]
        q=xs[0]
        for x in xs[1:]:
            q=gate('or',q,x)
        out=gate('and',out,q)
    f.append((out,))
    assert all(1<=len(c)<=3 for c in f)
    assert all((l<0)==negative for c in f for l in c if abs(l)<=d)
    return top,tuple(f)


def pin(d,x):
    return {i+1:bool(x&(1<<i)) for i in range(d)}


def concrete():
    dimensions=holes=baseline=checks=distinguished=max_v=max_c=0
    for d in range(2,7):
        r=d//2
        v1,a=threshold(d,r)
        v2,b=threshold(d,d-r+1,True)
        max_v=max(max_v,v1,v2)
        max_c=max(max_c,len(a),len(b))
        for x in range(1<<d):
            av=sat(restrict(a,pin(d,x)))
            bv=sat(restrict(b,pin(d,x)))
            assert (av,bv)==(x.bit_count()>=r,x.bit_count()<r)
            assert av or bv
            baseline+=2
        for s in range(1<<d):
            if s.bit_count()!=r:
                continue
            top,h=threshold(d,r,hole=s)
            max_v=max(max_v,top)
            max_c=max(max_c,len(h))
            for x in range(1<<d):
                got=sat(restrict(h,pin(d,x)))
                want=x.bit_count()>=r and x!=s
                assert got==want
                distinguished+=got!=(x.bit_count()>=r)
                checks+=1
            holes+=1
        # Exercise the actual seed selector on baseline and one hole.
        # Exact finite SAT is only a regression callback, not an efficient solver.
        s=(1<<r)-1
        _,h=threshold(d,r,hole=s)
        for f,expected in (((a,b),True),((h,b),False)):
            def solve(i,pins):
                # Extract a full witness via successive exact finite queries.
                local=f[i]
                if not sat(restrict(local,pins)):
                    return None
                assignment=dict(pins)
                for v in sorted({abs(l) for c in local for l in c}-set(pins)):
                    assignment[v]=False
                    if not sat(restrict(local,assignment)):
                        assignment[v]=True
                assert all(any(assignment[abs(l)]==(l>0) for l in c) for c in local)
                return sum(1<<(v-1) for v,value in assignment.items() if value)
            dm,table=seeds(f,(1<<d)-1,solve)
            assert dm==(1<<d)-1
            assert all(v is not None for v in table.values())==expected
            assert all((v is None)==(not expected and x==s)
                       for x,v in table.items())
        dimensions+=1
    assert (dimensions,holes,baseline,checks,distinguished,max_v,max_c)==(
        5,41,248,1728,41,56,74)
    print(f'F038_SWITCH_QUERY_BARRIER_OK dimensions={dimensions} holes={holes} '
          f'baseline_checks={baseline} hole_checks={checks} '
          f'distinguished={distinguished} max_variables={max_v} max_clauses={max_c}')


if __name__=='__main__':
    abstract()
    concrete()
