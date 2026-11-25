"""Checked case-dependent nonlocal transport for existential SAT choice.

A certificate covers all valuations of a fixed case scope. Each case
is unit-refutable or supplies a signed variable permutation that maps
its models to the requested branch. No general discovery claim.
"""
from itertools import product, permutations
from mathos.research.f037_log_backdoor import normalize, satisfies
from mathos.research.f037_rup_repair import rup
from mathos.research.f037_frozen_model import cover, cnf


def variables(f):
    return {abs(l) for c in f for l in c}


def image(c,p):
    return frozenset((1 if l>0 else -1)*p.get(abs(l),abs(l)) for l in c)


def check_permutation(vs,p):
    return (set(p)<=vs and all(type(l) is int and abs(l) in vs for l in p.values())
            and {abs(p.get(v,v)) for v in vs}==vs)


def implied(f,rows,c):
    if any(-l in c for l in c):
        return True
    # Fast direct implication check, then unit-propagation fallback.
    from itertools import combinations
    a=tuple(c)
    if any(frozenset(s) in rows for k in range(len(a)+1)
           for s in combinations(a,k)):
        return True
    return rup(f,c)


def check(raw,v,b,scope,maps):
    f=normalize(raw)
    vs=variables(f)
    if v not in vs or type(b) is not bool or v not in scope:
        return False
    if len(set(scope))!=len(scope) or not set(scope)<=vs:
        return False
    if len(maps)!=(1<<len(scope)):
        return False
    for bits,p in zip(product((False,True),repeat=len(scope)),maps):
        x=dict(zip(scope,bits))
        g=f+tuple((w if bit else -w,) for w,bit in x.items())
        if p is None:
            if not rup(g,()):
                return False
            continue
        if not check_permutation(vs,p):
            return False
        rows={frozenset(c) for c in g}
        if not implied(g,rows,image((v if b else -v,),p)):
            return False
        if not all(implied(g,rows,image(c,p)) for c in f):
            return False
    return True


def apply(x,p,vs):
    return {v:(x.get(abs(p.get(v,v)),False)==(p.get(v,v)>0)) for v in vs}


def transport(raw,v,b,scope,maps,x):
    assert satisfies(raw,x)
    i=0
    for w in scope:
        i=2*i+int(x.get(w,False))
    p=maps[i]
    assert p is not None
    y=apply(x,p,variables(normalize(raw)))
    assert satisfies(raw,y) and y[v]==b
    return y


def palette(n,p):
    return {3*i+j+1:3*i+p[j]+1 for i in range(n) for j in range(3) if p[j]!=j}


def coloring_certificate(raw,n,vertex,target,permitted=tuple(permutations(range(3)))):
    # This discovers a certificate within a supplied palette vocabulary,
    # not arbitrary signed permutations. Previous pins are unit clauses.
    f=normalize(raw)
    vs=variables(f)
    scope=tuple(3*vertex+j+1 for j in range(3))
    v=scope[target]
    maps=[]
    for bits in product((False,True),repeat=3):
        g=f+tuple((w if bit else -w,) for w,bit in zip(scope,bits))
        if sum(bits)!=1:
            assert rup(g,())
            maps.append(None)
            continue
        if bits[target]:
            maps.append({})
            continue
        rows={frozenset(c) for c in g}
        for p in permitted:
            if not bits[p[target]]:
                continue
            m=palette(n,p)
            if (check_permutation(vs,m) and
                all(implied(g,rows,image(c,m)) for c in f)):
                maps.append(m)
                break
        else:
            if not rup(g,()):
                return None
            maps.append(None)
    assert check(f,v,True,scope,maps)
    return scope,tuple(maps)


def run():
    # Case splitting permits a many-to-one global repair even though
    # each individual permutation is bijective.
    f=cnf(1,[])
    s,m=coloring_certificate(f,1,0,0)
    assert check(f,1,True,s,m)
    original=[dict(zip(s,b)) for b in product((False,True),repeat=3)
              if satisfies(f,dict(zip(s,b)))]
    assert len(original)==3
    assert len({tuple(transport(f,1,True,s,m,x).values()) for x in original})==1
    # The explicit frozen-model instance, then fix an adjacent vertex
    # with the remaining color permutations.
    edges=[(u,v) for u in range(6) for v in range(u+1,6) if u//2!=v//2]
    n,e,colors=cover(6,edges,[0,0,1,1,2,2])
    f=cnf(n,e)
    a,b=e[0]
    v=3*a+1
    s,m=coloring_certificate(f,n,a,0)
    assert check(f,v,True,s,m)
    assert not check(f,v,True,s,m[:-1])
    fake=list(m)
    fake[1]={}
    assert not check(f,v,True,s,fake)
    fake=list(m)
    fake[1]={1:2}
    assert not check(f,v,True,s,fake)
    f2=f+((v,),)
    w=3*b+2
    s2,m2=coloring_certificate(f2,n,b,1,((0,1,2),(0,2,1)))
    assert check(f2,w,True,s2,m2)
    total=0
    for p in permutations(range(3)):
        x={3*i+j+1:p[colors[i]]==j for i in range(n) for j in range(3)}
        y=transport(f,v,True,s,m,x)
        z=transport(f2,w,True,s2,m2,y)
        assert z[v] and z[w] and satisfies(f,z)
        total+=2
    print(f"frozen_variables={3*n} frozen_clauses={len(f)} transports={total}")
    print("F037_CASE_TRANSPORT_OK variables=2304 clauses=7680 choices=2 cases=16 transports=12 rejection=3")


if __name__=="__main__":
    run()
