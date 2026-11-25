"""ROBDD cylinders for exact affine projection and certified semantic repair."""
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_affine_separator import span, orthogonal, signature, equations, lift, clause
from mathos.research.f038_separator_discovery import balanced
from mathos.research.f038_separator_repair import prepare, modified, translation_predicate, model


class BDD:
    def __init__(self,n):
        self.n=n
        self.nodes=[None,None]
        self.unique={}
        self.cache={}
        self.shifts={}
        self.parities={}

    def node(self,i,l,h):
        if l==h:
            return l
        assert 0<=i<self.n and self.var(l)>i and self.var(h)>i
        key=(i,l,h)
        if key not in self.unique:
            self.unique[key]=len(self.nodes)
            self.nodes.append(key)
        return self.unique[key]

    def var(self,u):
        return self.nodes[u][0] if u>=2 else self.n

    def apply(self,op,a,b):
        if a>b:
            a,b=b,a
        if a==b:
            return a
        if op=='and':
            if a==0:
                return 0
            if a==1:
                return b
        else:
            assert op=='or'
            if a==0:
                return b
            if a==1:
                return 1
        key=(op,a,b)
        if key not in self.cache:
            i=min(self.var(a),self.var(b))
            _,al,ah=self.nodes[a] if self.var(a)==i else (i,a,a)
            _,bl,bh=self.nodes[b] if self.var(b)==i else (i,b,b)
            self.cache[key]=self.node(i,self.apply(op,al,bl),self.apply(op,ah,bh))
        return self.cache[key]

    def shift(self,u,v):
        if u<2 or not v:
            return u
        key=(u,v)
        if key not in self.shifts:
            i,l,h=self.nodes[u]
            if v&(1<<i):
                l,h=h,l
            self.shifts[key]=self.node(i,self.shift(l,v),self.shift(h,v))
        return self.shifts[key]

    def parity(self,a,b):
        if not a:
            return int(b==0)
        key=(a,b)
        if key not in self.parities:
            bit=a&-a
            self.parities[key]=self.node(bit.bit_length()-1,
                self.parity(a^bit,b),self.parity(a^bit,b^1))
        return self.parities[key]

    def point(self,W,z):
        u=1
        for i,a in enumerate(W):
            u=self.apply('and',u,self.parity(a,(z>>i)&1))
        return u

    def allowed(self,W,rows):
        u=0
        for z in sorted(rows):
            u=self.apply('or',u,self.point(W,z))
        return u

    def project(self,u,T):
        for v in orthogonal(T,self.n):
            if u<2:
                break
            u=self.apply('or',u,self.shift(u,v))
        return u

    def join(self,a,b,T):
        return self.project(self.apply('and',a,b),T)

    def holds(self,u,t):
        while u>=2:
            i,l,h=self.nodes[u]
            u=h if t&(1<<i) else l
        return bool(u)

    def witness(self,u):
        if not u:
            return None
        t=0
        while u>=2:
            i,l,h=self.nodes[u]
            if l:
                u=l
            else:
                t|=1<<i
                u=h
        assert u==1
        return t

    def size(self,u):
        seen=set()
        todo=[u]
        while todo:
            v=todo.pop()
            if v<2 or v in seen:
                continue
            seen.add(v)
            _,l,h=self.nodes[v]
            todo.extend((l,h))
        return len(seen)


def upward(B,nodes,pred):
    up=[]
    for i,(_,W,S,ch) in enumerate(nodes):
        if ch:
            a,b=ch
            u=B.join(up[a],up[b],S)
        else:
            u=B.project(B.allowed(W,pred[i]),S)
        up.append(u)
    return tuple(up)


def downward(B,nodes,up):
    down=[None]*len(nodes)
    down[-1]=1
    for i in reversed(range(len(nodes))):
        _,W,S,ch=nodes[i]
        if ch:
            a,b=ch
            down[a]=B.join(down[i],up[b],nodes[a][2])
            down[b]=B.join(down[i],up[a],nodes[b][2])
    return tuple(down)


