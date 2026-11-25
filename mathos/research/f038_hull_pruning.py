"""Sound affine hull summaries and exact reduced-fiber queries."""
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_affine_separator import (
    span, orthogonal, signature, equations, lift, clause)
from mathos.research.f038_separator_discovery import balanced
from mathos.research.f038_separator_repair import prepare, modified, model
from mathos.research.f038_symbolic_affine import normalize, project, contains


def equation_rows(E):
    return tuple((a,b,()) for a,b in E)


def linear_combination(W,z):
    v=0
    for i,a in enumerate(W):
        if z&(1<<i):
            v^=a
    return v


def affine_hull(S,rows):
    rows=tuple(sorted(set(rows)))
    if not rows:
        return None
    base=rows[0]
    D=span(z^base for z in rows)
    return normalize((linear_combination(S,v),(v&base).bit_count()%2)
                     for v in orthogonal(D,len(S)))


def summaries(nodes,pred,n,h):
    out=[]
    for i,(mask,W,S,ch) in enumerate(nodes):
        if not ch or len(W)<=h:
            rows=set()
            local=tuple((nodes[j][1],p) for j,p in pred.items()
                        if nodes[j][0]&mask)
            for z in range(1<<len(W)):
                t=lift(equations(W,z))
                assert t is not None
                if all(signature(t,B) in p for B,p in local):
                    rows.add(signature(t,S))
            H=affine_hull(S,rows)
        else:
            a,b=ch
            if out[a] is None or out[b] is None:
                H=None
            else:
                E=normalize(out[a]+out[b])
                H=None if E is None else project(E,S,n)
        out.append(H)
    return tuple(out)


def fiber(nodes,pred,H,n,i,z):
    _,W,S,ch=nodes[i]
    if not ch:
        rows=tuple(y for y in sorted(pred[i])
                   if signature(lift(equations(W,y)),S)==z)
        return len(rows),iter(rows)
    a,b=ch
    if H[a] is None or H[b] is None:
        return 0,iter(())
    A,B=nodes[a][2],nodes[b][2]
    K=span(A+B)
    E=normalize(H[a]+H[b]+tuple((v,(z>>j)&1) for j,v in enumerate(S)))
    if E is None:
        return 0,iter(())
    t0=lift(equation_rows(E))
    assert t0 is not None
    origin=signature(t0,K)
    shifts=span(signature(v,K) for v in orthogonal(tuple(a for a,b in E),n))
    assert len(shifts)==len(K)-len(E)
    size=1<<len(shifts)
    def generate():
        for u in range(size):
            y=origin^linear_combination(shifts,u)
            t=lift(equations(K,y))
            assert t is not None
            yield signature(t,A),signature(t,B)
    return size,generate()


def solve(nodes,pred,n,h,summary_fn=summaries,fiber_fn=fiber):
    H=summary_fn(nodes,pred,n,h)
    root=len(nodes)-1
    memo={}
    chosen={}
    trace=[]
    def visit(i,z):
        key=i,z
        if key in memo:
            return memo[key]
        ch=nodes[i][3]
        count=0
        ok=False
        size,options=fiber_fn(nodes,pred,H,n,i,z)
        for opt in options:
            count+=1
            if ch:
                a,b=ch
                good=visit(a,opt[0]) and visit(b,opt[1])
            else:
                good=True
            if good:
                ok=True
                chosen[key]=opt
                break
        memo[key]=ok
        trace.append((i,z,ok,count))
        return ok
    ok=visit(root,0)
    t=None
    if ok:
        eq=[]
        def collect(i,z):
            _,W,S,ch=nodes[i]
            opt=chosen[i,z]
            if ch:
                a,b=ch
                collect(a,opt[0])
                collect(b,opt[1])
            else:
                eq.extend(equations(W,opt))
        collect(root,0)
        t=lift(tuple(eq))
        assert t is not None
    cert=H,tuple(trace)
    assert verify(nodes,pred,n,h,t,cert,summary_fn,fiber_fn)
    return t,cert


