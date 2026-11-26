"""Same-U near-quadratic clock obstruction: crossing transcript and rejection audits."""
import json
from itertools import product,combinations
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import encoded,encode_tm,tape_run,stage,valid

PLAN='docs/research/tga-universal/f038-unrestricted-crossing-adversary.json'


def dimensions(m):
    require(type(m) is int and m>=1,'invalid group size')
    n=32*m
    M=m**3
    N=sum((1<<j)*comb(n,j) for j in (1,2,3))
    L=n+1+N
    P=L-8*comb(24*m,3)
    E=L-8*comb(21*m,3)
    F=L-8*comb(8*m,3)
    R=P-n
    g=F-E+1
    u=(L-1).bit_length()+1
    Q=M*min(g,R)//(256*u*u)
    s=Q.bit_length()-1
    return n,M,N,L,P,E,F,R,g,u,s


def geometry():
    rows=[]
    for m in (1,2,4,8,16,32,64,128,256,512):
        n,M,N,L,P,E,F,R,g,u,s=dimensions(m)
        good=s>=0 and m>s+1 and s-3<n and M>=8
        if good:
            require(s<=2*u and 164*u*u*(1<<s)<M*min(g,R),'record average bound failed')
        rows.append([m,n,M,L,R,g,u,s,int(good)])
    return rows


def onehot(X,Y):
    require(len(X)>=1 and len(Y)==len(X)-1,'bad OR chain')
    C=[(-a,-b) for a,b in combinations(X,2)]
    if not Y:
        C.append((X[0],))
    else:
        for j,y in enumerate(Y):
            a=X[0] if j==0 else Y[j-1]
            b=X[j+1]
            C.extend(((-a,y),(-b,y),(a,b,-y)))
        C.append((Y[-1],))
    return tuple(C)


def true(c,w):
    return any(bool(w>>(abs(l)-1)&1)==(l>0) for l in c)


def onehot_audit():
    rows=[]
    for m in range(1,7):
        C=onehot(tuple(range(1,m+1)),tuple(range(m+1,2*m)))
        st=[m,len(C),0,0,0]
        for x in range(1<<m):
            count=0
            for y in range(1<<(m-1)):
                count+=all(true(c,x|(y<<m)) for c in C)
                st[2]+=1
            require(count==int(x.bit_count()==1),'onehot projection failed')
            st[3]+=count
            st[4]+=bool(count)
        rows.append(st)
    return rows


def norm(c):
    return tuple(sorted(c,key=abs))


def encoding(m,pins):
    n,M,N,L,P,E,F,R,g,u,s=dimensions(m)
    require(0<=pins<1<<m,'bad pins')
    X=tuple(tuple(range(8*m+i*m+1,8*m+(i+1)*m+1)) for i in range(3))
    Z=tuple(tuple(range(24*m+i*m+1,24*m+(i+1)*m+1)) for i in range(3))
    Y=tuple(tuple(range(i*(m-1)+1,(i+1)*(m-1)+1)) for i in range(3))
    C=[]
    for A,B,G in zip(X,Z,Y):
        C.extend(onehot(A,G))
        for a,b in zip(A,B):
            C.extend(((-a,b),(a,-b)))
    pinclauses=[]
    for j in range(m):
        l=27*m+j+1
        if not pins>>j&1:
            l=-l
        pinclauses.extend((l,a,b) for a,b in product((1-n,n-1),(-n,n)))
    C.extend(pinclauses)
    I=tuple(product(range(m),repeat=3))
    left=tuple(tuple(-X[k][j[k]] for k in range(3)) for j in I)
    right=tuple(tuple(-Z[k][j[k]] for k in range(3)) for j in I)
    C=tuple(map(norm,C))
    U=pool(n)
    idx={c:i+n+1 for i,c in enumerate(U)}
    require(len(U)==N and all(c in idx for c in C),'fixed clause outside pool')
    require(all(P<=idx[c]<E for c in left) and all(idx[c]>=F for c in right+tuple(pinclauses)),
            'separated index geometry failed')
    W=[]
    for j in I:
        ones=[27*m+i+1 for i in range(m) if pins>>i&1]
        for k,b in enumerate(j):
            ones.extend((X[k][b],Z[k][b]))
            ones.extend(v for i,v in enumerate(Y[k]) if b<=i+1)
        w=sum(1<<(i-1) for i in ones)
        require(all(true(c,w) for c in C),'fixed witness failed')
        W.append(w)
    for i,w in enumerate(W):
        require(all(true(c,w)==(i!=j) for j,c in enumerate(left)) and
                all(true(c,w)==(i!=j) for j,c in enumerate(right)),
                'index predicate failed')
    return U,C,left,right,W