def projection(B,W,allowed,outside):
    return tuple(z for z in sorted(allowed)
                 if B.apply('and',outside,B.point(W,z)))


def transcript(plan,c):
    rows,rest,forms,db,nodes,width,original=plan
    B=BDD(len(forms))
    bad=modified(nodes,original,c)
    up=upward(B,nodes,bad)
    down=downward(B,nodes,up)
    pr=tuple(projection(B,nodes[i][1],bad[i],down[i]) for i in original)
    qr=tuple(tuple(sorted(translation_predicate(nodes[i][1],original[i],p)))
             for i,p in zip(original,pr))
    pred=dict(zip(original,qr))
    tu=upward(B,nodes,pred)
    cert=(tuple(B.nodes),up,down,pr,qr,tu)
    return B,pred,cert


def choose(B,nodes,pred,up):
    if not up[-1]:
        return None
    restrictions=[]
    def visit(i,z):
        _,W,S,ch=nodes[i]
        pin=B.point(S,z)
        if not ch:
            t=B.witness(B.apply('and',pin,B.allowed(W,pred[i])))
            assert t is not None
            restrictions.extend(equations(W,signature(t,W)))
            return
        a,b=ch
        t=B.witness(B.apply('and',pin,B.apply('and',up[a],up[b])))
        assert t is not None
        visit(a,signature(t,nodes[a][2]))
        visit(b,signature(t,nodes[b][2]))
    visit(len(nodes)-1,0)
    d=lift(tuple(restrictions))
    assert d is not None
    return d


def produce(plan,c):
    B,pred,cert=transcript(plan,c)
    d=choose(B,plan[4],pred,cert[-1])
    assert verify_plan(plan,c,d,cert)
    return d,cert,len(B.nodes)-2


def verify_plan(plan,c,d,cert):
    rows,rest,forms,db,nodes,width,original=plan
    if not 0<=c<len(db):
        return False
    B,pred,want=transcript(plan,c)
    if want!=cert:
        return False
    if d is None:
        return want[-1][-1]==0
    return want[-1][-1]==1 and type(d) is int and 0<=d<1<<len(forms) and all(
        signature(d,nodes[i][1]) in pred[i] for i in original)


def verify(f,n,c,d,cert,tree=None):
    try:
        p=prepare(f,n,tree)
    except (ValueError,TypeError):
        return False
    return p is not None and verify_plan(p,c,d,cert)


def operation_audit():
    spaces=((1,),(2,),(3,),(4,),(5,6),(1,2),(2,4),(1,4))
    cases=checks=empty=0
    for A in spaces:
        for C in spaces:
            for T in spaces:
                for q in range(8):
                    B=BDD(3)
                    p,r=tuple(tuple(z for z in range(1<<len(W))
                                    if (q+j*3+z*5)%7<4)
                              for j,W in enumerate((A,C)))
                    u=B.join(B.allowed(A,p),B.allowed(C,r),T)
                    expected={signature(t,T) for t in range(8)
                              if signature(t,A) in p and signature(t,C) in r}
                    assert (u==0)==(not expected)
                    for t in range(8):
                        assert B.holds(u,t)==(signature(t,T) in expected)
                        checks+=1
                    cases+=1
                    empty+=not expected
    assert (cases,checks,empty)==(4096,32768,832)
    print('F038_OBDD_PROJECTION_OK cases=4096 membership_checks=32768 empty=832')


