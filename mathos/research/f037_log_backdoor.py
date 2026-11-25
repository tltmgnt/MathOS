"""Decision-specific component backdoors to 2-CNF.

Known parameterized technique; no unrestricted SAT completeness claim.
UNSAT certificates cover one component and every backdoor assignment.
SAT answers include a checked finite model. UNKNOWN is distinct.
"""
from collections import deque
from itertools import product


def normalize(f):
    rows=[]
    for c in f:
        assert all(type(l) is int and l for l in c)
        c=tuple(sorted(set(c)))
        if not any(-l in c for l in c):
            rows.append(c)
    return tuple(rows)


def components(f):
    adj={}
    for c in f:
        if not c:
            continue
        u=abs(c[0])
        for l in c:
            v=abs(l)
            adj.setdefault(u,set()).add(v)
            adj.setdefault(v,set()).add(u)
    owner={}
    groups=[]
    for u in sorted(adj):
        if u in owner:
            continue
        q=[u]
        owner[u]=len(groups)
        for v in q:
            for w in sorted(adj[v]):
                if w not in owner:
                    owner[w]=len(groups)
                    q.append(w)
        groups.append([])
    for i,c in enumerate(f):
        if c:
            groups[owner[abs(c[0])]].append(i)
    return tuple(tuple(g) for g in groups)


def hit(rows,k):
    if not rows:
        return ()
    if k==0:
        return None
    for v in sorted(map(abs,rows[0])):
        tail=hit(tuple(c for c in rows if v not in map(abs,c)),k-1)
        if tail is not None:
            return (v,)+tail
    return None


def restrict(f,x):
    return tuple(tuple(l for l in c if abs(l) not in x) for c in f
                 if not any(abs(l) in x and x[abs(l)]==(l>0) for l in c))


def arcs(f):
    g={}
    for c in f:
        assert 1<=len(c)<=2
        u,v=c[0],c[-1]
        g.setdefault(-u,set()).add(v)
        g.setdefault(-v,set()).add(u)
    return g


def path(g,s,t):
    q=deque([s])
    prev={s:None}
    while q:
        u=q.popleft()
        if u==t:
            out=[]
            while u is not None:
                out.append(u)
                u=prev[u]
            return tuple(reversed(out))
        for v in sorted(g.get(u,())):
            if v not in prev:
                prev[v]=u
                q.append(v)
    return None


def conflict(f):
    if () in f:
        return ('empty',)
    g=arcs(f)
    for v in sorted({abs(l) for c in f for l in c}):
        p=path(g,v,-v)
        if p is not None:
            q=path(g,-v,v)
            if q is not None:
                return ('paths',p,q)
    return None


def check_leaf(f,p):
    if any(len(c)>2 for c in f):
        return False
    if p==('empty',):
        return () in f
    if () in f or len(p)!=3 or p[0]!='paths':
        return False
    _,a,b=p
    if not a or not b or a[0]!=-a[-1] or b[0]!=a[-1] or b[-1]!=a[0]:
        return False
    g=arcs(f)
    return all(v in g.get(u,()) for seq in (a,b) for u,v in zip(seq,seq[1:]))


def model(f):
    # Called only for a satisfiable 2-CNF. Self-reduction avoids
    # relying on a particular SCC ordering or arbitrary model choice.
    x={}
    g=f
    for v in sorted({abs(l) for c in f for l in c}):
        test=g+((-v,),)
        if conflict(test) is None:
            x[v]=False
            g=test
        else:
            x[v]=True
            g=g+((v,),)
    assert satisfies(f,x)
    return x


def satisfies(f,x):
    return all(any(x.get(abs(l),False)==(l>0) for l in c) for c in f)


def check_unsat(f,cert):
    f=normalize(f)
    indices,B,proofs=cert
    if (not indices or len(set(indices))!=len(indices)
            or any(not 0<=i<len(f) for i in indices)
            or len(set(B))!=len(B) or any(v<=0 for v in B)):
        return False
    g=tuple(f[i] for i in indices)
    if len(proofs)!=(1<<len(B)):
        return False
    return all(check_leaf(restrict(g,dict(zip(B,bits))),p)
               for bits,p in zip(product((False,True),repeat=len(B)),proofs))


def decide(raw,k):
    assert k>=0
    raw=tuple(tuple(c) for c in raw)
    f=normalize(raw)
    if () in f:
        cert=((f.index(()),),(),(('empty',),))
        assert check_unsat(raw,cert)
        return 'UNSAT',cert
    x={}
    unknown=False
    for indices in components(f):
        g=tuple(f[i] for i in indices)
        B=hit(tuple(c for c in g if len(c)>2),k)
        if B is None:
            unknown=True
            continue
        proofs=[]
        for bits in product((False,True),repeat=len(B)):
            fixed=dict(zip(B,bits))
            h=restrict(g,fixed)
            p=conflict(h)
            if p is None:
                x.update(fixed)
                x.update(model(h))
                break
            proofs.append(p)
        else:
            cert=(indices,B,tuple(proofs))
            assert check_unsat(raw,cert)
            return 'UNSAT',cert
    if unknown:
        return 'UNKNOWN',None
    assert satisfies(raw,x)
    return 'SAT',x


def run():
    rows=((),(1,),(-1,),(2,3),(1,-1),(1,1,1),
          (-1,-2,-3),(-1,-2,3),(1,2,-3),(1,2,3),(2,1),(1,2))
    counts={}
    for m in range(1<<len(rows)):
        f=tuple(c for j,c in enumerate(rows) if m&(1<<j))
        sat=any(satisfies(f,dict(zip((1,2,3),bits)))
                for bits in product((False,True),repeat=3))
        for k in range(3):
            result,evidence=decide(f,k)
            counts[k,result]=counts.get((k,result),0)+1
            if result=='SAT':
                assert sat and satisfies(f,evidence)
            elif result=='UNSAT':
                assert not sat and check_unsat(f,evidence)
    assert counts=={(0,'SAT'):80,(0,'UNSAT'):2096,(0,'UNKNOWN'):1920,
                    (1,'SAT'):1280,(1,'UNSAT'):2816,
                    (2,'SAT'):1280,(2,'UNSAT'):2816}
    blocks=tuple((3*j+1,3*j+2,3*j+3) for j in range(128))
    assert decide(blocks,1)[0]=='SAT'
    assert decide(blocks,0)[0]=='UNKNOWN'
    # An unsupported component must not hide a separate contradiction.
    f=blocks+((10000,),(-10000,))
    status,cert=decide(f,0)
    assert status=='UNSAT' and check_unsat(f,cert)
    indices,B,proofs=cert
    assert not check_unsat(f,(indices,B,()))
    assert not check_unsat(f,(indices,B,(('empty',),)))
    # OBDD-hard family from the preceding note: decision at budget zero.
    d=8
    cube=tuple((u+1,(u^(1<<j))+1) for u in range(1<<d)
               for j in range(d) if u<(u^(1<<j)))
    assert decide(cube,0)[0]=='SAT'
    print('F037_LOG_BACKDOOR_OK formulas=4096 budgets=3 components=128 cube=256 rejection=2')


if __name__=='__main__':
    run()
