"""Programmable directional selector parity and compact hidden-hole oracle audit."""
import json
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool

PLAN='docs/research/tga-universal/f038-mrax-programmable-parity.json'


def normalized(c):
    return tuple(sorted(set(c),key=abs))


def encode(C,n):
    U={c:i for i,c in enumerate(pool(n))}
    S={normalized(c) for c in C}
    require(S<=U.keys(),'clause outside normalized pool')
    return sum(1<<U[c] for c in S)


def sat(C,w):
    return all(any(bool(w>>(abs(l)-1)&1)==(l>0) for l in c) for c in C)


def selector_sat(U,p,n):
    require(0<=p<1<<len(U),'invalid selector')
    C=tuple(c for i,c in enumerate(U) if p>>i&1)
    # Deliberately evaluate all assignments for the bounded reference count.
    return any([sat(C,w) for w in range(1<<n)])


def rank(A):
    B={}
    for a in A:
        while a:
            j=a.bit_length()-1
            if j in B:
                a^=B[j]
            else:
                B[j]=a
                break
    return len(B)


def points(p,A):
    V=[p]
    for a in A:
        V.extend(v^a for v in V[:])
    return V


def parity(U,p,A,n):
    require(0<=p<1<<len(U) and all(type(a) is int and 0<=a<1<<len(U) for a in A),
            'invalid direction dimensions')
    if rank(A)<len(A):
        return 0
    return sum(selector_sat(U,q,n) for q in points(p,A))&1


def paired(F,n,J):
    require(len(set(J))==len(J) and all(1<=j<=n for j in J),'invalid projection')
    G=list(F)
    for i,j in enumerate(J,1):
        u=n+i
        G.extend(((-j,u),(j,-u)))
    m=n+len(J)
    U=pool(m)
    p=encode(G,m)
    A=[]
    for i in range(1,len(J)+1):
        u=n+i
        neg=encode(((-u,),),m)
        pos=encode(((u,),),m)
        require(not p&(neg|pos),'copy unit already selected')
        p|=neg
        A.append(neg|pos)
    require(rank(A)==len(J),'paired directions not independent')
    return U,p,tuple(A),m,len(G)


def projection():
    C=pool(2)
    st=[0]*8
    for s in range(1<<len(C)):
        F=tuple(c for i,c in enumerate(C) if s>>i&1)
        W=[x for x in range(4) if sat(F,x)]
        for I in range(4):
            J=tuple(i+1 for i in range(2) if I>>i&1)
            Y={sum(((x>>(j-1))&1)<<i for i,j in enumerate(J)) for x in W}
            U,p,A,m,g=paired(F,2,J)
            V=points(p,A)
            accepted={z for z,q in enumerate(V) if selector_sat(U,q,m)}
            require(accepted==Y and parity(U,p,A,m)==(len(Y)&1),'projected parity mismatch')
            st[1]+=1
            st[2]+=len(Y)
            st[3]+=len(V)
            st[4]+=len(V)*(1<<m)
            st[5]+=len(Y)&1
            st[6]+=bool(Y)
            st[7]+=g
        st[0]+=1
    return st


def hole(h,a):
    require(h>=1 and 0<=a<1<<h,'invalid hole')
    C=[]
    for i in range(h):
        l=-(i+1) if a>>i&1 else i+1
        y=h+i+1
        if not i:
            C.extend(((-l,y),(l,-y)))
        else:
            v=y-1
            C.extend(((-v,y),(-l,y),(v,l,-y)))
    C.append((2*h,))
    return tuple(C)


def holes():
    rows=[]
    for h in range(1,6):
        N=1<<h
        U=pool(2*h)
        st=[h,N,3**h,0,0,0,0,0,0]
        for a in range(N):
            F=hole(h,a)
            require(all(len(c)<=3 for c in F),'wide hole clause')
            p=encode(F,2*h)
            units=encode(tuple((l,) for i in range(1,h+1) for l in (i,-i)),2*h)
            require(not p&units,'hole uses address unit')
            G=tuple(c for i,c in enumerate(U) if p>>i&1)
            count=[0]*N
            for w in range(1<<(2*h)):
                count[w&(N-1)]+=sat(G,w)
                st[7]+=1
            require(count==[int(x!=a) for x in range(N)],'hole extension not unique')
            st[8]+=sum(count)
            for t in range(3**h):
                P=tuple((t//3**i)%3 for i in range(h))
                X=[x for x in range(N) if all(not v or (x>>i&1)==v-1
                                              for i,v in enumerate(P))]
                yes=any(count[x] for x in X)
                require(bool(X) and yes==(X!=[a]),'oracle distinction failed')
                st[3]+=1
                st[4]+=N
                st[5]+=not yes
                st[6]+=yes
        rows.append(st)
    return rows


def controls():
    U=pool(1)
    require(parity(U,0,(1,1),1)==0 and parity(U,0,(0,),1)==0,
            'rank-deficient parity failed')
    require(parity(U,0,(),1)==1 and parity(U,3,(),1)==0,'zero directions not SAT')
    # One projected empty assignment with two possible existential witnesses.
    U,p,A,n,g=paired((),1,())
    require(parity(U,p,A,n)==1,'counted witnesses instead of projections')
    try:
        parity(U,p,(1<<len(U),),n)
    except ValueError:
        pass
    else:
        raise ValueError('invalid direction accepted')
    return 4


def audit():
    result={'projection':projection(),'holes':holes(),'controls':controls()}
    print('F038_MRAX_PROGRAMMABLE_PARITY_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
