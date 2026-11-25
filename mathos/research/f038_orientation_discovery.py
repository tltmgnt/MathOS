"""Exact orientation 2SAT and componentwise family compatibility discovery."""
import json
from itertools import product,combinations
from mathos.research.f038_bounded_inference import require
from mathos.research import f038_mixed_polymorphisms as M
from mathos.research.f038_semantic_repair import two_solve
from mathos.research.f038_mrax_cycle import run_mrax

PLAN='docs/research/tga-universal/f038-mrax-orientation-discovery.json'


def family(t):
    return 0 if t<2 else t-1


def local_tables(R,n):
    require(M.valid_tables(R,n))
    return tuple((I,tuple(T for T in product(range(4),repeat=len(I)) if M.closed(P,T)))
                 for I,P in R)


def slice_rows(I,P,F):
    H=tuple(j for j,i in enumerate(I) if F[i]==0)
    O=tuple(I[j] for j in H)
    rows=tuple(sorted({sum(t[j]<<k for k,j in enumerate(H)) for t in P
                       if all(family(v)==F[i] for i,v in zip(I,t))}))
    return O,rows


def orientation_clauses(O,P):
    if not P:
        return ((),)
    out=[]
    for k in (1,2):
        for ids in combinations(range(len(O)),k):
            allowed={M.project(p,ids) for p in P}
            for z in range(1<<k):
                if z not in allowed:
                    out.append(tuple(-(O[j]+1) if z>>i&1 else O[j]+1
                                     for i,j in enumerate(ids)))
    return tuple(out)


def fixed(local,n,F):
    require(len(F)==n and all(type(f) is int and 0<=f<3 for f in F))
    clauses=[]
    for I,P in local:
        O,Q=slice_rows(I,P,F)
        clauses.extend(orientation_clauses(O,Q))
    w=two_solve(tuple(clauses),n)
    if w is None:
        return None
    T=tuple((w>>i&1) if f==0 else f+1 for i,f in enumerate(F))
    require(all(tuple(T[i] for i in I) in P for I,P in local),'invalid orientation witness')
    return T


def components(local,n):
    parent=list(range(n))
    def root(i):
        while parent[i]!=i:
            i=parent[i]
        return i
    for I,P in local:
        for i in I[1:]:
            a,b=root(I[0]),root(i)
            if a!=b:
                parent[max(a,b)]=min(a,b)
    D={}
    for i in range(n):
        D.setdefault(root(i),[]).append(i)
    return tuple(tuple(I) for I in D.values())


def discover_local(local,n,cap,domains=None):
    require(type(cap) is int and cap>=0)
    D=[set(range(3)) for _ in range(n)] if domains is None else [set(s) for s in domains]
    require(len(D)==n and all(s<=set(range(3)) for s in D))
    if any(not P for I,P in local) or any(not s for s in D):
        return 'NO_TYPING',None,()
    while True:
        changed=False
        for I,P in local:
            Q=tuple(t for t in P if all(family(v) in D[i] for i,v in zip(I,t)))
            if not Q:
                return 'NO_TYPING',None,()
            for j,i in enumerate(I):
                s=D[i]&{family(t[j]) for t in Q}
                if s!=D[i]:
                    D[i]=s
                    changed=True
        if not changed:
            break
    result=[0]*n
    log=[]
    for C in components(local,n):
        b=sum(len(D[i])>1 for i in C)
        if b>cap:
            return 'UNKNOWN',None,tuple(log)
        S=set(C)
        L=tuple((I,P) for I,P in local if I and I[0] in S)
        count=0
        found=None
        for fs in product(*(sorted(D[i]) for i in C)):
            F=[0]*n
            for i,f in zip(C,fs):
                F[i]=f
            count+=1
            T=fixed(L,n,tuple(F))
            if T is not None:
                found=T
                break
        log.append((C,b,count))
        if found is None:
            return 'NO_TYPING',None,tuple(log)
        for i in C:
            result[i]=found[i]
    T=tuple(result)
    require(all(tuple(T[i] for i in I) in P for I,P in local))
    return 'TYPED',T,tuple(log)


def discover(R,n,cap,domains=None):
    result=discover_local(local_tables(R,n),n,cap,domains)
    if result[0]=='TYPED':
        require(M.valid_types(R,n,result[1]))
    return result


def verify(R,n,cap,domains,result):
    try:
        return result==discover(R,n,cap,domains)
    except (TypeError,ValueError,IndexError,KeyError):
        return False