def audit_fixture(fixture):
    inconsistent=candidates=upchecks=downchecks=projections=directions=valid=exists=empty=0
    for mask in range(1<<len(fixture)):
        f=tuple(c for i,c in enumerate(fixture) if mask&(1<<i))
        p=prepare(f,3)
        if p is None:
            inconsistent+=1
            continue
        rows,rest,forms,db,nodes,width,original=p
        free=span(a for a,b in forms)
        ts=tuple(lift(equations(free,z)) for z in range(1<<len(free)))
        for c in range(len(db)):
            candidates+=1
            d,cert,allocated=produce(p,c)
            raw,up,down,pr,qr,tu=cert
            B=BDD(3)
            B.nodes=list(raw)
            def good(j,t):
                return clause(db[j],forms,t)==(j!=c)
            bad=tuple(t for t in ts if all(good(j,t) for j in range(len(db))))
            empty+=not bad
            for i,(subset,W,S,ch) in enumerate(nodes):
                inside={signature(t,S) for t in ts if all(
                    not subset&(1<<j) or good(j,t) for j in range(len(db)))}
                outside={signature(t,S) for t in ts if all(
                    subset&(1<<j) or good(j,t) for j in range(len(db)))}
                assert all(B.holds(up[i],t)==(signature(t,S) in inside) for t in ts)
                assert all(B.holds(down[i],t)==(signature(t,S) in outside) for t in ts)
                upchecks+=1
                downchecks+=1
            for j,i in enumerate(original):
                assert set(pr[j])=={signature(t,nodes[i][1]) for t in bad}
                projections+=1
            count=0
            for v in ts:
                expected=all(satisfies(f,model(forms,t^v)) for t in bad)
                assert expected==all(signature(v,nodes[i][1]) in qr[j]
                                     for j,i in enumerate(original))
                directions+=1
                count+=expected
                valid+=expected
            assert (d is not None)==bool(count)
            if d is not None:
                assert all(satisfies(f,model(forms,t^d)) for t in bad)
            exists+=bool(count)
    return inconsistent,candidates,upchecks,downchecks,projections,directions,valid,exists,empty


def chain(m):
    half=tuple(c for i in range(m) for c in (
        (2*i+1,2*i+2,2*i+3),(-2*i-1,-2*i-2,-2*i-3)))
    return half,2*m+1


def chain_audit():
    sizes=[]
    counts=[]
    projections=[]
    for m in range(1,7):
        f,n=chain(m)
        B=BDD(n)
        u=1
        for c in f:
            W=tuple(1<<(abs(l)-1) for l in c)
            bad=sum(1<<i for i,l in enumerate(c) if l<0)
            u=B.apply('and',u,B.allowed(W,tuple(z for z in range(8) if z!=bad)))
        good=tuple(t for t in range(1<<n) if satisfies(f,t))
        assert all(B.holds(u,t)==satisfies(f,t) for t in range(1<<n))
        odd=tuple(1<<(2*i+j) for i in range(0,m,2) for j in range(3))
        sizes.append(B.size(u))
        counts.append(len(good))
        projections.append(len({signature(t,odd) for t in good}))
    assert sizes==[5,10,15,20,25,30]
    assert counts==[6,18,54,162,486,1458] and projections==[6,6,36,36,216,216]
    print('F038_OBDD_CHAIN_SMALL_OK sizes=5,10,15,20,25,30 '
          'models=6,18,54,162,486,1458 projections=6,6,36,36,216,216')
    corrupt=0
    for m in (1,2,4,8,16,32):
        half,n=chain(m)
        f=half+half+((-1,n+1),)
        left=balanced([(1<<(2*i),1<<(2*i+1)) for i in range(m)])
        right=balanced([(1<<(2*m+2*i),1<<(2*m+2*i+1)) for i in range(m)])
        tree=((left,right),1<<(4*m))
        p=prepare(f,n+1,tree)
        assert p is not None and p[5]==n and not p[0]
        B=BDD(n+1)
        ordinary=upward(B,p[4],p[-1])
        for mask in ((1<<(2*m))-1,((1<<(2*m))-1)<<(2*m)):
            i=next(i for i,node in enumerate(p[4]) if node[0]==mask)
            assert len(p[4][i][2])==n and B.size(ordinary[i])==5*m
        d,cert,allocated=produce(p,4*m)
        assert d is not None and verify(f,n+1,4*m,d,cert,tree)
        fresh=1<<n
        assert all(signature(fresh,p[4][i][1]) in cert[4][j]
                   for j,i in enumerate(p[-1]))
        t=sum(1<<(2*i) for i in range(m+1))
        assert satisfies(f[:-1],t) and not satisfies((f[-1],),t)
        assert satisfies(f,t^d)
        raw=list(cert[0])
        raw.append((0,0,1))
        assert not verify(f,n+1,4*m,d,(tuple(raw),)+cert[1:],tree)
        data=list(cert)
        data[-1]=data[-1][:-1]+(0,)
        assert not verify(f,n+1,4*m,d,tuple(data),tree)
        corrupt+=2
        assert allocated>=len(cert[0])-2
    print('F038_OBDD_CHAIN_HIGH_OK sizes=1,2,4,8,16,32 max_rank=65 '
          'max_half_nodes=160 corrupt_rejected='+str(corrupt))


