"""Checked mixed Boolean polymorphisms and bounded-ambiguity type discovery."""
import json
from itertools import product,combinations
from mathos.research.f038_bounded_inference import require,block_project,lift_blocks
from mathos.research.f038_affine_separator import span,orthogonal,lift
from mathos.research.f038_semantic_repair import two_solve
from mathos.research.f038_rule_certification import satisfies
from mathos.research.f038_mrax_cycle import run_mrax

PLAN='docs/research/tga-universal/f038-mrax-mixed-polymorphisms.json'
# Variable coordinates are zero-based. Type: AND=0, OR=1, MAJ=2, XOR=3.


def project(w,ids):
    return sum(((w>>j)&1)<<i for i,j in enumerate(ids))


def embed(w,ids):
    return sum(((w>>i)&1)<<j for i,j in enumerate(ids))


def op(t,a,b,c):
    return (a&b&c,a|b|c,(a&b)|(a&c)|(b&c),a^b^c)[t]


def closed(P,T):
    S=set(P)
    return all(sum(op(t,(a>>i)&1,(b>>i)&1,(c>>i)&1)<<i
                   for i,t in enumerate(T)) in S for a,b,c in product(P,repeat=3))


def valid_tables(R,n):
    return all(tuple(sorted(set(I)))==I and all(0<=i<n for i in I)
               and tuple(sorted(set(P)))==P and all(0<=p<1<<len(I) for p in P)
               for I,P in R)


def valid_types(R,n,T):
    return (len(T)==n and all(type(t) is int and 0<=t<4 for t in T)
            and valid_tables(R,n) and all(closed(P,tuple(T[i] for i in I)) for I,P in R))


def discover(R,n,cap):
    require(valid_tables(R,n) and cap>=0)
    local=tuple((I,tuple(T for T in product(range(4),repeat=len(I)) if closed(P,T)))
                for I,P in R)
    D=[set(range(4)) for _ in range(n)]
    while True:
        changed=False
        for I,allowed in local:
            rows=tuple(t for t in allowed if all(v in D[i] for i,v in zip(I,t)))
            if not rows:
                return 'NO_TYPING',None
            for j,i in enumerate(I):
                s=D[i]&{t[j] for t in rows}
                if s!=D[i]:
                    D[i]=s
                    changed=True
        if not changed:
            break
    if sum(len(s)>1 for s in D)>cap:
        return 'UNKNOWN',None
    for T in product(*(sorted(s) for s in D)):
        if all(tuple(T[i] for i in I) in P for I,P in local):
            require(valid_types(R,n,T))
            return 'TYPED',T
    return 'NO_TYPING',None


def evaluate(R,w):
    return all(project(w,I) in P for I,P in R)


