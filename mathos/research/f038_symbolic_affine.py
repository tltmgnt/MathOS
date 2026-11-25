"""Affine-union symbolic messages and exact two-pass repair certificates."""
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_hybrid_affine import reduce, parity
from mathos.research.f038_affine_separator import span, intersection, signature, equations, lift, clause
from mathos.research.f038_separator_discovery import balanced
from mathos.research.f038_separator_repair import (
    prepare, modified, translation_predicate, model)


def normalize(eqs):
    b,bad=reduce(tuple((a,c,()) for a,c in eqs))
    if b is None:
        return None
    return tuple((a,c) for _,(a,c,p) in sorted(b.items()))


def project(flat,S,n):
    t=lift(tuple((a,b,()) for a,b in flat))
    assert t is not None
    K=tuple(a for a,b in flat)
    return normalize((a,parity(a&t)) for a in intersection(K,S,n))


def contains(flat,t):
    return all(parity(a&t)==b for a,b in flat)


def parallel_merge(a,b):
    if tuple(x for x,y in a)!=tuple(x for x,y in b) or a==b:
        return None
    j=next(i for i,(x,y) in enumerate(a) if y!=b[i][1])
    p,q=a[j]
    return normalize((x^p,y^q) if y!=b[i][1] else (x,y)
                     for i,(x,y) in enumerate(a) if i!=j)


def compress(pieces):
    work=sorted(set(pieces))
    while True:
        changed=False
        for i,a in enumerate(work):
            for j,b in enumerate(work):
                if i!=j and normalize(a+b)==a:
                    work.pop(i)
                    changed=True
                    break
            if changed:
                break
        if changed:
            continue
        for i,a in enumerate(work):
            for j in range(i+1,len(work)):
                b=work[j]
                c=parallel_merge(a,b)
                if c is not None:
                    work=sorted(set(work[:i]+work[i+1:j]+work[j+1:]+[c]))
                    changed=True
                    break
            if changed:
                break
        if not changed:
            return tuple(work)


def points(W,allowed):
    return compress(normalize((v,(z>>i)&1) for i,v in enumerate(W))
                    for z in sorted(allowed))


def join(A,B,S,n):
    out=[]
    for a in A:
        for b in B:
            c=normalize(a+b)
            if c is not None:
                out.append(project(c,S,n))
    return compress(out)


def leaf_message(W,S,allowed,n):
    return compress(project(p,S,n) for p in points(W,allowed))


def upward(nodes,pred,n):
    out=[]
    for i,(_,W,S,ch) in enumerate(nodes):
        if ch:
            a,b=ch
            out.append(join(out[a],out[b],S,n))
        else:
            out.append(leaf_message(W,S,pred[i],n))
    return tuple(out)


def downward(nodes,up,n):
    down=[None]*len(nodes)
    down[-1]=((),)
    for i in reversed(range(len(nodes))):
        _,W,S,ch=nodes[i]
        if ch:
            a,b=ch
            down[a]=join(down[i],up[b],nodes[a][2],n)
            down[b]=join(down[i],up[a],nodes[b][2],n)
    return tuple(down)


def projection(W,allowed,exterior):
    return tuple(z for z in sorted(allowed) if any(
        normalize(tuple((v,(z>>i)&1) for i,v in enumerate(W))+p) is not None
        for p in exterior))


def choose(nodes,pred,up):
    if not up[-1]:
        return None
    restrictions=[]
    def visit(i,wanted):
        _,W,S,ch=nodes[i]
        if not ch:
            for z in sorted(pred[i]):
                q=tuple((v,(z>>j)&1) for j,v in enumerate(W))
                if normalize(q+wanted) is not None:
                    restrictions.extend(q)
                    return
            raise AssertionError('leaf reconstruction')
        a,b=ch
        for p in up[a]:
            for q in up[b]:
                together=normalize(p+q+wanted)
                if together is None:
                    continue
                t=lift(tuple((v,h,()) for v,h in together))
                assert t is not None
                visit(a,tuple((v,parity(v&t)) for v in nodes[a][2]))
                visit(b,tuple((v,parity(v&t)) for v in nodes[b][2]))
                return
        raise AssertionError('join reconstruction')
    visit(len(nodes)-1,())
    d=lift(tuple((v,h,()) for v,h in restrictions))
    assert d is not None
    return d


def produce(plan,c):
    rows,rest,forms,db,nodes,width,original=plan
    n=len(forms)
    bad=modified(nodes,original,c)
    up=upward(nodes,bad,n)
    down=downward(nodes,up,n)
    pr=tuple(projection(nodes[i][1],bad[i],down[i]) for i in original)
    qr=tuple(tuple(sorted(translation_predicate(nodes[i][1],original[i],p)))
             for i,p in zip(original,pr))
    pred=dict(zip(original,qr))
    tu=upward(nodes,pred,n)
    d=choose(nodes,pred,tu)
    cert=(up,down,pr,qr,tu)
    assert verify_plan(plan,c,d,cert)
    return d,cert


