"""Tree syndrome cosets, exact contraction, charged layout discovery."""
import json
from itertools import combinations
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_affine_syndrome_decision import basis,syndrome,true_clause,tagged
from mathos.research.f038_universal_witness_layout import pool

PLAN='docs/research/tga-universal/f038-mrax-syndrome-tree-interfaces.json'


def independent(V):
    V=tuple(V)
    return tuple(v for v,p in basis(V,range(len(V))))


def pivots(V):
    return {v.bit_length()-1:(v,p) for v,p in V}


def express(P,v):
    p=0
    while v:
        j=v.bit_length()-1
        if j not in P:
            return None
        a,q=P[j]
        v^=a
        p^=q
    return p


def coset(A,B,b):
    # A and B individually independent. Track dependencies of combined columns.
    V=A+B
    P={}
    K=[]
    for i,a in enumerate(V):
        v,p=a,1<<i
        while v:
            j=v.bit_length()-1
            if j not in P:
                P[j]=(v,p)
                break
            u,q=P[j]
            v^=u
            p^=q
        if not v:
            K.append(p)
    k=len(K)
    p=express(P,b)
    if p is None:
        return k,set()
    mask=(1<<len(A))-1
    T={syndrome(A,p&mask)}
    for q in K:
        a=syndrome(A,q&mask)
        T|={s^a for s in T}
    require(len(T)==1<<k,'coset dimension mismatch')
    return k,T


def signs(C,n,A,r,b):
    require(type(n) is int and n>=1 and len(C)==len(A) and type(r) is int and r>=0
            and type(b) is int and 0<=b<1<<r and all(type(a) is int and 0<=a<1<<r for a in A)
            and all(all(type(l) is int and 1<=abs(l)<=n for l in c) for c in C),'bad system')
    P=[]
    for i in range(n):
        P.append(tuple(basis(A,(j for j,c in enumerate(C) if l in c))
                       for l in (-i-1,i+1)))
    W=tuple(independent(v for B in pair for v,p in B) for pair in P)
    return P,W


def tree_nodes(tree,n):
    nodes=[]
    def rec(t):
        if type(t) is int:
            require(0<=t<n,'bad leaf')
            I=1<<t
        else:
            require(type(t) is tuple and len(t)==2,'bad tree node')
            P,Q=map(rec,t)
            require(not P&Q,'duplicate leaf')
            I=P|Q
        nodes.append((I,t))
        return I
    require(rec(tree)==(1<<n)-1,'incomplete layout')
    return nodes


def subspace(W,I):
    return independent(v for i,B in enumerate(W) if I>>i&1 for v in B)


def solve_tree(C,n,A,r,b,tree):
    P,W=signs(C,n,A,r,b)
    nodes=tree_nodes(tree,n)
    full=(1<<n)-1
    T={}
    k=total=0
    for I,t in nodes:
        width,K=coset(subspace(W,I),subspace(W,full^I),b)
        k=max(k,width)
        D={}
        if type(t) is int:
            for v in K:
                for bit,B in enumerate(P[t]):
                    p=express(pivots(B),v)
                    if p is not None:
                        D[v]=(bit,p)
                        break
        else:
            # Postorder child masks computed structurally, not guessed.
            def mask(u):
                return 1<<u if type(u) is int else mask(u[0])|mask(u[1])
            L,R=map(mask,t)
            for a in T[L]:
                for c in T[R]:
                    s=a^c
                    if s in K:
                        D.setdefault(s,(L,R,a,c))
        require(len(D)<=1<<width,'interface overflow')
        T[I]=D
        total+=len(D)
    if b not in T[full]:
        return None,k,total
    def back(I,v):
        q=T[I][v]
        if I.bit_count()==1:
            bit,p=q
            return p,bit<<(I.bit_length()-1)
        L,R,a,c=q
        p,x=back(L,a)
        u,y=back(R,c)
        return p^u,x|y
    p,x=back(full,b)
    require(syndrome(A,p)==b and all(not(p>>j&1) or true_clause(c,x)
                                    for j,c in enumerate(C)),'witness replay failed')
    return (p,x),k,total


def cuts(W):
    n=len(W)
    full=(1<<n)-1
    d=[len(subspace(W,I)) for I in range(1<<n)]
    return tuple(d[I]+d[full^I]-d[full] for I in range(1<<n))


def optimal(c):
    n=(len(c)-1).bit_length()
    D=[0]*len(c)
    T=[None]*len(c)
    for I in range(1,len(c)):
        if I.bit_count()==1:
            D[I]=c[I]
            T[I]=I.bit_length()-1
            continue
        best=None
        P=(I-1)&I
        while P:
            Q=I^P
            if P<Q:
                v=max(D[P],D[Q])
                if best is None or v<best[0]:
                    best=(v,P,Q)
            P=(P-1)&I
        v,P,Q=best
        D[I]=max(c[I],v)
        T[I]=(T[P],T[Q])
    require(max(c[I] for I,t in tree_nodes(T[-1],n))==D[-1],'layout replay failed')
    return D[-1],T[-1]


