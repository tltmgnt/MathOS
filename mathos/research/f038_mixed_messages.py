"""Certified heterogeneous affine messages with local representation switching."""
from itertools import product
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_affine_separator import signature, equations, lift, span, clause
from mathos.research.f038_separator_discovery import balanced
from mathos.research.f038_separator_repair import prepare, modified, translation_predicate, model
from mathos.research import f038_factored_affine as F
from mathos.research.f038_symbolic_affine import points
from mathos.research.f038_affine_obdd import BDD, chain
from mathos.research.f038_certified_portfolio import metered, schedule


TAGS=('table','factored','obdd')


def table(W,rows):
    return ('table',tuple(W),tuple(sorted(set(rows))))


def pack(B,u):
    ids={0:0,1:1}
    out=[]
    def visit(v):
        if v not in ids:
            i,l,h=B.nodes[v]
            a,b=visit(l),visit(h)
            ids[v]=len(out)+2
            out.append((i,a,b))
        return ids[v]
    root=visit(u)
    return tuple(out),root


def import_bdd(B,payload):
    raw,root=payload
    ids=[0,1]
    for i,l,h in raw:
        ids.append(B.node(i,ids[l],ids[h]))
    return ids[root]


def to_bdd(B,M):
    kind,W,p=M
    if kind=='obdd':
        return import_bdd(B,p)
    if kind=='table':
        return B.allowed(W,p)
    assert kind=='factored'
    if p is None:
        return 0
    u=1
    for S,pieces in p:
        v=0
        for flat in pieces:
            z=1
            for a,b in flat:
                z=B.apply('and',z,B.parity(a,b))
            v=B.apply('or',v,z)
        u=B.apply('and',u,v)
    return u


def holds(M,t,n):
    kind,W,p=M
    if kind=='table':
        return signature(t,W) in p
    if kind=='factored':
        return F.holds(p,t)
    B=BDD(n)
    return B.holds(import_bdd(B,p),t)


def to_table(M,n):
    kind,W,p=M
    if kind=='table':
        return p
    if kind=='obdd':
        B=BDD(n)
        u=import_bdd(B,p)
        test=lambda t:B.holds(u,t)
    else:
        assert kind=='factored'
        test=lambda t:F.holds(p,t)
    return tuple(z for z in range(1<<len(W)) if test(lift(equations(W,z))))


def convert(M,tag,n):
    if M[0]==tag:
        return M
    _,W,p=M
    if tag=='table':
        return table(W,to_table(M,n))
    if tag=='factored':
        return (tag,W,F.factor(W,points(W,to_table(M,n))))
    if tag=='obdd':
        B=BDD(n)
        return (tag,W,pack(B,to_bdd(B,M)))
    raise ValueError('unknown representation')


def operation(inputs,T,n,tag):
    T=tuple(T)
    if tag=='table':
        rs=tuple(to_table(M,n) for M in inputs)
        rows=set()
        for combo in product(*rs):
            eq=tuple(e for M,z in zip(inputs,combo) for e in equations(M[1],z))
            if lift(eq) is None:
                continue
            for z in range(1<<len(T)):
                if lift(eq+equations(T,z)) is not None:
                    rows.add(z)
        return table(T,rows)
    if tag=='factored':
        rs=tuple(convert(M,tag,n)[2] for M in inputs)
        return (tag,T,F.combine(rs,T,n)[0])
    if tag=='obdd':
        B=BDD(n)
        u=1
        for M in inputs:
            u=B.apply('and',u,to_bdd(B,M))
        return (tag,T,pack(B,B.project(u,T)))
    raise ValueError('unknown representation')


def bounded_join(inputs,T,n,cap):
    # Each accepted local operation includes a deterministic replay.
    def attempt(tag,budget):
        def work():
            M=operation(inputs,T,n,tag)
            if M!=operation(inputs,T,n,tag):
                return 'rejected',None
            return 'positive',M
        return metered(work,budget)
    return schedule(TAGS,attempt,cap)


def policy(i,inputs,T):
    # Small messages rotate between representations; avoid enumerating a
    # high-rank boundary just to convert it to a table in this prototype.
    if max([len(T)]+[len(M[1]) for M in inputs])>4:
        return 'obdd'
    return TAGS[i%len(TAGS)]