def sets():
    U,C,A,B,W=encoding(2,1)
    M=len(W)
    st=[M,0,0,0,0]
    # Compute actual forbidden masks from clause truth on reconstructed models.
    badA=[sum(1<<j for j,c in enumerate(A) if not true(c,w)) for w in W]
    badB=[sum(1<<j for j,c in enumerate(B) if not true(c,w)) for w in W]
    for a in range(1<<M):
        for b in range(1<<M):
            good=sum(not(a&x or b&y) for x,y in zip(badA,badB))
            require(good==M-(a|b).bit_count(),'forbidden set equivalence failed')
            st[1]+=1
            st[2]+=bool(good)
            st[3]+=good
            st[4]+=not good
    return st


def trace(T,q,S,t,cut,n):
    tape=dict(enumerate(S))
    head=state=l=r=0
    crossings=[]
    halt=False
    for _ in range(t):
        old=head
        if head<cut:
            l+=1
        else:
            r+=1
        state,w,move=T[3*state+tape.get(head,2)]
        tape[head]=w
        head+=move
        if (old<cut)!=(head<cut):
            crossings.append(state)
        if state==q:
            halt=True
            break
    bits=tuple(tape.get(head+i,2) for i in range(n)) if halt else ()
    return l,r,tuple(crossings),halt,head if halt else 0,bits


def tiny(a,b):
    return (a&1,a>>1,0,0,b&1,b>>1)


def reason(v,a,b):
    if not v[3]:
        return -1
    bits=v[5]
    if 2 in bits:
        return 6+bits.index(2)
    x,y=bits
    if not x and not y:
        return 0
    if x and y:
        return 1
    i=0 if x else 1
    if a>>i&1:
        return 2+i
    if b>>i&1:
        return 4+i
    return -2


def record(v,a,b):
    return v[:5]+(reason(v,a,b),)


def splice():
    rows=[]
    options=tuple(product(range(2),range(3),range(-1,2)))
    for t in (1,4,8):
        st=[t,0,0,0,0,0,0,0]
        for T in product(options,repeat=3):
            st[1]+=1
            for c in (2,3,4):
                V=[trace(T,1,tiny(a,a^3),t,c,2) for a in range(4)]
                K=[record(v,a,a^3) for a,v in enumerate(V)]
                st[2]+=len(V)
                for i,j in combinations(range(4),2):
                    if K[i]!=K[j]:
                        continue
                    st[3]+=1
                    for a,b in ((i,j^3),(j,i^3)):
                        v=trace(T,1,tiny(a,b),t,c,2)
                        st[4]+=record(v,a,b)==K[i]
                        require(reason(v,a,b)!=-2,'accepted crossed output')
                        st[5]+=1
                        st[6]+=(a|b)!=3
                        st[7]+=v[3] and v[4]<c<=v[4]+1
        rows.append(st)
    return rows


def controls():
    U,C,A,B,W=encoding(1,1)
    idx={c:j for j,c in enumerate(U)}
    p=sum(1<<idx[c] for c in set(C))
    require(valid(U,32,p,W[0]) and stage(U,32,p,6)[0] is None,'actual small stage failed')
    T=((1,1,0),)*3
    d=encode_tm(T,1)
    v=trace(T,1,tuple(map(int,encoded(32,p,U))),1,1,32)
    require(v[3] and sum(b<<i for i,b in enumerate(v[5]))==tape_run(U,32,p,d,1),
            'actual interpreter replay failed')
    # Halt crossing and output straddling are separate boundary cases.
    v=trace(((1,0,1),)*3,1,(0,1,0),1,1,2)
    require(v==(1,0,(1,),True,1,(1,0)),'halt crossing lost')
    v=trace(((1,0,0),)*3,1,(0,1),1,1,2)
    require(v[3] and v[4]==0 and v[5]==(0,1),'straddling output lost')
    return 4


def audit():
    result={'geometry':geometry(),'onehot':onehot_audit(),'sets':sets(),'splice':splice(),'controls':controls()}
    print('F038_UNRESTRICTED_CROSSING_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
