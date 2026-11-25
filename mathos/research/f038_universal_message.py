"""Universal exact boundary family and finite encoding checks."""
from itertools import combinations, product
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_hybrid_affine import extract, verify_partition
from mathos.research.f038_affine_separator import span, intersection
from mathos.research.f038_separator_discovery import balanced
from mathos.research.f038_separator_repair import prepare, upward


def universe(n):
    return tuple(tuple(v if bit else -v for v,bit in zip(vs,bits))
                 for k in range(1,min(3,n)+1)
                 for vs in combinations(range(1,n+1),k)
                 for bits in product((0,1),repeat=k))


def build(rows,n):
    m=len(rows)
    s=sum(len(c)==3 for c in rows)
    top=m+n
    inside=[]
    groups=[]
    for j,D in enumerate(rows,1):
        c=tuple((m+abs(l)) if l>0 else -(m+abs(l)) for l in D)
        if len(c)==3:
            top+=1
            g=((-j,c[0],top),(-top,c[1],c[2]))
        else:
            g=((-j,)+c,)
        groups.append(g)
        inside.extend(g)
    assert top==m+n+s
    outside=tuple((j,top+j) for j in range(1,m+1))
    f=tuple(inside)+outside
    return f,top+m,len(inside),tuple(groups)


def fixture_audit(rows,n):
    f,total,k,groups=build(rows,n)
    m=len(rows)
    s=sum(len(c)==3 for c in rows)
    assert total==n+2*m+s and len(f)==2*m+s
    a,rest=extract(f)
    assert not a and rest==tuple(range(len(f))) and verify_partition(f,a,rest)
    U=span(1<<(abs(l)-1) for c in f[:k] for l in c)
    V=span(1<<(abs(l)-1) for c in f[k:] for l in c)
    assert span(intersection(U,V,total))==tuple(1<<i for i in range(m))
    yes=no=checks=valid=ext_trials=ext_valid=anchors=0
    projected=set()
    anchor_mask=((1<<m)-1)<<(m+n+s)
    for p in range(1<<m):
        D=tuple(c for i,c in enumerate(rows) if p&(1<<i))
        assert satisfies(f[k:],p|anchor_mask)
        anchors+=m
        hit=False
        for x in range(1<<n):
            direct=satisfies(D,x)
            count=0
            for u in range(1<<s):
                w=p|(x<<m)|(u<<(m+n))
                count+=satisfies(f[:k],w)
                ext_trials+=1
            assert bool(count)==direct
            hit|=direct
            checks+=1
            valid+=direct
            ext_valid+=count
        yes+=hit
        no+=not hit
        if hit:
            projected.add(p)
    return (yes,no,checks,valid,ext_trials,ext_valid,anchors),projected


def tree_audit(rows,n,expected):
    f,total,k,groups=build(rows,n)
    tree=(balanced([1<<i for i in range(k)]),
          balanced([1<<i for i in range(k,len(f))]))
    p=prepare(f,total,tree)
    assert p is not None and not p[0]
    nodes=p[4]
    i=next(i for i,node in enumerate(nodes) if node[0]==(1<<k)-1)
    assert nodes[i][2]==tuple(1<<j for j in range(len(rows)))
    up=upward(nodes,p[-1])
    assert up[i]==expected and up[-1]=={0}


def audit():
    a,_=fixture_audit(ROWS,3)
    assert a==(1360,2736,32768,2304,524288,11520,49152)
    print('F038_UNIVERSAL_MESSAGE_OK selections=4096 sat=1360 unsat=2736 '
          'witness_checks=32768 valid_witnesses=2304 extension_trials=524288 '
          'valid_extensions=11520 anchor_checks=49152')
    rows=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3))
               for w in range(8))
    a,_=fixture_audit(rows,3)
    assert a==(255,1,2048,1024,524288,27648,2048)
    print('F038_UNIVERSAL_MESSAGE_FULL_OK selections=256 sat=255 unsat=1 '
          'witness_checks=2048 valid_witnesses=1024 extension_trials=524288 '
          'valid_extensions=27648 anchor_checks=2048')
    rows=universe(2)
    a,expected=fixture_audit(rows,2)
    assert a==(95,161,1024,128,1024,128,2048)
    print('F038_UNIVERSAL_MESSAGE_2VAR_OK selections=256 sat=95 unsat=161 '
          'witness_checks=1024 valid_witnesses=128 extension_trials=1024 '
          'valid_extensions=128 anchor_checks=2048')
    a,small=fixture_audit(universe(1),1)
    assert a==(3,1,8,4,8,4,8)
    tree_audit(universe(1),1,small)
    tree_audit(rows,2,expected)
    sizes=[]
    for n in range(1,6):
        R=universe(n)
        f,total,k,groups=build(R,n)
        m=len(R)
        s=sum(len(c)==3 for c in R)
        assert len(set(R))==m and len(f)==2*m+s and total==n+2*m+s
        a,rest=extract(f)
        assert not a and verify_partition(f,a,rest)
        inside={abs(l) for c in f[:k] for l in c}
        outside={abs(l) for c in f[k:] for l in c}
        assert inside&outside==set(range(1,m+1))
        sizes.append(m)
    assert sizes==[2,8,26,64,130]
    print('F038_UNIVERSAL_MESSAGE_TREE_OK sizes=1,2,3,4,5 '
          'presence_bits=2,8,26,64,130 actual_tables=2,8 '
          'table_rows=3,95')


if __name__=='__main__':
    audit()
