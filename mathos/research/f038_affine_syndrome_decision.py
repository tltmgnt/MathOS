"""Affine-selector feasibility by exact syndrome DP; dual and reduction audits."""
import json
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool

PLAN='docs/research/tga-universal/f038-mrax-affine-syndrome-decision.json'


def true_clause(c,x):
    return any(bool(x>>(abs(l)-1)&1)==(l>0) for l in c)


def syndrome(cols,p):
    v=0
    while p:
        bit=p&-p
        v^=cols[bit.bit_length()-1]
        p^=bit
    return v


def reduce_system(cols,r,b):
    N=len(cols)
    require(type(r) is int and r>=0 and 0<=b<1<<r and
            all(type(c) is int and 0<=c<1<<r for c in cols),'invalid matrix')
    piv={}
    mask=(1<<N)-1
    for i in range(r):
        row=sum(((c>>i)&1)<<j for j,c in enumerate(cols))|(((b>>i)&1)<<N)
        while row&mask:
            j=(row&mask).bit_length()-1
            if j not in piv:
                piv[j]=row
                break
            row^=piv[j]
        else:
            if row>>N&1:
                return None
    rows=tuple(piv.values())
    return tuple(sum(((a>>j)&1)<<i for i,a in enumerate(rows)) for j in range(N)),len(rows),sum(((a>>N)&1)<<i for i,a in enumerate(rows))


def basis(cols,indices):
    piv={}
    for j in indices:
        v=cols[j]
        p=1<<j
        while v:
            i=v.bit_length()-1
            if i not in piv:
                piv[i]=(v,p)
                break
            a,q=piv[i]
            v^=a
            p^=q
    return tuple(piv.values())


def span(cols,indices):
    V={0}
    for a,p in basis(cols,indices):
        V|={v^a for v in V}
    return V


def reach(C,n,cols):
    D={0:None}
    layers=[]
    for i in range(1,n+1):
        E={}
        for bit in (0,1):
            l=i if bit else -i
            B=basis(cols,(j for j,c in enumerate(C) if l in c))
            T={v:(v,0) for v in D}
            for a,p in B:
                for v,(old,mask) in tuple(T.items()):
                    T.setdefault(v^a,(old,mask^p))
            for v,(old,mask) in T.items():
                E.setdefault(v,(old,bit,mask))
        D=E
        layers.append(D)
    return D,layers


def solve(C,n,cols,r,b):
    require(type(n) is int and n>=1 and len(C)==len(cols) and
            all(all(type(l) is int and 1<=abs(l)<=n for l in c) for c in C),
            'invalid clause dimensions')
    red=reduce_system(cols,r,b)
    if red is None:
        return None
    A,k,t=red
    D,L=reach(C,n,A)
    if t not in D:
        return None
    p=x=0
    for i in reversed(range(n)):
        t,bit,mask=L[i][t]
        p^=mask
        x|=bit<<i
    require(t==0 and syndrome(cols,p)==b and
            all(not(p>>j&1) or true_clause(c,x) for j,c in enumerate(C)),
            'reconstruction failed')
    return p,x


def dual(C,cols,r,b):
    return tuple(tuple(sorted({l for c,a in zip(C,cols) if (a&v).bit_count()&1 for l in c}))
                 for v in range(1<<r) if (v&b).bit_count()&1)


def matrices(n,r):
    if n==1:
        for a in range(1<<r):
            for b in range(1<<r):
                yield (a,b)
    else:
        for seed in range(64):
            x=seed+1
            A=[]
            for j in range(8):
                x=(1664525*x+1013904223)&0xffffffff
                A.append((x>>16)&((1<<r)-1))
            yield tuple(A)


