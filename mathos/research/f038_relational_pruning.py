"""Bounded-order carried predicates with affine context propagation."""
from itertools import combinations
from mathos.research.f038_rule_certification import ROWS
from mathos.research.f038_affine_separator import span, intersection, orthogonal, signature, equations, lift
from mathos.research.f038_separator_discovery import balanced
from mathos.research.f038_separator_repair import prepare, modified
from mathos.research.f038_symbolic_affine import normalize, project, contains
from mathos.research import f038_hull_pruning as H


def refine(E,tables):
    passes=0
    if E is None:
        return None,passes
    while True:
        rank=len(E)
        passes+=1
        for W,P in tables:
            allowed=tuple(z for z in P if lift(
                H.equation_rows(E)+equations(W,z)) is not None)
            hull=H.affine_hull(W,allowed)
            if hull is None:
                return None,passes
            E=normalize(E+hull)
            if E is None:
                return None,passes
        if len(E)==rank:
            return E,passes


def exact_summary(nodes,pred,i,k):
    mask,W,S,ch=nodes[i]
    local=tuple((nodes[j][1],p) for j,p in pred.items() if nodes[j][0]&mask)
    rows=set()
    for z in range(1<<len(W)):
        t=lift(equations(W,z))
        assert t is not None
        if all(signature(t,B) in P for B,P in local):
            rows.add(signature(t,S))
    E=H.affine_hull(S,rows)
    if E is None:
        return None,()
    tables=[]
    for d in range(1,min(k,len(S))+1):
        for ids in combinations(range(len(S)),d):
            B=tuple(S[j] for j in ids)
            P=tuple(sorted({sum(((z>>j)&1)<<i for i,j in enumerate(ids)) for z in rows}))
            if len(P)<1<<d:
                tables.append((B,P))
    return E,tuple(sorted(tables))


def carry(tables,S,n):
    out=set()
    for W,P in tables:
        B=span(intersection(W,S,n))
        rows=tuple(sorted({signature(lift(equations(W,z)),B) for z in P}))
        if len(rows)<1<<len(B):
            out.add((B,rows))
    return tuple(sorted(out))


def summaries(nodes,pred,n,h,k):
    out=[]
    for i,(mask,W,S,ch) in enumerate(nodes):
        if not ch or len(W)<=h:
            out.append(exact_summary(nodes,pred,i,k))
            continue
        a,b=ch
        E,P=out[a]
        F,Q=out[b]
        if E is None or F is None:
            out.append((None,()))
            continue
        tables=tuple(sorted(set(P+Q)))
        R,_=refine(normalize(E+F),tables)
        out.append((None,()) if R is None else (project(R,S,n),carry(tables,S,n)))
    return tuple(out)


def fiber(nodes,pred,M,n,i,z):
    _,W,S,ch=nodes[i]
    if not ch:
        return H.fiber(nodes,pred,(),n,i,z)
    a,b=ch
    E,P=M[a]
    F,Q=M[b]
    if E is None or F is None:
        return 0,iter(())
    R,_=refine(normalize(E+F+tuple((v,(z>>j)&1) for j,v in enumerate(S))),
               tuple(sorted(set(P+Q))))
    if R is None:
        return 0,iter(())
    A,B=nodes[a][2],nodes[b][2]
    K=span(A+B)
    t0=lift(H.equation_rows(R))
    assert t0 is not None
    origin=signature(t0,K)
    shifts=span(signature(v,K) for v in orthogonal(tuple(a for a,b in R),n))
    assert len(shifts)==len(K)-len(R)
    size=1<<len(shifts)
    def generate():
        for u in range(size):
            y=origin^H.linear_combination(shifts,u)
            t=lift(equations(K,y))
            assert t is not None
            yield signature(t,A),signature(t,B)
    return size,generate()


def solve(nodes,pred,n,h,k):
    return H.solve(nodes,pred,n,h,lambda a,b,c,d:summaries(a,b,c,d,k),fiber)


def verify(nodes,pred,n,h,k,t,cert):
    return H.verify(nodes,pred,n,h,t,cert,lambda a,b,c,d:summaries(a,b,c,d,k),fiber)


def held(M,t):
    E,P=M
    return E is not None and contains(E,t) and all(signature(t,W) in R for W,R in P)


def propagation_audit():
    spaces=((1,),(2,),(3,),(4,),(5,6),(1,2),(2,4),(1,4))
    cases=checks=empty=true_empty=false_positive=strict=exact=passes=initial=remaining=0
    for A in spaces:
        for B in spaces:
            for T in spaces:
                for q in range(8):
                    P,Q=tuple(tuple(z for z in range(1<<len(W))
                                    if (q+j*3+z*5)%7<4)
                              for j,W in enumerate((A,B)))
                    E=normalize((v,(q>>j)&1) for j,v in enumerate(T))
                    start={t for t in range(8) if contains(E,t)}
                    actual={t for t in start if signature(t,A) in P and signature(t,B) in Q}
                    F,sweeps=refine(E,((A,P),(B,Q)))
                    got={t for t in range(8) if F is not None and contains(F,t)}
                    assert actual<=got<=start
                    cases+=1
                    checks+=8
                    empty+=not got
                    true_empty+=not actual
                    false_positive+=not actual and bool(got)
                    strict+=len(got)<len(start)
                    exact+=got==actual
                    passes+=sweeps
                    initial+=len(start)
                    remaining+=len(got)
    assert (cases,checks,empty,true_empty,false_positive,strict,exact,passes,initial,remaining)==(
        4096,32768,1710,1710,0,3647,4026,6100,12288,3808)
    print('F038_RELATIONAL_PROPAGATION_OK cases=4096 membership_checks=32768 '
          'empty=1710 true_empty=1710 false_positive=0 strict=3647 exact=4026 '
          'sweeps=6100 initial=12288 remaining=3808')