def check_up(nodes,pred,n,up):
    if len(up)!=len(nodes):
        return False
    for i,(_,W,S,ch) in enumerate(nodes):
        if ch:
            a,b=ch
            want=join(up[a],up[b],S,n)
        else:
            want=leaf_message(W,S,pred[i],n)
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
    if not check_up(nodes,bad,n,up) or len(down)!=len(nodes) or down[-1]!=((),):
        return False
    for i in reversed(range(len(nodes))):
        _,W,S,ch=nodes[i]
        if ch:
            a,b=ch
            if down[a]!=join(down[i],up[b],nodes[a][2],n):
                return False
            if down[b]!=join(down[i],up[a],nodes[b][2],n):
                return False
    if len(pr)!=len(original) or len(qr)!=len(original):
        return False
    pred={}
    for j,i in enumerate(original):
        W=nodes[i][1]
        if pr[j]!=projection(W,bad[i],down[i]):
            return False
        want=tuple(sorted(translation_predicate(W,original[i],pr[j])))
        if qr[j]!=want:
            return False
        pred[i]=want
    if not check_up(nodes,pred,n,tu):
        return False
    if d is None:
        return not tu[-1]
    return bool(tu[-1]) and type(d) is int and 0<=d<1<<n and all(
        signature(d,nodes[i][1]) in pred[i] for i in original)


def verify(f,n,c,d,cert,tree=None,budget=None):
    try:
        p=prepare(f,n,tree,budget)
    except (ValueError,TypeError):
        return False
    return p is not None and verify_plan(p,c,d,cert)


def represented(pieces,t):
    return any(contains(p,t) for p in pieces)


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
                assert all(represented(up[i],t)==(signature(t,S) in inside) for t in ts)
                assert all(represented(down[i],t)==(signature(t,S) in outside) for t in ts)
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


def high_rank(m):
    half=tuple(c for i in range(m) for c in ((2*i+1,2*i+2),(2*i+1,-2*i-2)))
    f=half+half+((-1,2*m+1),)
    left=balanced([(1<<(2*i),1<<(2*i+1)) for i in range(m)])
    right=balanced([(1<<(2*m+2*i),1<<(2*m+2*i+1)) for i in range(m)])
    tree=((left,right),1<<(4*m))
    return f,2*m+1,tree


def high_rank_audit():
    corrupt=0
    for m in (1,2,4,8,16,32):
        f,n,tree=high_rank(m)
        p=prepare(f,n,tree)
        rows,rest,forms,db,nodes,width,original=p
        assert not rows and len(rest)==4*m+1
        assert width==2*m
        ordinary=upward(nodes,original,n)
        for mask in ((1<<(2*m))-1,((1<<(2*m))-1)<<(2*m)):
            i=next(i for i,node in enumerate(nodes) if node[0]==mask)
            assert len(nodes[i][2])==2*m
            assert len(ordinary[i])==1 and len(ordinary[i][0])==m
        d,cert=produce(p,4*m)
        assert d is not None and d&(1<<(2*m))
        assert verify(f,n,4*m,d,cert,tree)
        # Both an omitted and an extra leaf projection are detectable.
        data=list(cert)
        pr=list(data[2])
        pr[0]=tuple(sorted(set(pr[0])^{0}))
        data[2]=tuple(pr)
        assert not verify(f,n,4*m,d,tuple(data),tree)
        corrupt+=1
        data=list(cert)
        tu=list(data[4])
        tu[-1]=()
        data[4]=tuple(tu)
        assert not verify(f,n,4*m,d,tuple(data),tree)
        corrupt+=1
    print('F038_SYMBOLIC_HIGH_RANK_OK sizes=1,2,4,8,16,32 max_rank=64 '
          'half_flats_each=1 max_half_equations=32 corrupt_rejected='+str(corrupt))


def all_spaces(n):
    seen={frozenset((0,))}
    frontier=list(seen)
    while frontier:
        nxt=[]
        for s in frontier:
            for x in range(1,1<<n):
                if x in s:
                    continue
                t=s|frozenset(v^x for v in s)
                if t not in seen:
                    seen.add(t)
                    nxt.append(t)
        frontier=nxt
    return seen


def barrier_audit():
    results=[]
    for m in (1,2):
        n=3*m
        spaces=all_spaces(n)
        flats=inside=maximum=0
        for s in spaces:
            used=set()
            for x in range(1<<n):
                if x in used:
                    continue
                t={v^x for v in s}
                used.update(t)
                flats+=1
                if all(all(((v>>(3*i))&7) not in (0,7) for i in range(m)) for v in t):
                    inside+=1
                    maximum=max(maximum,len(t))
        results.append((len(spaces),flats,inside,maximum))
    assert results==[(16,51,24,4),(2825,26387,1944,16)]
    print('F038_SYMBOLIC_AFFINE_COVER_BARRIER_OK spaces=16,2825 '
          'flats=51,26387 contained=24,1944 max_sizes=4,16')


def audit():
    a=audit_fixture(ROWS)
    assert a==(2384,4736,26320,26320,15528,11136,8587,4294,3424)
    print('F038_SYMBOLIC_REPAIR_OK formulas=4096 inconsistent=2384 candidates=4736 '
          'up_checks=26320 down_checks=26320 projections=15528 direction_checks=11136 '
          'valid_directions=8587 repair_exists=4294 bad_empty=3424')
    fixture=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3))
                  for w in range(8))
    a=audit_fixture(fixture)
    assert a==(1,896,6336,6336,3616,6944,3328,896,0)
    print('F038_SYMBOLIC_REPAIR_FULL_OK formulas=256 inconsistent=1 candidates=896 '
          'up_checks=6336 down_checks=6336 projections=3616 direction_checks=6944 '
          'valid_directions=3328 repair_exists=896 bad_empty=0')
    high_rank_audit()
    barrier_audit()


if __name__=='__main__':
    audit()
