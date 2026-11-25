"""Demand-driven boundary membership with replay certificates and repair synthesis."""
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_affine_separator import span, signature, equations, lift
from mathos.research.f038_separator_discovery import balanced
from mathos.research.f038_separator_repair import prepare, modified, translation_predicate, model


class Limit(Exception):
    pass


def complement(S,K):
    B=tuple(S)
    extra=[]
    for v in K:
        if len(span(B+(v,)))>len(B):
            B+=(v,)
            extra.append(v)
    assert span(B)==span(K)
    return tuple(extra)


def options(nodes,i,z):
    _,W,S,ch=nodes[i]
    if ch:
        a,b=ch
        K=span(nodes[a][2]+nodes[b][2])
    else:
        K=W
    extra=complement(S,K)
    for h in range(1<<len(extra)):
        t=lift(equations(S,z)+equations(extra,h))
        assert t is not None
        if ch:
            yield (signature(t,nodes[a][2]),signature(t,nodes[b][2]))
        else:
            yield signature(t,W)


def query(nodes,pred,i,z,cap=None):
    assert 0<=i<len(nodes) and 0<=z<1<<len(nodes[i][2])
    memo={}
    chosen={}
    trace=[]
    trials=0
    def visit(j,y):
        nonlocal trials
        key=(j,y)
        if key in memo:
            return memo[key]
        ch=nodes[j][3]
        count=0
        answer=False
        for opt in options(nodes,j,y):
            if cap is not None and trials>=cap:
                raise Limit
            trials+=1
            count+=1
            if ch:
                a,b=ch
                u,v=opt
                good=visit(a,u) and visit(b,v)
            else:
                good=opt in pred[j]
            if good:
                answer=True
                chosen[key]=opt
                break
        memo[key]=answer
        trace.append((j,y,answer,count))
        return answer
    try:
        answer=visit(i,z)
    except Limit:
        return None,(),None,trials
    t=None
    if answer:
        eq=[]
        def collect(j,y):
            _,W,S,ch=nodes[j]
            opt=chosen[j,y]
            if ch:
                a,b=ch
                collect(a,opt[0])
                collect(b,opt[1])
            else:
                eq.extend(equations(W,opt))
        collect(i,z)
        t=lift(tuple(eq))
        assert t is not None
    return answer,tuple(trace),t,trials


def check(nodes,pred,i,z,result):
    try:
        answer,trace,t,trials=result
        if type(answer) is not bool or not 0<=i<len(nodes) or not 0<=z<1<<len(nodes[i][2]):
            return False
        known={}
        counted=0
        for j,y,ok,count in trace:
            if type(j) is not int or not 0<=j<len(nodes) or (j,y) in known:
                return False
            if type(ok) is not bool or type(count) is not int or count<1:
                return False
            if type(y) is not int or not 0<=y<1<<len(nodes[j][2]):
                return False
            ch=nodes[j][3]
            used=0
            hit=False
            for opt in options(nodes,j,y):
                if used==count:
                    break
                used+=1
                if ch:
                    a,b=ch
                    u,v=opt
                    good=known[a,u] and known[b,v]
                else:
                    good=opt in pred[j]
                if good:
                    hit=True
                    break
            if used!=count or hit!=ok:
                return False
            if not ok:
                # The number of extensions is exactly the fiber cardinality.
                _,W,S,ch=nodes[j]
                K=span(nodes[ch[0]][2]+nodes[ch[1]][2]) if ch else W
                if count!=1<<(len(K)-len(S)):
                    return False
            known[j,y]=ok
            counted+=count
        if known.get((i,z)) is not answer or counted!=trials:
            return False
        if not answer:
            return t is None
        if type(t) is not int or t<0 or signature(t,nodes[i][2])!=z:
            return False
        mask=nodes[i][0]
        return all(signature(t,nodes[j][1]) in allowed
                   for j,allowed in pred.items() if nodes[j][0]&mask)
    except (KeyError,TypeError,ValueError,IndexError):
        return False


def repair(plan,c):
    nodes,original=plan[4],plan[-1]
    bad=modified(nodes,original,c)
    root=len(nodes)-1
    log=[]
    pr=[]
    qr=[]
    for i in original:
        W=nodes[i][1]
        observed=[]
        for z in range(1<<len(W)):
            p=dict(bad)
            p[i]=bad[i]&{z}
            result=query(nodes,p,root,0)
            log.append(result)
            if result[0]:
                observed.append(z)
        pr.append(tuple(observed))
        qr.append(tuple(sorted(translation_predicate(W,original[i],observed))))
    pred=dict(zip(original,qr))
    result=query(nodes,pred,root,0)
    cert=(tuple(log),tuple(pr),tuple(qr),result)
    d=result[2]
    assert verify_repair(plan,c,d,cert)
    return d,cert


def verify_repair(plan,c,d,cert):
    nodes,original=plan[4],plan[-1]
    if not 0<=c<len(plan[3]):
        return False
    try:
        log,pr,qr,final=cert
        bad=modified(nodes,original,c)
        root=len(nodes)-1
        pos=0
        projected=[]
        compiled=[]
        for i in original:
            W=nodes[i][1]
            observed=[]
            for z in range(1<<len(W)):
                p=dict(bad)
                p[i]=bad[i]&{z}
                result=log[pos]
                pos+=1
                if not check(nodes,p,root,0,result):
                    return False
                if result[0]:
                    observed.append(z)
            projected.append(tuple(observed))
            compiled.append(tuple(sorted(translation_predicate(W,original[i],observed))))
        if pos!=len(log) or tuple(projected)!=pr or tuple(compiled)!=qr:
            return False
        pred=dict(zip(original,qr))
        if not check(nodes,pred,root,0,final):
            return False
        if d!=final[2]:
            return False
        return d is None or (0<=d<1<<len(plan[2]) and all(
            signature(d,nodes[i][1]) in pred[i] for i in original))
    except (ValueError,TypeError,IndexError,KeyError):
        return False