def verify(nodes,pred,n,h,t,cert,summary_fn=summaries,fiber_fn=fiber):
    try:
        H,trace=cert
        if H!=summary_fn(nodes,pred,n,h):
            return False
        known={}
        root=len(nodes)-1
        for i,z,ok,count in trace:
            if type(i) is not int or not 0<=i<len(nodes) or (i,z) in known:
                return False
            if type(z) is not int or not 0<=z<1<<len(nodes[i][2]):
                return False
            if type(ok) is not bool or type(count) is not int or count<0:
                return False
            size,options=fiber_fn(nodes,pred,H,n,i,z)
            if count>size or (not ok and count!=size):
                return False
            hit=False
            used=0
            for opt in options:
                if used==count:
                    break
                used+=1
                ch=nodes[i][3]
                if ch:
                    a,b=ch
                    good=known[a,opt[0]] and known[b,opt[1]]
                else:
                    good=True
                if good:
                    hit=True
                    break
            if used!=count or hit!=ok:
                return False
            known[i,z]=ok
        if known.get((root,0)) is not (t is not None):
            return False
        if t is None:
            return True
        return type(t) is int and 0<=t<1<<n and all(
            signature(t,nodes[i][1]) in p for i,p in pred.items())
    except (ValueError,TypeError,KeyError,IndexError):
        return False


def audit_fixture(fixture):
    inc=queries=yes=no=nodes_count=small=large=checks=strict=empty=0
    root_empty=false_positive=before=after=0
    for mask in range(1<<len(fixture)):
        f=tuple(c for i,c in enumerate(fixture) if mask&(1<<i))
        p=prepare(f,3)
        if p is None:
            inc+=1
            continue
        rows,rest,forms,db,nodes,width,original=p
        if not db:
            continue
        free=span(a for a,b in forms)
        ts=tuple(lift(equations(free,z)) for z in range(1<<len(free)))
        for c in range(-1,len(db)):
            pred=original if c<0 else modified(nodes,original,c)
            want=any(all(signature(t,nodes[i][1]) in P for i,P in pred.items())
                     for t in ts)
            t,cert=solve(nodes,pred,3,2)
            H,trace=cert
            assert (t is not None)==want and verify(nodes,pred,3,2,t,cert)
            queries+=1
            yes+=want
            no+=not want
            for i,(subset,W,S,ch) in enumerate(nodes):
                exact={signature(u,S) for u in ts if all(
                    not nodes[j][0]&subset or signature(u,nodes[j][1]) in P
                    for j,P in pred.items())}
                hull={z for z in range(1<<len(S)) if H[i] is not None and
                      contains(H[i],lift(equations(S,z)))}
                assert exact<=hull
                checks+=1<<len(S)
                strict+=len(hull)>len(exact)
                empty+=not hull
                nodes_count+=1
                small+=not ch or len(W)<=2
                large+=bool(ch) and len(W)>2
            root=len(nodes)-1
            _,W,S,ch=nodes[root]
            K=span(nodes[ch[0]][2]+nodes[ch[1]][2]) if ch else W
            root_empty+=H[root] is None
            false_positive+=not want and H[root] is not None
            before+=1<<len(K)
            size,_=fiber(nodes,pred,H,3,root,0)
            after+=size
    return (inc,queries,yes,no,nodes_count,small,large,checks,strict,empty,
            root_empty,false_positive,before,after)


def sign_family(m,positive):
    left=tuple(c for i in range(1,m+1) for c in (
        (i if positive else -i,m+i),(i if positive else -i,-m-i)))
    right=tuple((i,2*m+i) for i in range(1,m+1))
    tree=(balanced([(1<<(2*i),1<<(2*i+1)) for i in range(m)]),
          balanced([1<<(2*m+i) for i in range(m)]))
    return left+right,3*m,tree