def syndromes():
    out=[]
    for n,r in ((1,0),(1,1),(1,2),(1,3),(2,1),(2,2),(2,3),(2,4)):
        C=pool(n)
        N=len(C)
        X=[sum(1<<j for j,c in enumerate(C) if true_clause(c,x)) for x in range(1<<n)]
        st=[n,r,0,0,0,0,0,0,0]
        for A in matrices(n,r):
            st[2]+=1
            allsy=set()
            good=set()
            for p in range(1<<N):
                b=syndrome(A,p)
                allsy.add(b)
                st[4]+=1
                if any(p&x==p for x in X):
                    good.add(b)
                    st[5]+=1
            D,L=reach(C,n,A)
            require(set(D)==good,'syndrome union mismatch')
            spans=[span(A,(j for j in range(N) if x>>j&1)) for x in X]
            for b in range(1<<r):
                w=solve(C,n,A,r,b)
                red=reduce_system(A,r,b)
                require((w is not None)==(b in good) and
                        (red is not None)==(b in allsy),'row reduction or DP mismatch')
                F=dual(C,A,r,b)
                require(len(F)==(1<<(r-1) if b else 0),'dual row count mismatch')
                for x,V in enumerate(spans):
                    require(all(true_clause(c,x) for c in F)==(b in V),'dual clause mismatch')
                st[3]+=1
                st[6]+=b in good
                st[7]+=b not in good
                st[8]+=b not in allsy
        out.append(st)
    return out


def tagged(F,n):
    m=len(F)
    C=pool(n+m)
    index={c:i for i,c in enumerate(C)}
    A=[0]*len(C)
    blocks=[]
    for j,c in enumerate(F):
        require(1<=len(c)<=3 and len(set(map(abs,c)))==len(c),'invalid source clause')
        g=n+j+1
        u=index[(-g,)]
        block=tuple(index[(l,g)] for l in c)
        require(not A[u] and all(not A[i] for i in block),'overlapping equation support')
        A[u]=1<<(2*j)
        for i in block:
            A[i]=1<<(2*j+1)
        blocks.append((u,block))
    return C,tuple(A),2*m,(1<<(2*m))-1,blocks


def reduction():
    U=pool(2)
    st=[0]*8
    for s in range(1<<len(U)):
        F=tuple(c for i,c in enumerate(U) if s>>i&1)
        C,A,r,b,blocks=tagged(F,2)
        require(all(a.bit_count()<=1 for a in A),'overlapping row supports')
        red=reduce_system(A,r,b)
        require(red is not None and red[1]==r,'dependent rows')
        yes=0
        for x in range(4):
            ways=1
            for u,block in blocks:
                require(true_clause(C[u],x),'guard not false')
                count=0
                for p in range(1<<len(block)):
                    if p.bit_count()&1 and all(not(p>>i&1) or true_clause(C[j],x)
                                               for i,j in enumerate(block)):
                        count+=1
                    st[2]+=1
                ways*=count
            ok=all(true_clause(c,x) for c in F)
            require(bool(ways)==ok,'tagged parity equivalence failed')
            yes+=ok
            st[1]+=1
            st[5]+=ways
        if len(F)<=4:
            w=solve(C,2+len(F),A,r,b)
            require((w is not None)==bool(yes),'tagged DP mismatch')
            if w is not None:
                require(all(true_clause(c,w[1]) for c in F),'decoded witness failed')
            st[6]+=1
        st[0]+=1
        st[3]+=bool(yes)
        st[4]+=yes
        st[7]=max(st[7],r)
    return st


def controls():
    # Incompatible signs must not be merged into one span.
    C=((-1,),(1,))
    A=(1,2)
    require(solve(C,1,A,2,3) is None and span(A,range(2))=={0,1,2,3},
            'incompatible signs merged')
    require(solve(C,1,(3,3),2,1) is None and solve(C,1,(3,3),2,3) is not None,
            'dependent equation control failed')
    require(solve(((),(1,-1)),1,(1,2),2,1) is None and
            solve(((),(1,-1)),1,(1,2),2,2) is not None,
            'empty or tautological clause control failed')
    try:
        solve(C,1,(1,4),2,1)
    except ValueError:
        pass
    else:
        raise ValueError('malformed matrix accepted')
    return 4


def audit():
    result={'syndromes':syndromes(),'reduction':reduction(),'controls':controls()}
    print('F038_MRAX_AFFINE_SYNDROME_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