def comb(n):
    T=0
    for i in range(1,n):
        T=(T,i)
    return T


def balanced(lo,hi):
    if hi-lo==1:
        return lo
    mid=(lo+hi)//2
    return balanced(lo,mid),balanced(mid,hi)


def random_audit():
    C=((-1,),(1,),(-2,),(2,),(-3,),(3,),(-1,2),(1,-2,3),(),(2,-2))
    n=3
    tree=(0,(1,2))
    out=[]
    for r in range(5):
        st=[r,0,0,0,0,0,0,0]
        for seed in range(32):
            x=seed+1
            A=[]
            for j in C:
                x=(1664525*x+1013904223)&0xffffffff
                A.append((x>>16)&((1<<r)-1))
            A=tuple(A)
            P,W=signs(C,n,A,r,0)
            allowed=set()
            for p in range(1<<len(C)):
                if any(all(not(p>>j&1) or true_clause(c,x) for j,c in enumerate(C))
                       for x in range(1<<n)):
                    allowed.add(syndrome(A,p))
            width=max(cuts(W)[I] for I,t in tree_nodes(tree,n))
            st[1]+=1
            st[4]+=width
            st[5]=max(st[5],width)
            full=pivots(basis(A,(j for j,c in enumerate(C) if c)))
            for b in range(1<<r):
                ans,k,total=solve_tree(C,n,A,r,b,tree)
                require((ans is not None)==(b in allowed) and k==width,'tree DP mismatch')
                st[2]+=1
                st[3]+=ans is not None
                st[6]+=total
                st[7]+=express(full,b) is None
        out.append(st)
    return out


def tagged_instance(F,n):
    C,A,r,b,_=tagged(F,n)
    # Zero columns can always be set to zero. Work in the compact representation.
    I=[j for j,a in enumerate(A) if a]
    C=tuple(C[j] for j in I)
    A=tuple(A[j] for j in I)
    h=n+len(F)
    _,W=signs(C,h,A,r,b)
    c=cuts(W)
    edges=tuple((1<<(n+j))|sum(1<<(abs(l)-1) for l in clause)
                for j,clause in enumerate(F))
    full=(1<<h)-1
    require(all(v==sum(bool(I&e) and bool((full^I)&e) for e in edges)
                for I,v in enumerate(c)),'tagged cut rank mismatch')
    return C,A,r,b,h,c


def tagged_audit():
    U=pool(2)
    st=[0]*8
    for s in range(1<<len(U)):
        F=tuple(c for j,c in enumerate(U) if s>>j&1)
        C,A,r,b,n,c=tagged_instance(F,2)
        t=comb(n)
        ans,k,_=solve_tree(C,n,A,r,b,t)
        yes=any(all(true_clause(cl,x) for cl in F) for x in range(4))
        require((ans is not None)==yes and k==max(c[I] for I,_ in tree_nodes(t,n)),
                'tagged feasibility mismatch')
        if ans is not None:
            require(all(true_clause(cl,ans[1]) for cl in F),'source witness mismatch')
        st[0]+=1
        st[1]+=yes
        st[2]+=len(c)
        st[3]+=k
        st[4]=max(st[4],k)
        if len(F)<=4:
            d,t=optimal(c)
            w,k,_=solve_tree(C,n,A,r,b,t)
            require(k==d and (w is not None)==yes,'optimal replay mismatch')
            st[5]+=1
            st[6]+=d
            st[7]=max(st[7],d)
    return st


def complete():
    rows=[]
    for n in (2,3,4):
        F=tuple(combinations(range(1,n+1),2))
        C,A,r,b,h,c=tagged_instance(F,n)
        d,t=optimal(c)
        bound=(2*n*n+8)//9
        require(d>=bound,'complete-pair lower bound failed')
        ans,k,_=solve_tree(C,h,A,r,b,t)
        require(ans is not None and k==d,'complete-pair replay failed')
        rows.append([n,len(F),r,len(c),d,bound])
    return rows


def controls():
    for n in (16,64,128):
        C=tuple((i+1,) for i in range(n))
        A=tuple(1<<i for i in range(n))
        b=(1<<n)-1
        ans,k,total=solve_tree(C,n,A,n,b,balanced(0,n))
        require(ans==(b,b) and k==0 and total==2*n-1,'large rank zero-width control')
    # Non-coordinate intersection: <3,5> intersect <6,8> = <6>.
    require(coset((3,5),(6,8),11)==(1,{3,5}),'non-coordinate coset failed')
    require(coset((3,5),(6,8),16)==(1,set()),'inconsistent coset accepted')
    require(solve_tree(((-1,),(1,)),1,(1,2),2,3,0)[0] is None,'merged signs')
    try:
        tree_nodes((0,0),2)
    except ValueError:
        pass
    else:
        raise ValueError('duplicate leaf accepted')
    return 5


def audit():
    result={'random':random_audit(),'tagged':tagged_audit(),'complete':complete(),'controls':controls()}
    print('F038_MRAX_SYNDROME_TREE_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
