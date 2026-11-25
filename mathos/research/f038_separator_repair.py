"""Two-pass separator projections and same-tree semantic translation synthesis."""
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_hybrid_affine import extract, verify_partition, parity
from mathos.research.f038_affine_separator import span, signature, equations, lift, clause, cycle
from mathos.research.f038_branchwidth_adapter import setup


def rows_of(table):
    return tuple(sorted(table))


def leaf_predicates(forms,db,nodes):
    out={}
    for i,(mask,w,s,ch) in enumerate(nodes):
        if ch:
            continue
        assert mask and not mask&(mask-1)
        j=mask.bit_length()-1
        out[i]=frozenset(z for z in range(1<<len(w))
                         if clause(db[j],forms,lift(equations(w,z))))
    return out


def join(A,sa,B,sb,s):
    out=set()
    for a in A:
        for b in B:
            t=lift(equations(sa,a)+equations(sb,b))
            if t is not None:
                out.add(signature(t,s))
    return out


def upward(nodes,pred):
    up=[]
    for i,(mask,w,s,ch) in enumerate(nodes):
        if ch:
            a,b=ch
            table=join(up[a],nodes[a][2],up[b],nodes[b][2],s)
        else:
            table={signature(lift(equations(w,z)),s) for z in pred[i]}
        up.append(table)
    return up


def downward(nodes,up):
    down=[None]*len(nodes)
    down[-1]={0}
    for i in reversed(range(len(nodes))):
        mask,w,s,ch=nodes[i]
        if ch:
            a,b=ch
            down[a]=join(down[i],s,up[b],nodes[b][2],nodes[a][2])
            down[b]=join(down[i],s,up[a],nodes[a][2],nodes[b][2])
    return down


def projection(nodes,i,allowed,down):
    _,w,s,_=nodes[i]
    return {z for z in allowed if signature(lift(equations(w,z)),s) in down}


def translation_predicate(w,original,proj):
    return {d for d in range(1<<len(w)) if all(z^d in original for z in proj)}


def choose_direction(nodes,pred,up):
    if not up[-1]:
        return None
    # Reconstruct from compatible child boundary rows, collecting full leaf
    # functional restrictions; solve once for a common ambient direction.
    eq=[]
    def visit(i,z):
        _,w,s,ch=nodes[i]
        if not ch:
            y=next(y for y in sorted(pred[i]) if
                   signature(lift(equations(w,y)),s)==z)
            eq.extend(equations(w,y))
            return
        a,b=ch
        for u in sorted(up[a]):
            for v in sorted(up[b]):
                t=lift(equations(nodes[a][2],u)+equations(nodes[b][2],v))
                if t is not None and signature(t,s)==z:
                    visit(a,u)
                    visit(b,v)
                    return
        raise AssertionError('missing witness')
    visit(len(nodes)-1,0)
    d=lift(tuple(eq))
    assert d is not None
    return d


def prepare(f,n,tree=None,budget=None):
    rows,rest=extract(f)
    assert verify_partition(f,rows,rest)
    p,bad=setup(f,n,rows,rest,tree,budget)
    if p is None:
        return None
    forms,db,nodes,width=p
    if not db:
        return (rows,rest,forms,db,nodes,width,{})
    return (rows,rest,forms,db,nodes,width,leaf_predicates(forms,db,nodes))


def modified(nodes,original,candidate):
    target=next(i for i in original if nodes[i][0]==1<<candidate)
    bad=dict(original)
    bad[target]=frozenset(range(1<<len(nodes[target][1])))-original[target]
    return bad


