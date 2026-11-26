"""Streaming solver for the actual previous quadratic adversary family."""
import json
from itertools import product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import encoded,valid
from mathos.research.f038_unrestricted_quadratic_stage import encoding,dimensions

PLAN='docs/research/tga-universal/f038-unrestricted-quadratic-family-cutoff.json'


def stream(C,n,S):
    require(n%11==0 and n>=33,'invalid family dimension')
    m=n//11
    require(len(S)==n+1+len(C) and S[:n+1]=='1'*n+'0','invalid tape')
    A=[]
    B=[]
    P=[]
    for c,b in zip(C,S[n+1:]):
        require(b in '01','nonbinary selector')
        if len(c)!=3:
            continue
        a,d,e=c
        if a<0 and d<0 and e<0:
            for base,V in ((m,A),(7*m,B)):
                if base< -a<=base+m and base+m< -d<=base+2*m and base+2*m< -e<=base+3*m:
                    V.append(int(b))
        if 10*m<a<=n-2 and d==1-n and e==-n:
            P.append(int(b))
    require(len(A)==len(B)==m**3 and len(P)==m-2,'stream geometry')
    return A,B,P


def reconstruct(m,j,P):
    require(0<=j<m**3 and len(P)==m-2,'invalid index')
    a,b=divmod(j,m*m)
    b,c=divmod(b,m)
    # Build the output in original source variable order. This prototype uses
    # an integer accumulator; the mathematical tape implementation streams bits.
    bits=[]
    for v in range(1,11*m+1):
        bit=0
        for k,i in enumerate((a,b,c)):
            if v in ((k+1)*m+i+1,(k+7)*m+i+1):
                bit=1
            lo=4*m+k*(m-1)+1
            if lo<=v<lo+m-1 and i<=v-lo+1:
                bit=1
        if 10*m<v<=11*m-2:
            bit=P[v-10*m-1]
        bits.append(bit)
    return sum(b<<i for i,b in enumerate(bits))


def solve(C,n,S):
    A,B,P=stream(C,n,S)
    for j,(a,b) in enumerate(zip(A,B)):
        if a==b==0:
            return reconstruct(n//11,j,P),j,A,B,P
    return None,None,A,B,P


def masks(M,mode):
    A=[]
    B=[]
    for j in range(M):
        A.append(int((False,j%2==0,j!=M-1,True,j%3==0,j%5!=1,2*j<M,j==0)[mode]))
        B.append(int((False,j%2==1,False,False,j%5==0,j%5==1,2*j>=M,j==M-1)[mode]))
    return A,B


def rows():
    out=[]
    for m in (3,4,5):
        n,M,L,*_=dimensions(m)
        C=pool(n)
        I={c:i for i,c in enumerate(C)}
        st=[m,n,L,M,0,0,0,0,0,0,0,0]
        for pins in (0,(1<<(m-2))-1,((1<<(m-2))-1)//3):
            F,A,B,W=encoding(m,pins)
            fixed=set(F)
            for mode in range(8):
                a,b=masks(M,mode)
                selected=fixed|{c for c,z in zip(A,a) if z}|{c for c,z in zip(B,b) if z}
                p=sum(1<<I[c] for c in selected)
                S=encoded(n,p,C)
                require(len(S)==L,'actual length')
                w,j,aa,bb,P=solve(C,n,S)
                require(aa==a and bb==b and P==[(pins>>i)&1 for i in range(m-2)],
                        'stream extraction mismatch')
                good=[i for i in range(M) if not(a[i] or b[i])]
                require(j==(good[0] if good else None),'surviving index mismatch')
                require(w==(W[j] if j is not None else None),'parent witness mismatch')
                require(w is None or valid(C,n,p,w),'original verifier rejected')
                st[4]+=1
                st[5]+=w is not None
                st[6]+=w is None
                st[7]+=len(good)
                st[8]+=j+1 if j is not None else 0
                st[9]+=sum(aa)
                st[10]+=sum(bb)
                st[11]+=len(C)
        out.append(st)
    return out


def controls():
    m=3
    n,M,L,*_=dimensions(m)
    C=pool(n)
    I={c:i for i,c in enumerate(C)}
    F,A,B,W=encoding(m,1)
    p=sum(1<<I[c] for c in set(F))
    require(solve(C,n,encoded(n,p,C))[:2]==(W[0],0),'empty masks')
    p2=sum(1<<I[c] for c in set(F+A))
    require(solve(C,n,encoded(n,p2,C))[:2]==(None,None),'full mask')
    for j in range(M):
        require(reconstruct(m,j,[1])==W[j],'all index witnesses')
    try:
        stream(C,n,'0'*L)
    except ValueError:
        pass
    else:
        raise ValueError('invalid header accepted')
    return 4


def audit():
    result={'controls':controls(),'rows':rows()}
    print('F038_UNRESTRICTED_QUADRATIC_FAMILY_CUTOFF_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