def compute(plan,c,select):
    rows,rest,forms,db,nodes,width,original=plan
    n=len(forms)
    bad=modified(nodes,original,c)
    log=[]
    def op(inputs,T):
        tag=select(len(log),inputs,T)
        M=operation(inputs,T,n,tag)
        log.append(M)
        return M
    def upward(pred):
        out=[]
        for i,(_,W,S,ch) in enumerate(nodes):
            if ch:
                a,b=ch
                out.append(op((out[a],out[b]),S))
            else:
                out.append(op((table(W,pred[i]),),S))
        return tuple(out)
    up=upward(bad)
    down=[None]*len(nodes)
    down[-1]=table((),(0,))
    for i in reversed(range(len(nodes))):
        _,W,S,ch=nodes[i]
        if ch:
            a,b=ch
            down[a]=op((down[i],up[b]),nodes[a][2])
            down[b]=op((down[i],up[a]),nodes[b][2])
    pr=[]
    qr=[]
    for i in original:
        W=nodes[i][1]
        observed=tuple(z for z in sorted(bad[i]) if holds(
            op((down[i],table(W,(z,))),()),0,n))
        pr.append(observed)
        qr.append(tuple(sorted(translation_predicate(W,original[i],observed))))
    pred=dict(zip(original,qr))
    tu=upward(pred)
    cert=(tuple(log),tuple(pr),tuple(qr))
    return cert,up,tuple(down),tu,pred


def choose(plan,tu,pred):
    nodes=plan[4]
    n=len(plan[2])
    if not holds(tu[-1],0,n):
        return None
    eq=[]
    def visit(i,z):
        _,W,S,ch=nodes[i]
        B=BDD(n)
        u=B.point(S,z)
        if ch:
            a,b=ch
            u=B.apply('and',u,to_bdd(B,tu[a]))
            u=B.apply('and',u,to_bdd(B,tu[b]))
            t=B.witness(u)
            assert t is not None
            visit(a,signature(t,nodes[a][2]))
            visit(b,signature(t,nodes[b][2]))
        else:
            t=B.witness(B.apply('and',u,B.allowed(W,pred[i])))
            assert t is not None
            eq.extend(equations(W,signature(t,W)))
    visit(len(nodes)-1,0)
    d=lift(tuple(eq))
    assert d is not None
    return d


def verify_plan(plan,c,d,cert):
    if not 0<=c<len(plan[3]):
        return False
    try:
        log,pr,qr=cert
        def select(i,inputs,T):
            # Only the tag is read; inputs always come from verified replay.
            return log[i][0]
        want,up,down,tu,pred=compute(plan,c,select)
        if want!=cert:
            return False
        n=len(plan[2])
        if d is None:
            return not holds(tu[-1],0,n)
        return type(d) is int and 0<=d<1<<n and holds(tu[-1],0,n) and all(
            signature(d,plan[4][i][1]) in p for i,p in pred.items())
    except (ValueError,IndexError,TypeError,KeyError):
        return False


def produce(plan,c,select=policy):
    cert,up,down,tu,pred=compute(plan,c,select)
    d=choose(plan,tu,pred)
    assert verify_plan(plan,c,d,cert)
    return d,cert,up,down


def verify(f,n,c,d,cert,tree=None):
    try:
        p=prepare(f,n,tree)
    except (ValueError,TypeError):
        return False
    return p is not None and verify_plan(p,c,d,cert)