def solve(R,n,T):
    if not valid_types(R,n,T):
        return 'UNSUPPORTED',None,()
    if any(not P for I,P in R):
        return 'UNSAT',None,('empty',)
    flip=sum(1<<i for i,t in enumerate(T) if t==1)
    norm=tuple((I,tuple(sorted(p^project(flip,I) for p in P))) for I,P in R)
    horn=[]
    for I,P in norm:
        J=tuple(j for j,i in enumerate(I) if T[i]<2)
        horn.append((tuple(I[j] for j in J),tuple(sorted({project(p,J) for p in P}))))
    h=0
    trace=[]
    while True:
        old=h
        for I,P in horn:
            z=project(h,I)
            allowed=tuple(p for p in P if p&z==z)
            if not allowed:
                return 'UNSAT',None,('horn',tuple(trace),h,I)
            m=allowed[0]
            for p in allowed[1:]:
                m&=p
            h|=embed(m,I)
        trace.append(h)
        if h==old:
            break
    binary=[]
    rows=[]
    for I,P in norm:
        J=tuple(j for j,i in enumerate(I) if T[i]<2)
        M=tuple(j for j,i in enumerate(I) if T[i]==2)
        A=tuple(j for j,i in enumerate(I) if T[i]==3)
        Q=tuple(p for p in P if project(p,J)==project(h,tuple(I[j] for j in J)))
        require(bool(Q),'least projection not feasible')
        U={project(p,M) for p in Q}
        V={project(p,A) for p in Q}
        require(len(Q)==len(U)*len(V),'factorization failure')
        for k in (1,2):
            for ids in combinations(range(len(M)),k):
                W=tuple(I[M[j]] for j in ids)
                allowed={project(p,ids) for p in U}
                for z in range(1<<k):
                    if z not in allowed:
                        binary.append(tuple(-(i+1) if z>>j&1 else i+1 for j,i in enumerate(W)))
        base=min(V)
        D=span(p^base for p in V)
        for a in orthogonal(D,len(A)):
            rows.append((embed(a,tuple(I[j] for j in A)),(a&base).bit_count()%2,()))
    cert=(tuple(trace),h,tuple(binary),tuple(rows))
    m=two_solve(tuple(binary),n)
    a=lift(tuple(rows))
    if m is None or a is None:
        return 'UNSAT',None,cert
    Mmask=sum(1<<i for i,t in enumerate(T) if t==2)
    Amask=sum(1<<i for i,t in enumerate(T) if t==3)
    w=(h|(m&Mmask)|(a&Amask))^flip
    require(evaluate(R,w),'bad mixed witness')
    return 'SAT',w,cert


def verify(R,n,T,result):
    try:
        if result[0] not in ('SAT','UNSAT') or result!=solve(R,n,T):
            return False
        return result[1] is None if result[0]=='UNSAT' else evaluate(R,result[1])
    except (TypeError,ValueError,IndexError,KeyError):
        return False


def table_audit():
    closed_count=nonempty=least_checks=factor_checks=untypable=0
    for mask in range(256):
        P=tuple(i for i in range(8) if mask>>i&1)
        R=(((0,1,2),P),)
        num=0
        for T in product(range(4),repeat=3):
            if not closed(P,T):
                continue
            num+=1
            closed_count+=1
            result=solve(R,3,T)
            require(result[0]==('SAT' if P else 'UNSAT') and verify(R,3,T,result))
            if not P:
                continue
            nonempty+=1
            H=tuple(i for i,t in enumerate(T) if t<2)
            M=tuple(i for i,t in enumerate(T) if t==2)
            A=tuple(i for i,t in enumerate(T) if t==3)
            flip=sum(1<<i for i,t in enumerate(T) if t==1)
            h=(1<<len(H))-1
            for p in P:
                h&=project(p^flip,H)
            Q=tuple(p for p in P if project(p^flip,H)==h)
            for p in P:
                require(any(project(p,M)==project(q,M) and project(p,A)==project(q,A) for q in Q))
                least_checks+=1
            for a in {project(q,M) for q in Q}:
                for b in {project(q,A) for q in Q}:
                    require(any(project(q,M)==a and project(q,A)==b for q in Q))
                    factor_checks+=1
        state,T=discover(R,3,3)
        require((state=='TYPED')==bool(num))
        if T is not None:
            require(valid_types(R,3,T))
        untypable+=not num
    return [256,16384,closed_count,nonempty,least_checks,factor_checks,untypable]


def mixed():
    T=(0,0,1,2,2,3,3,3)
    defs=(
        ((0,1,2),lambda x:not x&1 or not x&2 or not x&4),
        ((0,),lambda x:bool(x)),((1,),lambda x:bool(x)),((2,),lambda x:bool(x)),
        ((0,3,4),lambda x:not x&1 or bool(x&6)),
        ((1,3,4),lambda x:not x&1 or x&6!=6),
        ((0,5,6,7),lambda x:not x&1 or ((x>>1).bit_count()%2)==0),
        ((1,5,6,7),lambda x:not x&1 or ((x>>1).bit_count()%2)==1),
        ((3,),lambda x:bool(x)),((5,),lambda x:bool(x)))
    R=tuple((I,tuple(z for z in range(1<<len(I)) if fn(z))) for I,fn in defs)
    require(valid_types(R,8,T))
    return R,T