def obstruction(m):
    left=tuple(c for i in range(m) for c in (
        (3*i+1,3*i+2,3*i+3),(-3*i-1,-3*i-2,-3*i-3)))
    right=[]
    groups=[]
    top=3*m
    for i in range(m):
        pair_trees=[]
        for x,y in ((3*i+1,3*i+2),(3*i+2,3*i+3)):
            u,v=top+1,top+2
            top+=2
            start=len(left)+len(right)
            right.extend(((-x,y,u),(-x,y,-u),(x,-y,v),(x,-y,-v)))
            pair_trees.append(((1<<start,1<<(start+1)),
                              (1<<(start+2),1<<(start+3))))
        groups.append(tuple(pair_trees))
    tree=(balanced([(1<<(2*i),1<<(2*i+1)) for i in range(m)]),
          balanced(groups))
    return left+tuple(right),top,tree


def family_audit():
    sign_cases=corrupt=0
    for m in (1,2,4,8,16,32):
        for positive in (False,True):
            f,n,tree=sign_family(m,positive)
            p=prepare(f,n,tree)
            assert p is not None and not p[0] and p[5]==max(m,2)
            nodes,pred=p[4],p[-1]
            t,cert=solve(nodes,pred,n,4)
            assert t is not None and satisfies(f,model(p[2],t))
            H,trace=cert
            root=len(nodes)-1
            assert fiber(nodes,pred,H,n,root,0)[0]==1
            assert trace[-1]==(root,0,True,1)
            assert sum(row[-1] for row in trace)<=8*m
            bad=list(trace)
            bad[-1]=(root,0,False,1)
            assert not verify(nodes,pred,n,4,None,(H,tuple(bad)))
            corrupt+=1
            sign_cases+=1
    counts=[]
    for m in (1,2,3,4,5,6):
        f,n,tree=obstruction(m)
        p=prepare(f,n,tree)
        assert p is not None and not p[0]
        nodes,pred=p[4],p[-1]
        root=len(nodes)-1
        a,b=nodes[root][3]
        assert len(nodes[a][2])==len(nodes[b][2])==3*m
        t,cert=solve(nodes,pred,n,4)
        H,trace=cert
        assert t is None and H[a]==() and len(H[b])==2*m
        assert H[root]==() and trace[-1]==(root,0,False,1<<m)
        assert fiber(nodes,pred,H,n,root,0)[0]==1<<m
        bad=list(H)
        bad[a]=None
        assert not verify(nodes,pred,n,4,None,(tuple(bad),trace))
        corrupt+=1
        counts.append(trace[-1][-1])
    assert (sign_cases,counts,corrupt)==(12,[2,4,8,16,32,64],18)
    print('F038_HULL_PRUNING_FAMILIES_OK sign_cases=12 max_shared_rank=32 '
          'sign_root_trials_each=1 obstruction_sizes=1,2,3,4,5,6 '
          'obstruction_root_trials=2,4,8,16,32,64 corrupt_rejected=18')


def audit():
    a=audit_fixture(ROWS)
    assert a==(2384,6398,2622,3776,34130,33619,511,66390,2637,10538,
               3748,28,13452,3823)
    print('F038_HULL_PRUNING_OK formulas=4096 inconsistent=2384 queries=6398 '
          'sat=2622 unsat=3776 nodes=34130 exact_hulls=33619 relaxed=511 '
          'membership_checks=66390 strict=2637 empty=10538 root_empty=3748 '
          'root_false_positive=28 fiber_before=13452 fiber_after=3823')
    rows=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3))
               for w in range(8))
    a=audit_fixture(rows)
    assert a==(1,1148,1148,0,7876,4612,3264,54172,4936,0,0,0,8848,2768)
    print('F038_HULL_PRUNING_FULL_OK formulas=256 inconsistent=1 queries=1148 '
          'sat=1148 unsat=0 nodes=7876 exact_hulls=4612 relaxed=3264 '
          'membership_checks=54172 strict=4936 empty=0 root_empty=0 '
          'root_false_positive=0 fiber_before=8848 fiber_after=2768')
    family_audit()


if __name__=='__main__':
    audit()
