"""Explicit parity selector, proof-support invariant and finite regression."""
from collections import defaultdict
from itertools import product


def split_cube(d):
    n=1<<d
    edges=[]
    for v in range(n):
        edges.extend((v*d+j,v*d+j+1) for j in range(d-1))
        edges.extend((v*d+j,(v^(1<<j))*d+j)
                     for j in range(d) if not v&(1<<j))
    return n*d,tuple(edges)


def parity(w,edges):
    z=0
    for i,(a,b) in enumerate(edges):
        if w&(1<<i):
            z^=(1<<a)|(1<<b)
    return z


def encode(n,edges,charge):
    f=[]
    for v in range(n):
        inc=[i+1 for i,e in enumerate(edges) if v in e]
        if v==0:
            inc.append(len(edges)+1)
        assert len(inc)<=3
        for a in range(1<<len(inc)):
            if (a.bit_count()&1)!=((charge>>v)&1):
                f.append(tuple(-j if a&(1<<i) else j for i,j in enumerate(inc)))
    return tuple(f)


def satisfies(f,w):
    return all(any(bool(w&(1<<(abs(l)-1)))==(l>0) for l in c) for c in f)


def parse_witness(f,zvar):
    """Recover parity groups and solve the promised graph family."""
    groups=defaultdict(list)
    for c in f:
        groups[tuple(sorted(abs(l) for l in c))].append(c)
    scopes=list(groups)
    incidence=defaultdict(list)
    charge=0
    for i,scope in enumerate(scopes):
        cs=groups[scope]
        bad={sum(1<<scope.index(abs(l)) for l in c if l<0) for c in cs}
        assert len(bad)==1<<(len(scope)-1)
        p=next(iter(bad)).bit_count()&1
        assert all(a.bit_count()&1==p for a in bad)
        charge|=(1-p)<<i
        for v in scope:
            incidence[v].append(i)
    assert len(incidence[zvar])==1
    root=incidence[zvar][0]
    z=charge.bit_count()&1
    if z:
        charge^=1<<root
    adj=[[] for _ in scopes]
    for e,ends in incidence.items():
        if e==zvar:
            continue
        assert len(ends)==2
        a,b=ends
        adj[a].append((b,e))
        adj[b].append((a,e))
    order=[root]
    seen={root}
    parent={}
    for a in order:
        for b,e in adj[a]:
            if b not in seen:
                seen.add(b)
                order.append(b)
                parent[b]=(a,e)
    assert len(seen)==len(scopes)
    w=z<<(zvar-1)
    for v in reversed(order[1:]):
        if charge&(1<<v):
            a,e=parent[v]
            w|=1<<(e-1)
            charge^=(1<<a)|(1<<v)
    assert charge==0 and satisfies(f,w)
    return z,w


def submasks(mask):
    a=mask
    while True:
        yield a
        if a==0:
            return
        a=(a-1)&mask


def boundary(u,edges):
    return sum(1<<i for i,(v,w) in enumerate(edges)
               if ((u>>v)^(u>>w))&1)


def support_audit(n,edges,pars):
    full=(1<<n)-1
    m=len(edges)
    clauses=supports=cuts=0
    for u in range(full+1):
        if n<=3*u.bit_count()<=2*n:
            assert boundary(u,edges)
            cuts+=1
    for pos in range(1<<m):
        for neg in submasks(((1<<m)-1)^pos):
            # A normalized clause is false iff all its positive bits are
            # zero and all its negative bits are one. Odd charge is 1.
            possible=set()
            for w,p in enumerate(pars):
                if not w&pos and w&neg==neg:
                    possible.update(submasks(full^(p^1)))
            for u in range(full+1):
                if u not in possible and all(
                    not u&(1<<i) or u^(1<<i) in possible for i in range(n)):
                    assert not boundary(u,edges)&~(pos|neg)
                    supports+=1
            clauses+=1
    assert clauses==3**m
    return clauses,supports,cuts


def audit():
    graphs=charges=branches=assignments=witnesses=clauses=supports=cuts=0
    cube_cuts=max_e=max_c=0
    fixtures=((3,((0,1),(1,2),(0,2))),
              (4,((0,1),(1,2),(2,3),(3,0))),
              split_cube(1),split_cube(2))
    for n,edges in fixtures:
        m=len(edges)
        pars=tuple(parity(w,edges) for w in range(1<<m))
        assert set(pars)=={x for x in range(1<<n) if x.bit_count()%2==0}
        for c in range(1<<n):
            f=encode(n,edges,c)
            z=c.bit_count()&1
            for b in (0,1):
                found=False
                for w,p in enumerate(pars):
                    got=satisfies(f,w|(b<<m))
                    assert got==(p==c^b)
                    found|=got
                    assignments+=1
                assert found==(b==z)
                branches+=1
            got,w=parse_witness(f,m+1)
            assert got==z and satisfies(f,w)
            witnesses+=1
            charges+=1
            max_c=max(max_c,len(f))
        a,b,c=support_audit(n,edges,pars)
        clauses+=a
        supports+=b
        cuts+=c
        graphs+=1
        max_e=max(max_e,m)
    for d in range(1,4):
        n=1<<d
        es=tuple((v,v^(1<<j)) for v in range(n) for j in range(d)
                 if not v&(1<<j))
        for a in range(1<<n):
            assert boundary(a,es).bit_count()>=min(a.bit_count(),n-a.bit_count())
            cube_cuts+=1
    assert (graphs,charges,branches,assignments,witnesses,clauses,supports,
            cuts,cube_cuts,max_e,max_c)==(
        4,284,568,131728,284,6672,17652,196,276,8,18)
    print(f'F038_RESOLUTION_CERTIFICATE_OK graphs={graphs} charges={charges} '
          f'branch_checks={branches} assignments={assignments} witnesses={witnesses} '
          f'clauses={clauses} minimal_supports={supports} balanced_cuts={cuts} '
          f'cube_cuts={cube_cuts} max_edges={max_e} max_clauses={max_c}')


if __name__=='__main__':
    audit()