def mixed_audit():
    R,T=mixed()
    yes=no=checks=models=least_cases=least_models=factors=0
    for mask in range(1024):
        F=tuple(t for i,t in enumerate(R) if mask>>i&1)
        ms=tuple(w for w in range(256) if evaluate(F,w))
        result=solve(F,8,T)
        require((result[0]=='SAT')==bool(ms) and verify(F,8,T,result))
        if ms:
            require(result[1] in ms)
        yes+=bool(ms)
        no+=not ms
        checks+=256
        models+=len(ms)
        hp=[]
        for I,P in F:
            J=tuple(j for j,i in enumerate(I) if i<3)
            hp.append((tuple(I[j] for j in J),tuple(sorted({project(p^project(4,I),J) for p in P}))))
        hm=tuple(w for w in range(8) if evaluate(hp,w))
        if not hm:
            require(not ms)
            continue
        h=7
        for w in hm:
            h&=w
        h^=4
        Q=tuple(w for w in ms if w&7==h)
        require(bool(Q)==bool(ms))
        least_cases+=1
        least_models+=len(Q)
        for m in {w&24 for w in Q}:
            for a in {w&224 for w in Q}:
                require(h|m|a in Q)
                factors+=1
    return [1024,yes,no,checks,models,least_cases,least_models,factors]


def encode_tables(R,n):
    out=[]
    for I,P in R:
        for z in range(1<<len(I)):
            if z in P:
                continue
            c=tuple(-(i+1) if z>>j&1 else i+1 for j,i in enumerate(I))
            require(len(c)<=4)
            if len(c)==4:
                n+=1
                out.extend((c[:2]+(n,),(-n,)+c[2:]))
            else:
                out.append(c)
    return tuple(out),n


def merge_blocks(blocks):
    D={}
    for ids,B,table in blocks:
        I=tuple(i-1 for i in B)
        P=set(dict(table))
        if I in D:
            D[I]&=P
        else:
            D[I]=P
    return tuple(sorted((I,tuple(sorted(P))) for I,P in D.items()))


def source_audit():
    R,T=mixed()
    cases=yes=no=0
    for ids in ((0,1,2,4,5,6,8,9),tuple(range(10))):
        F=tuple(R[i] for i in ids)
        f,n=encode_tables(F,8)
        I=tuple(range(1,9))
        blocks=block_project(f,n,I,5)
        require(blocks is not None)
        Q=merge_blocks(blocks)
        require(all(evaluate(Q,w)==evaluate(F,w) for w in range(256)))
        result=solve(Q,8,T)
        require(verify(Q,8,T,result))
        if result[0]=='SAT':
            w=lift_blocks(f,n,I,result[1],blocks,5)
            require(w is not None and satisfies(f,w))
            yes+=1
        else:
            require(result[0]=='UNSAT' and not any(evaluate(F,w) for w in range(256)))
            no+=1
        cases+=1
    return [cases,yes,no]


def controls():
    nae=(((0,1,2),tuple(range(1,7))),)
    require(discover(nae,3,3)==('NO_TYPING',None))
    clauses=(((0,1,2),tuple(range(1,8))),((0,1,2),tuple(range(7))))
    require(discover(clauses,3,3)==('NO_TYPING',None))
    full=(((0,1,2),tuple(range(8))),)
    require(discover(full,3,0)==('UNKNOWN',None))
    require(solve(nae,3,(2,2,2))[0]=='UNSUPPORTED')
    R,T=mixed()
    F=tuple(R[i] for i in (0,1,2,4,5,6,8,9))
    result=solve(F,8,T)
    require(result[0]=='SAT' and not verify(F,8,T,(result[0],result[1],())))
    return 5


def audit():
    result={'tables':table_audit(),'mixed':mixed_audit(),'source':source_audit(),'controls':controls()}
    print('F038_MRAX_MIXED_TYPES_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
