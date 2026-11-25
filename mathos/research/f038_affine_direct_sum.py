"""Affine direct-sum components, exact local witnesses and UNSAT table certificates."""
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_hybrid_affine import extract, verify_partition, reduce, combination, parity, dimension


def bits(mask):
    while mask:
        b=mask&-mask
        mask^=b
        yield b


def submasks(mask):
    v=0
    while True:
        yield v
        v=(v-mask)&mask
        if not v:
            return


def coordinate_forms(rows,n):
    basis,bad=reduce(rows)
    if basis is None:
        return None,bad
    forms=[]
    for i in range(n):
        bit=1<<i
        if bit in basis:
            a,b,_=basis[bit]
            forms.append((a^bit,b))
        else:
            forms.append((bit,0))
    return tuple(forms),None


def plan(f,n,rows,rest):
    forms,bad=coordinate_forms(rows,n)
    if forms is None:
        return None,bad
    db=tuple(f[i] for i in rest)
    interface=sorted({abs(l) for c in db for l in c})
    span={}
    selected=[]
    coords={}
    for i in interface:
        a,b=forms[i-1]
        v=a
        p=0
        while v:
            bit=v&-v
            if bit not in span:
                k=1<<len(selected)
                selected.append(a)
                span[bit]=(v,p^k)
                p=k
                break
            c,q=span[bit]
            v^=c
            p^=q
        coords[i]=(p,b)
    r=len(selected)
    assert r==dimension(rows,db,n)
    groups=[1<<i for i in range(r)]
    scopes=[]
    for c in db:
        support=0
        for l in c:
            support|=coords[abs(l)][0]
        scopes.append(support)
        if support:
            merged=support
            for g in groups:
                if g&support:
                    merged|=g
            groups=[g for g in groups if not g&support]+[merged]
    blocks=tuple((g,tuple(i for i,s in enumerate(scopes) if s and s&g==s))
                 for g in sorted(groups))
    constants=tuple(i for i,s in enumerate(scopes) if not s)
    assert sum(g.bit_count() for g,_ in blocks)==r
    assert sorted([i for _,ids in blocks for i in ids]+list(constants))==list(range(len(db)))
    return (forms,tuple(selected),coords,db,blocks,constants),None


def clause_true(c,coords,z):
    return any((parity(coords[abs(l)][0]&z)^coords[abs(l)][1])==int(l>0)
               for l in c)


def reconstruct(forms,selected,z):
    pins=tuple((a,(z>>i)&1,()) for i,a in enumerate(selected))
    basis,bad=reduce(pins)
    assert bad is None
    t=sum(bit for bit,(_,b,_) in basis.items() if b)
    return sum(1<<i for i,(a,b) in enumerate(forms) if parity(a&t)^b)


def verify_negative(f,n,rows,rest,cert):
    if not verify_partition(f,rows,rest):
        return False
    kind,data=cert
    if kind=='xor':
        return combination(rows,data)==(0,1)
    p,bad=plan(f,n,rows,rest)
    if p is None:
        return False
    forms,selected,coords,db,blocks,constants=p
    if kind=='constant':
        return data in constants and not clause_true(db[data],coords,0)
    if kind!='block':
        return False
    g,table=data
    ids=next((ids for h,ids in blocks if h==g),None)
    if ids is None or len(table)!=1<<g.bit_count():
        return False
    allowed=set(ids)
    return all(i in allowed and not clause_true(db[i],coords,z)
               for z,i in zip(submasks(g),table))


def solve(f,n):
    rows,rest=extract(f)
    assert verify_partition(f,rows,rest)
    p,bad=plan(f,n,rows,rest)
    if p is None:
        cert=('xor',bad)
        assert verify_negative(f,n,rows,rest,cert)
        return None,cert,None,0,0
    forms,selected,coords,db,blocks,constants=p
    cert=None
    for i in constants:
        if not clause_true(db[i],coords,0):
            cert=('constant',i)
            break
    probes=failed=0
    chosen=0
    # Full local enumeration is deliberate, so the audit records exact coverage.
    for g,ids in blocks:
        hit=None
        table=[]
        for z in submasks(g):
            probes+=1
            false=next((i for i in ids if not clause_true(db[i],coords,z)),None)
            table.append(false)
            if false is None:
                if hit is None:
                    hit=z
            else:
                failed+=1
        if hit is None:
            if cert is None:
                cert=('block',(g,tuple(table)))
        else:
            chosen|=hit
    if cert is not None:
        assert verify_negative(f,n,rows,rest,cert)
        return None,cert,p,probes,failed
    w=reconstruct(forms,selected,chosen)
    assert satisfies(f,w)
    return w,None,p,probes,failed