def slice_audit():
    slices=nonempty=rows=triples=members=ambiguous=0
    for mask in range(256):
        R=(((0,1,2),tuple(w for w in range(8) if mask>>w&1)),)
        I,P=local_tables(R,3)[0]
        for F in product(range(3),repeat=3):
            O,Q=slice_rows(I,P,F)
            slices+=1
            require((fixed(((I,P),),3,F) is not None)==bool(Q))
            if not Q:
                continue
            nonempty+=1
            rows+=len(Q)
            ambiguous+=len(Q)>1
            for a,b,c in product(Q,repeat=3):
                require(((a&b)|(a&c)|(b&c)) in Q)
                triples+=1
            clauses=orientation_clauses(O,Q)
            for z in range(1<<len(O)):
                w=M.embed(z,O)
                require(M.satisfies(clauses,w)==(z in Q))
                members+=1
    return [256,slices,nonempty,rows,triples,members,ambiguous]


def fixture():
    defs=(((0,1),9),((1,2),6),((0,2),9),((2,3),14),
          ((0,1,3),254),((0,2,3),127),((1,2,3),105),((0,1,2),23))
    return tuple((I,tuple(w for w in range(1<<len(I)) if m>>w&1)) for I,m in defs)


def global_audit():
    R=fixture()
    local=local_tables(R,4)
    typed=untyped=global_types=tests=feasible=members=ts=tu=ns=nu=0
    all_types=tuple(product(range(4),repeat=4))
    for mask in range(256):
        A=tuple(r for i,r in enumerate(R) if mask>>i&1)
        L=tuple(r for i,r in enumerate(local) if mask>>i&1)
        actual=tuple(T for T in all_types if all(tuple(T[i] for i in I) in P for I,P in L))
        models=tuple(w for w in range(16) if M.evaluate(A,w))
        result=discover_local(L,4,4)
        require((result[0]=='TYPED')==bool(actual))
        if actual:
            require(result[1] in actual and M.valid_types(A,4,result[1]))
            answer=M.solve(A,4,result[1])
            require((answer[0]=='SAT')==bool(models) and M.verify(A,4,result[1],answer))
            ts+=bool(models)
            tu+=not models
        else:
            require(result[0]=='NO_TYPING')
            ns+=bool(models)
            nu+=not models
        typed+=bool(actual)
        untyped+=not actual
        global_types+=len(actual)
        for F in product(range(3),repeat=4):
            good={T for T in actual if tuple(map(family,T))==F}
            T=fixed(L,4,F)
            require((T is not None)==bool(good))
            if T is not None:
                require(T in good)
            O=tuple(i for i,f in enumerate(F) if f==0)
            clauses=tuple(c for I,P in L for c in orientation_clauses(*slice_rows(I,P,F)))
            for z in range(1<<len(O)):
                w=M.embed(z,O)
                t=tuple(w>>i&1 if f==0 else f+1 for i,f in enumerate(F))
                require(M.satisfies(clauses,w)==(t in good))
                members+=1
            tests+=1
            feasible+=bool(good)
    return [256,typed,untyped,global_types,tests,feasible,members,ts,tu,ns,nu]


def families():
    n=64
    chain=tuple(((i,i+1),(0,3)) for i in range(n-1))
    domains=tuple((0,) for _ in range(n))
    r=discover(chain,n,0,domains)
    require(r[0]=='TYPED' and len(set(r[1]))==1 and r[1][0]<2)
    require(len(r[2])==1 and r[2][0][1:]==(0,1))
    pairs=tuple(((i,i+1),(0,3) if i%4==0 else (1,2)) for i in range(0,n,2))
    s=discover(pairs,n,2)
    require(s[0]=='TYPED' and len(s[2])==32 and all(b==2 and k==1 for C,b,k in s[2]))
    require(M.valid_types(pairs,n,s[1]))
    return [n,len(r[2]),len(s[2]),sum(k for C,b,k in s[2])]


def controls():
    nae=(((0,1,2),tuple(range(1,7))),)
    require(discover(nae,3,3)[0]=='NO_TYPING' and any(M.evaluate(nae,w) for w in range(8)))
    cycle=(((0,1),(0,3)),((1,2),(0,3)),((0,2),(1,2)))
    require(discover(cycle,3,0,((0,),(0,),(0,)))[0]=='NO_TYPING')
    r=discover(cycle,3,0,((1,),(1,),(1,)))
    require(r[0]=='TYPED' and M.solve(cycle,3,r[1])[0]=='UNSAT')
    require(discover(cycle,3,0)[0]=='UNKNOWN')
    require(verify(cycle,3,0,((1,),(1,),(1,)),r) and
            not verify(cycle,3,0,((1,),(1,),(1,)),('TYPED',(0,0,0),r[2])))
    return 5


def audit():
    result={'slices':slice_audit(),'global':global_audit(),'families':families(),'controls':controls()}
    print('F038_MRAX_ORIENTATION_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