def operation_audit():
    spaces=((1,),(2,),(3,),(4,),(5,6),(1,2),(2,4),(1,4))
    cases=joins=checks=empty=0
    for A in spaces:
        for B in spaces:
            for T in spaces:
                for q in range(8):
                    P,Q=tuple(tuple(z for z in range(1<<len(W))
                                    if (q+j*3+z*5)%7<4)
                              for j,W in enumerate((A,B)))
                    X=convert(table(A,P),TAGS[q%3],3)
                    Y=convert(table(B,Q),TAGS[(q+1)%3],3)
                    expected={signature(t,T) for t in range(8) if
                              signature(t,A) in P and signature(t,B) in Q}
                    for tag in TAGS:
                        M=operation((X,Y),T,3,tag)
                        for t in range(8):
                            assert holds(M,t,3)==(signature(t,T) in expected)
                            checks+=1
                        joins+=1
                    cases+=1
                    empty+=not expected
    assert (cases,joins,checks,empty)==(4096,12288,98304,832)
    print('F038_MIXED_PROJECTION_OK cases=4096 backend_results=12288 '
          'membership_checks=98304 empty=832')


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
            d,cert,up,down=produce(p,c)
            log,pr,qr=cert
            def good(j,t):
                return clause(db[j],forms,t)==(j!=c)
            bad=tuple(t for t in ts if all(good(j,t) for j in range(len(db))))
            empty+=not bad
            for i,(subset,W,S,ch) in enumerate(nodes):
                inside={signature(t,S) for t in ts if all(
                    not subset&(1<<j) or good(j,t) for j in range(len(db)))}
                outside={signature(t,S) for t in ts if all(
                    subset&(1<<j) or good(j,t) for j in range(len(db)))}
                assert all(holds(up[i],t,3)==(signature(t,S) in inside) for t in ts)
                assert all(holds(down[i],t,3)==(signature(t,S) in outside) for t in ts)
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


def high_rank_audit():
    corrupt=0
    for m in (1,2,4,8,16,32):
        half,n=chain(m)
        f=half+half+((-1,n+1),)
        left=balanced([(1<<(2*i),1<<(2*i+1)) for i in range(m)])
        right=balanced([(1<<(2*m+2*i),1<<(2*m+2*i+1)) for i in range(m)])
        tree=((left,right),1<<(4*m))
        p=prepare(f,n+1,tree)
        assert p is not None and p[5]==n and not p[0]
        d,cert,up,down=produce(p,4*m)
        assert d is not None and verify(f,n+1,4*m,d,cert,tree)
        assert {M[0] for M in cert[0]}==set(TAGS)
        for mask in ((1<<(2*m))-1,((1<<(2*m))-1)<<(2*m)):
            i=next(i for i,node in enumerate(p[4]) if node[0]==mask)
            if n>4:
                assert up[i][0]=='obdd'
        t=sum(1<<(2*i) for i in range(m+1))
        assert satisfies(f[:-1],t) and not satisfies((f[-1],),t)
        assert satisfies(f,t^d)
        log,pr,qr=cert
        assert not verify(f,n+1,4*m,d,(log[:-1],pr,qr),tree)
        changed=list(pr)
        changed[0]=tuple(sorted(set(changed[0])^{0}))
        assert not verify(f,n+1,4*m,d,(log,tuple(changed),qr),tree)
        corrupt+=2
    assert corrupt==12
    X=table((1,2),(1,2,3))
    Y=convert(table((2,4),(0,1,3)),'obdd',3)
    assert bounded_join((X,Y),(1,4),3,1)[0]=='unknown'
    status,tag,M,log=bounded_join((X,Y),(1,4),3,1<<20)
    assert status=='positive' and M==operation((X,Y),(1,4),3,tag)
    assert all(row[-1]<=row[1] for row in log)
    print('F038_MIXED_HIGH_RANK_OK sizes=1,2,4,8,16,32 max_rank=65 '
          'representations=3 corrupt_rejected=12 bounded_success=1 bounded_unknown=1')


def audit():
    operation_audit()
    a=audit_fixture(ROWS)
    assert a==(2384,4736,26320,26320,15528,11136,8587,4294,3424)
    print('F038_MIXED_REPAIR_OK formulas=4096 inconsistent=2384 candidates=4736 '
          'up_checks=26320 down_checks=26320 projections=15528 direction_checks=11136 '
          'valid_directions=8587 repair_exists=4294 bad_empty=3424')
    fixture=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3))
                  for w in range(8))
    a=audit_fixture(fixture)
    assert a==(1,896,6336,6336,3616,6944,3328,896,0)
    print('F038_MIXED_REPAIR_FULL_OK formulas=256 inconsistent=1 candidates=896 '
          'up_checks=6336 down_checks=6336 projections=3616 direction_checks=6944 '
          'valid_directions=3328 repair_exists=896 bad_empty=0')
    high_rank_audit()


if __name__=='__main__':
    audit()