def fixture_audit(fixture):
    inc=queries=nodes_count=checks=yes=no=0
    stronger=0
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
            want=any(all(signature(t,nodes[i][1]) in R for i,R in pred.items()) for t in ts)
            t,cert=solve(nodes,pred,3,2,2)
            M,trace=cert
            old=H.summaries(nodes,pred,3,2)
            assert (t is not None)==want
            assert verify(nodes,pred,3,2,2,t,cert)
            queries+=1
            yes+=want
            no+=not want
            for i,(subset,W,S,ch) in enumerate(nodes):
                actual={signature(u,S) for u in ts if all(
                    not nodes[j][0]&subset or signature(u,nodes[j][1]) in R
                    for j,R in pred.items())}
                got={z for z in range(1<<len(S)) if held(M[i],lift(equations(S,z)))}
                prev={z for z in range(1<<len(S)) if old[i] is not None and
                      contains(old[i],lift(equations(S,z)))}
                assert actual<=got<=prev
                checks+=1<<len(S)
                nodes_count+=1
            root=len(nodes)-1
            new=fiber(nodes,pred,M,3,root,0)[0]
            prior=H.fiber(nodes,pred,old,3,root,0)[0]
            assert new<=prior
            stronger+=new<prior
    print('F038_RELATIONAL_STRICT_ROOTS count='+str(stronger))
    return inc,queries,yes,no,nodes_count,checks


def split_clause(c,top):
    out=[]
    while len(c)>3:
        top+=1
        out.append((c[0],c[1],top))
        c=(-top,)+c[2:]
    out.append(c)
    return tuple(out),top


def family(r,m):
    left=[]
    right=[]
    lt=[]
    rt=[]
    top=r*m
    for j in range(m):
        xs=tuple(range(r*j+1,r*j+r+1))
        start=len(left)
        for c in (xs,tuple(-x for x in xs)):
            f,top=split_clause(c,top)
            left.extend(f)
        lt.append(balanced([1<<i for i in range(start,len(left))]))
    for j in range(m):
        xs=tuple(range(r*j+1,r*j+r+1))
        eqs=[]
        for x,y in zip(xs,xs[1:]):
            u,v=top+1,top+2
            top+=2
            start=len(left)+len(right)
            right.extend(((-x,y,u),(-x,y,-u),(x,-y,v),(x,-y,-v)))
            eqs.append(((1<<start,1<<(start+1)),(1<<(start+2),1<<(start+3))))
        rt.append(balanced(eqs))
    return tuple(left+right),top,(balanced(lt),balanced(rt))


def hierarchy_audit():
    cases=low_trials=high_trials=corrupt=0
    for r in (3,4,5):
        for m in (2,3):
            f,n,tree=family(r,m)
            p=prepare(f,n,tree)
            assert p is not None and not p[0]
            nodes,pred=p[4],p[-1]
            root=len(nodes)-1
            a,b=nodes[root][3]
            assert len(nodes[a][2])==len(nodes[b][2])==r*m
            h=3*r-2
            t,cert=solve(nodes,pred,n,h,r-1)
            assert t is None and cert[0][a]==((),())
            assert len(cert[0][b][0])==(r-1)*m
            assert cert[1][-1]==(root,0,False,1<<m)
            assert verify(nodes,pred,n,h,r-1,t,cert)
            low_trials+=cert[1][-1][-1]
            t,cert=solve(nodes,pred,n,h,r)
            assert t is None and cert[1][-1]==(root,0,False,0)
            assert verify(nodes,pred,n,h,r,t,cert)
            high_trials+=cert[1][-1][-1]
            damaged=list(cert[0])
            damaged[a]=((),())
            assert not verify(nodes,pred,n,h,r,None,(tuple(damaged),cert[1]))
            corrupt+=1
            cases+=1
    assert (cases,low_trials,high_trials,corrupt)==(6,36,0,6)
    print('F038_RELATIONAL_HIERARCHY_OK ranks=3,4,5 blocks=2,3 cases=6 '
          'lower_order_root_trials=36 higher_order_root_trials=0 corrupt_rejected=6')


def audit():
    propagation_audit()
    a=fixture_audit(ROWS)
    assert a==(2384,6398,2622,3776,34130,66390)
    print('F038_RELATIONAL_PRUNING_OK formulas=4096 inconsistent=2384 queries=6398 '
          'sat=2622 unsat=3776 nodes=34130 membership_checks=66390')
    rows=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3))
               for w in range(8))
    a=fixture_audit(rows)
    assert a==(1,1148,1148,0,7876,54172)
    print('F038_RELATIONAL_PRUNING_FULL_OK formulas=256 inconsistent=1 queries=1148 '
          'sat=1148 unsat=0 nodes=7876 membership_checks=54172')
    hierarchy_audit()


if __name__=='__main__':
    audit()