def produce(plan,candidate):
    rows,rest,forms,db,nodes,width,original=plan
    assert 0<=candidate<len(db)
    bad=modified(nodes,original,candidate)
    up=upward(nodes,bad)
    down=downward(nodes,up)
    proj={i:projection(nodes,i,bad[i],down[i]) for i in original}
    pred={i:translation_predicate(nodes[i][1],original[i],proj[i])
          for i in original}
    tu=upward(nodes,pred)
    d=choose_direction(nodes,pred,tu)
    cert=(tuple(map(rows_of,up)),tuple(map(rows_of,down)),
          tuple(rows_of(proj[i]) for i in original),
          tuple(rows_of(pred[i]) for i in original),tuple(map(rows_of,tu)))
    assert verify_plan(plan,candidate,d,cert)
    return d,cert


def canonical(table,r):
    return tuple(sorted(set(table)))==table and all(
        type(z) is int and 0<=z<1<<r for z in table)


def check_up(nodes,pred,up):
    if len(up)!=len(nodes):
        return False
    for i,(mask,w,s,ch) in enumerate(nodes):
        if not canonical(up[i],len(s)):
            return False
        if ch:
            a,b=ch
            want=join(up[a],nodes[a][2],up[b],nodes[b][2],s)
        else:
            want={signature(lift(equations(w,z)),s) for z in pred[i]}
        if set(up[i])!=want:
            return False
    return True


def verify_plan(plan,candidate,d,cert):
    rows,rest,forms,db,nodes,width,original=plan
    if not 0<=candidate<len(db):
        return False
    up,down,pr,qr,tu=cert
    bad=modified(nodes,original,candidate)
    if not check_up(nodes,bad,up) or len(down)!=len(nodes) or down[-1]!=(0,):
        return False
    if any(not canonical(v,len(nodes[i][2])) for i,v in enumerate(down)):
        return False
    for i in reversed(range(len(nodes))):
        _,w,s,ch=nodes[i]
        if ch:
            a,b=ch
            if set(down[a])!=join(down[i],s,up[b],nodes[b][2],nodes[a][2]):
                return False
            if set(down[b])!=join(down[i],s,up[a],nodes[a][2],nodes[b][2]):
                return False
    if len(pr)!=len(original) or len(qr)!=len(original):
        return False
    pred={}
    for j,i in enumerate(original):
        w=nodes[i][1]
        if not canonical(pr[j],len(w)) or not canonical(qr[j],len(w)):
            return False
        if set(pr[j])!=projection(nodes,i,bad[i],down[i]):
            return False
        want=translation_predicate(w,original[i],pr[j])
        if set(qr[j])!=want:
            return False
        pred[i]=want
    if not check_up(nodes,pred,tu):
        return False
    if d is None:
        return not tu[-1]
    return bool(tu[-1]) and type(d) is int and 0<=d<1<<len(forms) and all(
        signature(d,nodes[i][1]) in pred[i] for i in original)


def verify(f,n,candidate,d,cert,tree=None,budget=None):
    try:
        p=prepare(f,n,tree,budget)
    except (ValueError,TypeError):
        return False
    return p is not None and verify_plan(p,candidate,d,cert)


def model(forms,t):
    return sum(1<<i for i,(a,b) in enumerate(forms) if parity(a&t)^b)


