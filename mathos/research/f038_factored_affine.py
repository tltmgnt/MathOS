"""Exact factored affine-union projection and semantic repair."""
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_hybrid_affine import parity
from mathos.research.f038_affine_separator import span, intersection, signature, equations, lift, clause
from mathos.research.f038_separator_discovery import balanced
from mathos.research.f038_separator_repair import prepare, modified, translation_predicate, model
from mathos.research.f038_symbolic_affine import normalize, project, contains, compress, points


# A relation is None (false), or a tuple of (scope, union) factors.
# An empty tuple represents true.
def factor(W,pieces):
    if not pieces:
        return None
    if pieces==((),):
        return ()
    return ((span(W),pieces),)


def point_factor(W,z):
    p=normalize((v,(z>>i)&1) for i,v in enumerate(W))
    assert p is not None
    return factor(W,(p,))


def holds(R,t):
    return R is not None and all(any(contains(p,t) for p in pieces)
                                 for W,pieces in R)


def coord_basis(factors):
    selected=[]
    rows={}
    for W,_ in factors:
        for v in W:
            a=v
            p=0
            while a:
                bit=a&-a
                if bit not in rows:
                    k=1<<len(selected)
                    selected.append(v)
                    rows[bit]=(a,p^k)
                    break
                b,q=rows[bit]
                a^=b
                p^=q
    def coords(v):
        p=0
        while v:
            bit=v&-v
            b,q=rows[bit]
            v^=b
            p^=q
        return p
    return tuple(selected),coords


def combine(relations,T,n):
    """Return exact projected factored relation, and a witness of inputs."""
    if any(R is None for R in relations):
        return None,None
    fs=tuple(f for R in relations for f in R)
    if not fs:
        return (),0
    K,coords=coord_basis(fs)
    U=span(intersection(K,T,n))
    supports=[]
    for W,_ in fs:
        m=0
        for v in W:
            m|=coords(v)
        assert m
        supports.append(m)
    us=tuple(coords(v) for v in U)
    groups=[1<<i for i in range(len(K))]
    for m in tuple(supports)+us:
        g=m
        for h in groups:
            if h&m:
                g|=h
        groups=[h for h in groups if not h&m]+[g]
    output=[]
    witness=[]
    for g in sorted(groups):
        if not g:
            continue
        local=((),)
        for (W,pieces),m in zip(fs,supports):
            if m&g!=m:
                continue
            new=[]
            for a in local:
                for b in pieces:
                    p=normalize(a+b)
                    if p is not None:
                        new.append(p)
            local=compress(new)
            if not local:
                return None,None
        witness.extend(local[0])
        S=span(v for v,m in zip(U,us) if m&g==m)
        parts=compress(project(p,S,n) for p in local)
        R=factor(S,parts)
        assert R is not None
        output.extend(R)
    t=lift(tuple((v,b,()) for v,b in witness))
    assert t is not None and all(holds(R,t) for R in relations)
    return tuple(sorted(output)),t


def leaf(W,S,pred,n):
    return combine((factor(W,points(W,pred)),),S,n)[0]


def upward(nodes,pred,n):
    up=[]
    for i,(_,W,S,ch) in enumerate(nodes):
        if ch:
            a,b=ch
            R=combine((up[a],up[b]),S,n)[0]
        else:
            R=leaf(W,S,pred[i],n)
        up.append(R)
    return tuple(up)


def downward(nodes,up,n):
    down=[None]*len(nodes)
    down[-1]=()
    for i in reversed(range(len(nodes))):
        _,W,S,ch=nodes[i]
        if ch:
            a,b=ch
            down[a]=combine((down[i],up[b]),nodes[a][2],n)[0]
            down[b]=combine((down[i],up[a]),nodes[b][2],n)[0]
    return tuple(down)


def projection(W,allowed,outside,n):
    return tuple(z for z in sorted(allowed)
                 if combine((outside,point_factor(W,z)),(),n)[0] is not None)