def grid_audit():
    counts=[]
    mins=[]
    matches=[]
    for k in (2,3,4):
        n=k*k
        edges=tuple((i,j) for i in range(n) for j in (i+1,i+k)
                    if j<n and (j==i+k or i%k<k-1))
        adj=[{i} for i in range(n)]
        for a,b in edges:
            adj[a].add(b)
            adj[b].add(a)
        count=0
        minimum=len(edges)
        minmatch=len(edges)
        for s in range(1<<n):
            if s.bit_count()!=n//2:
                continue
            cross=[(a,b) for a,b in edges if (s>>a&1)!=(s>>b&1)]
            minimum=min(minimum,len(cross))
            chosen=[]
            while cross:
                a,b=cross[0]
                chosen.append((a,b))
                forbidden=adj[a]|adj[b]
                cross=[(x,y) for x,y in cross if x not in forbidden and y not in forbidden]
            minmatch=min(minmatch,len(chosen))
            count+=1
            prefix=[a if s>>a&1 else b for a,b in chosen]
            suffix=[b if s>>a&1 else a for a,b in chosen]
            f=tuple((a+1,b+1) for a,b in edges)
            # Each residual has a distinct vector of evaluations at the
            # suffix assignments with exactly one matched endpoint zero.
            residuals=set()
            for z in range(1<<len(chosen)):
                w=((1<<n)-1)^sum(1<<a for i,a in enumerate(prefix) if z>>i&1)
                v=tuple(satisfies(f,w^(1<<b)) for b in suffix)
                residuals.add(v)
            assert len(residuals)==1<<len(chosen)
        counts.append(count)
        mins.append(minimum)
        matches.append(minmatch)
    assert (counts,mins,matches)==([6,126,12870],[2,4,4],[1,1,2])
    print('F038_OBDD_GRID_BARRIER_OK sizes=2,3,4 cuts=6,126,12870 '
          'min_cross=2,4,4 min_induced_matching=1,1,2')


def audit():
    operation_audit()
    a=audit_fixture(ROWS)
    assert a==(2384,4736,26320,26320,15528,11136,8587,4294,3424)
    print('F038_OBDD_REPAIR_OK formulas=4096 inconsistent=2384 candidates=4736 '
          'up_checks=26320 down_checks=26320 projections=15528 direction_checks=11136 '
          'valid_directions=8587 repair_exists=4294 bad_empty=3424')
    fixture=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3))
                  for w in range(8))
    a=audit_fixture(fixture)
    assert a==(1,896,6336,6336,3616,6944,3328,896,0)
    print('F038_OBDD_REPAIR_FULL_OK formulas=256 inconsistent=1 candidates=896 '
          'up_checks=6336 down_checks=6336 projections=3616 direction_checks=6944 '
          'valid_directions=3328 repair_exists=896 bad_empty=0')
    chain_audit()
    grid_audit()


if __name__=='__main__':
    audit()
