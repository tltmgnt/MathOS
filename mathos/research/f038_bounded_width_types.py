"""Exact four-label type recognition using common WNU and (2,3)-minimality."""
import json
from itertools import product,combinations
from mathos.research.f038_bounded_inference import require
from mathos.research import f038_mixed_polymorphisms as M
from mathos.research import f038_orientation_discovery as O
from mathos.research.f038_mrax_cycle import run_mrax

PLAN='docs/research/tga-universal/f038-mrax-bounded-width-types.json'
D=tuple(range(4))
C=(0,3,2,1) # values at weights 1 and 2, packed in low and high bit


def raw_t(p,q,r):
    return C.index(M.op(p,C[q]&1,C[r]&1,C[r]&1) |
                   (M.op(p,C[q]>>1,C[r]>>1,C[r]>>1)<<1))


T=tuple(tuple(tuple(raw_t(p,q,r) for r in D) for q in D) for p in D)


def t(p,q,r):
    return T[p][q][r]


def s(p,q):
    u,v=t(p,q,p),t(p,p,q)
    return t(u,u,v)


def wnu(xs):
    def fold(i):
        a=xs[i]
        for j in range(1,len(xs)):
            a=s(a,xs[(i+j)%len(xs)])
        return a
    return t(fold(0),fold(1),fold(2))


def decide(local,n,pins=()):
    # Retain high-arity input relations. Small scopes are additional constraints.
    require(all(tuple(sorted(set(I)))==I and all(0<=i<n for i in I)
                and all(len(r)==len(I) and all(v in D for v in r) for r in P)
                for I,P in local))
    require(all(0<=i<n and a in D for i,a in pins))
    tables=[(I,set(P)) for I,P in local]
    tables.extend(((i,),{(a,)}) for i,a in pins)
    for k in (1,2,3):
        tables.extend((I,set(product(D,repeat=k))) for I in combinations(range(n),k))
    scopes=[]
    for I,P in tables:
        scopes.append(tuple((tuple(I[j] for j in J),J)
                            for k in (1,2) for J in combinations(range(len(I)),k)))
    log=[]
    while True:
        if any(not P for I,P in tables):
            return False,tuple(log)
        support={}
        for (I,P),subs in zip(tables,scopes):
            for S,J in subs:
                proj={tuple(r[j] for j in J) for r in P}
                if S in support:
                    support[S]&=proj
                else:
                    support[S]=proj
        new=[]
        removed=0
        for (I,P),subs in zip(tables,scopes):
            Q={r for r in P if all(tuple(r[j] for j in J) in support[S] for S,J in subs)}
            removed+=len(P)-len(Q)
            new.append((I,Q))
        log.append(removed)
        if not removed:
            return True,tuple(log)
        tables=new


def recognize_local(local,n):
    yes,trace=decide(local,n)
    log=[trace]
    if not yes:
        return 'NO_TYPING',None,tuple(log)
    pins=[]
    for i in range(n):
        for a in D:
            yes,trace=decide(local,n,tuple(pins)+((i,a),))
            log.append(trace)
            if yes:
                pins.append((i,a))
                break
        else:
            raise ValueError('bounded-width reconstruction contradiction')
    labels=tuple(a for i,a in pins)
    require(all(tuple(labels[i] for i in I) in P for I,P in local))
    return 'TYPED',labels,tuple(log)


def recognize(R,n):
    result=recognize_local(O.local_tables(R,n),n)
    if result[0]=='TYPED':
        require(M.valid_types(R,n,result[1]))
    return result


def verify(R,n,result):
    try:
        return result==recognize(R,n)
    except (ValueError,TypeError,IndexError,KeyError):
        return False


def term_audit():
    require(tuple(tuple(s(p,q) for q in D) for p in D)==(
        (0,0,0,0),(1,1,1,1),(0,1,2,3),(0,1,3,3)))
    identities=rows=checks=0
    for k in range(3,9):
        for x,y in product(D,repeat=2):
            values=[]
            for i in range(k):
                a=[x]*k
                a[i]=y
                values.append(wnu(a))
                identities+=1
            require(len(set(values))==1 and (x!=y or values[0]==x))
    for mask in range(256):
        R=(((0,1,2),tuple(w for w in range(8) if mask>>w&1)),)
        I,P=O.local_tables(R,3)[0]
        S=set(P)
        rows+=len(P)
        for a,b,c in product(P,repeat=3):
            require(tuple(T[x][y][z] for x,y,z in zip(a,b,c)) in S)
            checks+=1
    return [identities,256,rows,checks]


def global_audit():
    R=O.fixture()
    local=O.local_tables(R,4)
    universe=tuple(product(D,repeat=4))
    typed=no=checks=feasible=sat=unsat=0
    for mask in range(256):
        A=tuple(r for i,r in enumerate(R) if mask>>i&1)
        L=tuple(r for i,r in enumerate(local) if mask>>i&1)
        good=tuple(a for a in universe if all(tuple(a[i] for i in I) in P for I,P in L))
        result=recognize_local(L,4)
        require((result[0]=='TYPED')==bool(good))
        if good:
            require(result[1] in good and M.valid_types(A,4,result[1]))
            answer=M.solve(A,4,result[1])
            want=any(M.evaluate(A,w) for w in range(16))
            require((answer[0]=='SAT')==want and M.verify(A,4,result[1],answer))
            sat+=want
            unsat+=not want
        else:
            require(result[0]=='NO_TYPING')
        typed+=bool(good)
        no+=not good
        for i in range(4):
            for a in D:
                got,trace=decide(L,4,((i,a),))
                want=any(v[i]==a for v in good)
                require(got==want)
                checks+=1
                feasible+=want
    return [256,typed,no,checks,feasible,sat,unsat]


def controls():
    R=(((0,1,2),tuple(range(7))),)
    I,P=O.local_tables(R,3)[0]
    require(all(a in P for a in ((2,2,0),(2,0,2),(0,2,2))) and (2,2,2) not in P)
    require(not decide(((I,P),),3,((0,2),(1,2),(2,2)))[0])
    nae=(((0,1,2),tuple(range(1,7))),)
    require(recognize(nae,3)[0]=='NO_TYPING' and M.evaluate(nae,1))
    cycle=(((0,1),(0,3)),((1,2),(0,3)),((0,2),(1,2)))
    L=O.local_tables(cycle,3)+tuple(((i,),((0,),(1,))) for i in range(3))
    require(not decide(L,3)[0])
    n=12
    chain=tuple(((i,i+1),(0,3)) for i in range(n-1))
    result=recognize(chain,n)
    require(result[0]=='TYPED' and M.valid_types(chain,n,result[1]))
    require(verify(chain,n,result) and not verify(chain,n,('TYPED',result[1],())))
    return 6


def audit():
    result={'terms':term_audit(),'global':global_audit(),'controls':controls()}
    print('F038_MRAX_BOUNDED_WIDTH_TYPES_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