def choose(nodes,pred,up,n):
    if up[-1] is None:
        return None
    restrictions=[]
    def visit(i,z):
        _,W,S,ch=nodes[i]
        pin=point_factor(S,z)
        if not ch:
            y=next(y for y in sorted(pred[i]) if
                   combine((pin,point_factor(W,y)),(),n)[0] is not None)
            restrictions.extend(equations(W,y))
            return
        a,b=ch
        R,t=combine((up[a],up[b],pin),(),n)
        assert R is not None and t is not None
        visit(a,signature(t,nodes[a][2]))
        visit(b,signature(t,nodes[b][2]))
    visit(len(nodes)-1,0)
    d=lift(tuple(restrictions))
    assert d is not None
    return d


def produce(plan,c):
    rows,rest,forms,db,nodes,width,original=plan
    n=len(forms)
    bad=modified(nodes,original,c)
    up=upward(nodes,bad,n)
    down=downward(nodes,up,n)
    pr=tuple(projection(nodes[i][1],bad[i],down[i],n) for i in original)
    qr=tuple(tuple(sorted(translation_predicate(nodes[i][1],original[i],p)))
             for i,p in zip(original,pr))
    pred=dict(zip(original,qr))
    tu=upward(nodes,pred,n)
    d=choose(nodes,pred,tu,n)
    cert=(up,down,pr,qr,tu)
    assert verify_plan(plan,c,d,cert)
    return d,cert


def check_up(nodes,pred,n,up):
    if len(up)!=len(nodes):
        return False
    for i,(_,W,S,ch) in enumerate(nodes):
        if ch:
            a,b=ch
            want=combine((up[a],up[b]),S,n)[0]
        else:
            want=leaf(W,S,pred[i],n)
        if up[i]!=want:
            return False
    return True


def verify_plan(plan,c,d,cert):
    rows,rest,forms,db,nodes,width,original=plan
    n=len(forms)
    if not 0<=c<len(db):
        return False
    up,down,pr,qr,tu=cert
    bad=modified(nodes,original,c)
    if not check_up(nodes,bad,n,up) or len(down)!=len(nodes) or down[-1]!=():
        return False
    for i in reversed(range(len(nodes))):
        _,W,S,ch=nodes[i]
        if ch:
            a,b=ch
            if down[a]!=combine((down[i],up[b]),nodes[a][2],n)[0]:
                return False
            if down[b]!=combine((down[i],up[a]),nodes[b][2],n)[0]:
                return False
    if len(pr)!=len(original) or len(qr)!=len(original):
        return False
    pred={}
    for j,i in enumerate(original):
        W=nodes[i][1]
        if pr[j]!=projection(W,bad[i],down[i],n):
            return False
        want=tuple(sorted(translation_predicate(W,original[i],pr[j])))
        if qr[j]!=want:
            return False
        pred[i]=want
    if not check_up(nodes,pred,n,tu):
        return False
    if d is None:
        return tu[-1] is None
    return tu[-1] is not None and type(d) is int and 0<=d<1<<n and all(
        signature(d,nodes[i][1]) in pred[i] for i in original)


def verify(f,n,c,d,cert,tree=None,budget=None):
    try:
        p=prepare(f,n,tree,budget)
    except (ValueError,TypeError):
        return False
    return p is not None and verify_plan(p,c,d,cert)


def operation_audit():
    spaces=((1,),(2,),(3,),(4,),(5,6),(1,2),(2,4),(1,4))
    cases=checks=empty=0
    for A in spaces:
        for B in spaces:
            for T in spaces:
                for q in range(8):
                    predicates=tuple(tuple(z for z in range(1<<len(W))
                                           if (q+j*3+z*5)%7<4)
                                     for j,W in enumerate((A,B)))
                    X=factor(A,points(A,predicates[0]))
                    Y=factor(B,points(B,predicates[1]))
                    R,t=combine((X,Y),T,3)
                    expected={signature(v,T) for v in range(8) if
                              signature(v,A) in predicates[0] and
                              signature(v,B) in predicates[1]}
                    assert (R is None)==(not expected)
                    assert (t is None)==(not expected)
                    if t is not None:
                        assert holds(X,t) and holds(Y,t)
                    for v in range(8):
                        assert holds(R,v)==(signature(v,T) in expected)
                        checks+=1
                    cases+=1
                    empty+=not expected
    assert (cases,checks,empty)==(4096,32768,832)
    print('F038_FACTORED_PROJECTION_OK cases=4096 membership_checks=32768 empty=832')


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
            d,cert=produce(p,c)
            up,down,pr,qr,tu=cert
            def good(j,t):
                return clause(db[j],forms,t)==(j!=c)
            bad=tuple(t for t in ts if all(good(j,t) for j in range(len(db))))
            empty+=not bad
            for i,(subset,W,S,ch) in enumerate(nodes):
                inside={signature(t,S) for t in ts if all(
                    not subset&(1<<j) or good(j,t) for j in range(len(db)))}
                outside={signature(t,S) for t in ts if all(
                    subset&(1<<j) or good(j,t) for j in range(len(db)))}
                assert all(holds(up[i],t)==(signature(t,S) in inside) for t in ts)
                assert all(holds(down[i],t)==(signature(t,S) in outside) for t in ts)
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