def audit_fixture(fixture):
    yes=no=inconsistent=blocks=constants=probes=failed=witnesses=0
    max_rank=max_block=rank_sum=projection_checks=certificates=0
    for mask in range(1<<len(fixture)):
        f=tuple(c for i,c in enumerate(fixture) if mask&(1<<i))
        w,cert,p,pr,fa=solve(f,3)
        models=tuple(x for x in range(8) if satisfies(f,x))
        assert (w is not None)==bool(models)
        if w is not None:
            assert w in models and cert is None
            yes+=1
            witnesses+=1
        else:
            assert cert is not None
            no+=1
            certificates+=1
        if p is None:
            inconsistent+=1
            continue
        forms,selected,coords,db,groups,cs=p
        r=len(selected)
        rank_sum+=r
        max_rank=max(max_rank,r)
        max_block=max([max_block]+[g.bit_count() for g,_ in groups])
        blocks+=len(groups)
        constants+=len(cs)
        probes+=pr
        failed+=fa
        rows,rest=extract(f)
        affine=tuple(x for x in range(8) if all(parity(x&a)==b for a,b,_ in rows))
        interface=sorted(coords)
        projected=set()
        for z in range(1<<r):
            x=reconstruct(forms,selected,z)
            assert x in affine
            expected=tuple(parity(coords[i][0]&z)^coords[i][1] for i in interface)
            assert expected==tuple((x>>(i-1))&1 for i in interface)
            projected.add(expected)
            assert satisfies(db,x)==all(clause_true(c,coords,z) for c in db)
            projection_checks+=1
        assert projected=={tuple((x>>(i-1))&1 for i in interface) for x in affine}
    return (yes,no,inconsistent,blocks,constants,probes,failed,witnesses,
            max_rank,max_block,rank_sum,projection_checks,certificates)


def connected(m,contradict=False):
    f=[]
    for i in range(m):
        a,b,c=3*i+1,3*i+2,3*i+3
        f.extend(((-a,b),(a,-b),(-a,c),(a,-c),(a,b,c)))
        if contradict and i==m-1:
            f.append((-a,-b,-c))
    for i in range(m-1):
        scope=(3*i+1,3*(i+1)+1,3*m+i+1)
        for w in (1,2,4,7):
            f.append(tuple(-v if w&(1<<j) else v for j,v in enumerate(scope)))
    return tuple(f),4*m-1


def audit():
    a=audit_fixture(ROWS)
    assert a==(1360,2736,2384,1136,1680,3312,1344,1360,3,3,1599,3890,2736)
    print('F038_AFFINE_DIRECT_SUM_OK formulas=4096 sat=1360 unsat=2736 '
          'inconsistent=2384 blocks=1136 constants=1680 probes=3312 failed=1344 '
          'witnesses=1360 max_rank=3 max_block=3 rank_sum=1599 '
          'projection_checks=3890 certificates=2736')
    fixture=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3))
                  for w in range(8))
    a=audit_fixture(fixture)
    assert a==(255,1,1,252,0,1904,896,255,3,3,728,1907,1)
    print('F038_AFFINE_DIRECT_SUM_FULL_OK formulas=256 sat=255 unsat=1 '
          'inconsistent=1 blocks=252 constants=0 probes=1904 failed=896 '
          'witnesses=255 max_rank=3 max_block=3 rank_sum=728 '
          'projection_checks=1907 certificates=1')
    for m in (2,4,8,16,32):
        for bad in (False,True):
            f,n=connected(m,bad)
            w,cert,p,probes,failed=solve(f,n)
            assert p is not None
            forms,selected,coords,db,groups,constants=p
            assert len(selected)==len(groups)==m and not constants
            assert all(g.bit_count()==1 for g,_ in groups)
            assert probes==2*m
            if bad:
                assert w is None and cert[0]=='block' and failed==m+1
                rows,rest=extract(f)
                g,table=cert[1]
                assert verify_negative(f,n,rows,rest,cert)
                assert not verify_negative(f,n,rows,rest,('block',(g,table[:-1])))
                assert not verify_negative(f,n,rows,rest,('block',(g,(-1,)+table[1:])))
            else:
                assert w==(1<<(3*m))-1 and cert is None and failed==m
    print('F038_AFFINE_DIRECT_SUM_CONNECTED_OK sizes=2,4,8,16,32 '
          'instances=10 max_global_rank=32 max_block_rank=1 '
          'corrupt_rejected=10')


if __name__=='__main__':
    audit()