def audit_fixture(fixture):
    inconsistent=candidates=empty=sem_exists=local_exists=strict=nonvacuous=0
    upchecks=downchecks=projections=directions=valid=repairs=maxwidth=0
    for mask in range(1<<len(fixture)):
        f=tuple(c for j,c in enumerate(fixture) if mask&(1<<j))
        p=prepare(f,3)
        if p is None:
            inconsistent+=1
            continue
        rows,rest,forms,db,nodes,width,original=p
        free=span(a for a,b in forms)
        ts=tuple(lift(equations(free,z)) for z in range(1<<len(free)))
        for c in range(len(db)):
            candidates+=1
            maxwidth=max(maxwidth,width)
            d,cert=produce(p,c)
            assert verify(f,3,c,d,cert)
            up,down,pr,qr,tu=cert
            def good(j,t):
                return clause(db[j],forms,t)==(j!=c)
            bad=tuple(t for t in ts if all(good(j,t) for j in range(len(db))))
            empty+=not bad
            for i,(subset,w,s,ch) in enumerate(nodes):
                inside={signature(t,s) for t in ts if all(
                    not subset&(1<<j) or good(j,t) for j in range(len(db)))}
                outside={signature(t,s) for t in ts if all(
                    subset&(1<<j) or good(j,t) for j in range(len(db)))}
                assert inside==set(up[i]) and outside==set(down[i])
                upchecks+=1
                downchecks+=1
            for j,i in enumerate(original):
                assert set(pr[j])=={signature(t,nodes[i][1]) for t in bad}
                projections+=1
            se=lo=0
            for v in ts:
                want=all(satisfies(f,model(forms,t^v)) for t in bad)
                got=all(signature(v,nodes[i][1]) in qr[j]
                        for j,i in enumerate(original))
                local=all(clause(db[c],forms,t) or (
                    clause(db[c],forms,t^v) and all(j==c or
                    not clause(D,forms,t) or clause(D,forms,t^v)
                    for j,D in enumerate(db))) for t in ts)
                assert got==want and (not local or want)
                directions+=1
                se+=want
                lo+=local
                valid+=want
                if want:
                    repairs+=len(bad)
            assert (d is not None)==bool(se)
            if d is not None:
                assert all(satisfies(f,model(forms,t^d)) for t in bad)
            sem_exists+=bool(se)
            local_exists+=bool(lo)
            strict+=bool(se) and not lo
            nonvacuous+=bool(se) and not lo and bool(bad)
    return (inconsistent,candidates,empty,sem_exists,local_exists,strict,
            nonvacuous,upchecks,downchecks,projections,directions,valid,repairs,maxwidth)


def cycle_audit():
    corrupt=good=bad=0
    for m in (3,4,7,8,15,16,31,32):
        f,n=cycle(m)
        p=prepare(f,n,budget=4)
        assert p is not None and p[5]<=4
        assert len(span(a for a,b in p[2]))==m
        d,cert=produce(p,0)
        assert (d is not None)==(m%2==0)
        assert verify(f,n,0,d,cert,budget=4)
        good+=d is not None
        bad+=d is None
        # Toggle membership of row zero in the first projection or
        # translation predicate: the independent recurrence must reject.
        for component in (2,3):
            data=list(cert)
            table=list(data[component])
            table[0]=tuple(sorted(set(table[0])^{0}))
            data[component]=tuple(table)
            assert not verify(f,n,0,d,tuple(data),budget=4)
            corrupt+=1
    assert (good,bad,corrupt)==(4,4,16)
    print('F038_SEPARATOR_REPAIR_CYCLE_OK cycles=8 valid=4 impossible=4 '
          'max_global_rank=32 boundary_budget=4 corrupt_rejected=16')


def audit():
    a=audit_fixture(ROWS)
    assert a==(2384,4736,3424,4294,4189,105,35,26320,26320,15528,
               11136,8587,1795,3)
    print('F038_SEPARATOR_REPAIR_OK formulas=4096 inconsistent=2384 candidates=4736 '
          'bad_empty=3424 semantic_exists=4294 local_exists=4189 strict=105 '
          'nonvacuous_strict=35 up_checks=26320 down_checks=26320 '
          'projections=15528 direction_checks=11136 valid_directions=8587 '
          'repairs=1795 max_width=3')
    fixture=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3))
                  for w in range(8))
    a=audit_fixture(fixture)
    assert a==(1,896,0,896,896,0,0,6336,6336,3616,6944,3328,3328,3)
    print('F038_SEPARATOR_REPAIR_FULL_OK formulas=256 inconsistent=1 candidates=896 '
          'bad_empty=0 semantic_exists=896 local_exists=896 strict=0 '
          'nonvacuous_strict=0 up_checks=6336 down_checks=6336 '
          'projections=3616 direction_checks=6944 valid_directions=3328 '
          'repairs=3328 max_width=3')
    cycle_audit()


if __name__=='__main__':
    audit()