def audit_fixture(fixture):
    inc=candidates=rootqueries=positive=negative=projections=exists=directions=valid=0
    nodequeries=nodepositive=0
    for mask in range(1<<len(fixture)):
        f=tuple(c for j,c in enumerate(fixture) if mask&(1<<j))
        p=prepare(f,3)
        if p is None:
            inc+=1
            continue
        rows,rest,forms,db,nodes,width,original=p
        if not db:
            continue
        free=span(a for a,b in forms)
        ts=tuple(lift(equations(free,z)) for z in range(1<<len(free)))
        for c in range(len(db)):
            candidates+=1
            badpred=modified(nodes,original,c)
            bad=tuple(t for t in ts if all(signature(t,nodes[i][1]) in P
                                            for i,P in badpred.items()))
            for i,(subset,W,S,ch) in enumerate(nodes):
                for z in range(1<<len(S)):
                    result=query(nodes,badpred,i,z)
                    expected=any(signature(t,S)==z and all(
                        signature(t,nodes[j][1]) in P for j,P in badpred.items()
                        if nodes[j][0]&subset) for t in ts)
                    assert result[0]==expected and check(nodes,badpred,i,z,result)
                    nodequeries+=1
                    nodepositive+=expected
            d,cert=repair(p,c)
            log,pr,qr,final=cert
            for j,i in enumerate(original):
                assert set(pr[j])=={signature(t,nodes[i][1]) for t in bad}
                projections+=1<<len(nodes[i][1])
            for r in log+(final,):
                rootqueries+=1
                positive+=r[0]
                negative+=not r[0]
            count=0
            for v in ts:
                expected=all(satisfies(f,model(forms,t^v)) for t in bad)
                assert expected==all(signature(v,nodes[i][1]) in qr[j]
                                     for j,i in enumerate(original))
                count+=expected
                directions+=1
                valid+=expected
            assert (d is not None)==bool(count)
            if d is not None:
                assert all(satisfies(f,model(forms,t^d)) for t in bad)
            exists+=bool(count)
    return inc,candidates,rootqueries,positive,negative,projections,exists,directions,valid,nodequeries,nodepositive


def sign_family(m,positive):
    left=tuple(c for i in range(1,m+1) for c in (
        (i if positive else -i,m+i),(i if positive else -i,-m-i)))
    right=tuple((i,2*m+i) for i in range(1,m+1))
    tree=(balanced([(1<<(2*i),1<<(2*i+1)) for i in range(m)]),
          balanced([1<<(2*m+i) for i in range(m)]))
    return left+right,3*m,tree


def sign_audit():
    early=[]
    late=[]
    corrupt=0
    for m in (1,2,4,8,16,32):
        f,n,tree=sign_family(m,False)
        p=prepare(f,n,tree)
        assert p is not None and not p[0] and p[5]==max(m,2)
        nodes,original=p[4],p[-1]
        root=len(nodes)-1
        result=query(nodes,original,root,0)
        assert result[0] and result[1][-1]==(root,0,True,1)
        assert result[3]<=8*m and check(nodes,original,root,0,result)
        assert satisfies(f,model(p[2],result[2]))
        early.append(result[1][-1][-1])
        trace=list(result[1])
        trace[-1]=(root,0,False,1)
        assert not check(nodes,original,root,0,(False,tuple(trace),None,result[3]))
        corrupt+=1
        assert query(nodes,original,root,0,0)[0] is None
        if m<=8:
            f,n,tree=sign_family(m,True)
            p=prepare(f,n,tree)
            nodes,original=p[4],p[-1]
            root=len(nodes)-1
            result=query(nodes,original,root,0)
            assert result[0] and result[1][-1]==(root,0,True,1<<m)
            assert check(nodes,original,root,0,result) and satisfies(f,model(p[2],result[2]))
            late.append(result[1][-1][-1])
            assert query(nodes,original,root,0,(1<<m)-1)[0] is None
    assert early==[1]*6 and late==[2,4,16,256] and corrupt==6
    print('F038_LAZY_ORDER_OK early_sizes=1,2,4,8,16,32 early_root_trials=1,1,1,1,1,1 '
          'late_sizes=1,2,4,8 late_root_trials=2,4,16,256 corrupt_rejected=6 cap_unknown=10')


def audit():
    a=audit_fixture(ROWS)
    assert a==(2384,4736,38176,8694,29482,33440,4294,11136,8587,51536,27972)
    print('F038_LAZY_REPAIR_OK formulas=4096 inconsistent=2384 candidates=4736 '
          'root_queries=38176 positive=8694 negative=29482 projections=33440 '
          'repair_exists=4294 directions=11136 valid=8587 node_queries=51536 node_positive=27972')
    rows=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3))
               for w in range(8))
    a=audit_fixture(rows)
    assert a==(1,896,29312,4512,24800,28416,896,6944,3328,43840,26864)
    print('F038_LAZY_REPAIR_FULL_OK formulas=256 inconsistent=1 candidates=896 '
          'root_queries=29312 positive=4512 negative=24800 projections=28416 '
          'repair_exists=896 directions=6944 valid=3328 node_queries=43840 node_positive=26864')
    sign_audit()


if __name__=='__main__':
    audit()