def nae_family(m):
    half=tuple(c for i in range(m) for c in (
        (3*i+1,3*i+2,3*i+3),(-3*i-1,-3*i-2,-3*i-3)))
    f=half+half+((-1,3*m+1),)
    left=balanced([(1<<(2*i),1<<(2*i+1)) for i in range(m)])
    right=balanced([(1<<(2*m+2*i),1<<(2*m+2*i+1)) for i in range(m)])
    return f,3*m+1,((left,right),1<<(4*m))


def high_rank_audit():
    corrupt=0
    for m in (1,2,4,8,16,32):
        f,n,tree=nae_family(m)
        p=prepare(f,n,tree)
        rows,rest,forms,db,nodes,width,original=p
        assert not rows and len(rest)==4*m+1 and width==3*m
        ordinary=upward(nodes,original,n)
        for mask in ((1<<(2*m))-1,((1<<(2*m))-1)<<(2*m)):
            i=next(i for i,node in enumerate(nodes) if node[0]==mask)
            R=ordinary[i]
            assert len(nodes[i][2])==3*m and R is not None and len(R)==m
            assert all(len(W)==3 and len(parts)<=6 for W,parts in R)
        d,cert=produce(p,4*m)
        assert d is not None and verify(f,n,4*m,d,cert,tree)
        # Explicit nonempty bad model and a valid flip of the fresh bit.
        t=sum(1<<(3*i) for i in range(m))
        assert satisfies(f[:-1],t) and not satisfies((f[-1],),t)
        assert satisfies(f,t^d)
        fresh=1<<(3*m)
        assert all(signature(fresh,nodes[i][1]) in cert[3][j]
                   for j,i in enumerate(original))
        data=list(cert)
        pr=list(data[2])
        pr[0]=tuple(sorted(set(pr[0])^{0}))
        data[2]=tuple(pr)
        assert not verify(f,n,4*m,d,tuple(data),tree)
        corrupt+=1
        data=list(cert)
        tu=list(data[4])
        tu[-1]=None
        data[4]=tuple(tu)
        assert not verify(f,n,4*m,d,tuple(data),tree)
        corrupt+=1
    assert corrupt==12
    print('F038_FACTORED_NAE_OK sizes=1,2,4,8,16,32 max_rank=96 '
          'max_half_factors=32 max_pieces_per_factor=6 corrupt_rejected=12')


def audit():
    operation_audit()
    a=audit_fixture(ROWS)
    assert a==(2384,4736,26320,26320,15528,11136,8587,4294,3424)
    print('F038_FACTORED_REPAIR_OK formulas=4096 inconsistent=2384 candidates=4736 '
          'up_checks=26320 down_checks=26320 projections=15528 direction_checks=11136 '
          'valid_directions=8587 repair_exists=4294 bad_empty=3424')
    fixture=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3))
                  for w in range(8))
    a=audit_fixture(fixture)
    assert a==(1,896,6336,6336,3616,6944,3328,896,0)
    print('F038_FACTORED_REPAIR_FULL_OK formulas=256 inconsistent=1 candidates=896 '
          'up_checks=6336 down_checks=6336 projections=3616 direction_checks=6944 '
          'valid_directions=3328 repair_exists=896 bad_empty=0')
    high_rank_audit()


if __name__=='__main__':
    audit()
