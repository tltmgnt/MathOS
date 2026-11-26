"""Direct block-interface bounds on binary DAGs, with indirect storage controls."""
import json
from itertools import product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax

PLAN='docs/research/tga-universal/f038-mrax-direct-dag-restriction.json'


def gate(t,a,b):
    return (t>>(2*a+b))&1


def support(n,G,o,blocks):
    require(type(n) is int and n>=1 and 0<=o<n+len(G),'invalid output')
    V=[0]*n
    used=0
    for i,B in enumerate(blocks):
        require(type(B) is int and 0<B<1<<n and not used&B,'invalid block partition')
        used|=B
        for j in range(n):
            if B>>j&1:
                V[j]=1<<i
    for j,(a,b,t) in enumerate(G):
        require(0<=a<n+j and 0<=b<n+j and 0<=t<16,'invalid gate')
        V.append(V[a]|V[b])
    live={o}
    for j in reversed(range(len(G))):
        if n+j in live:
            live.update(G[j][:2])
    require(V[o]==(1<<len(blocks))-1,'block absent from output cone')
    cuts=[set() for _ in blocks]
    charges=[0]*len(blocks)
    J=0
    for j,(a,b,t) in enumerate(G):
        if n+j not in live:
            continue
        J+=(V[a]^V[b]).bit_count()
        for i in range(len(blocks)):
            if (V[a]^V[b])>>i&1:
                w=b if V[a]>>i&1 else a
                cuts[i].add(w)
                charges[i]+=1
    require(sum(charges)==J and sum(map(len,cuts))<=J,'incidence count mismatch')
    return V,tuple(tuple(sorted(B)) for B in cuts),J


def evaluate(n,G,w):
    V=[w>>j&1 for j in range(n)]
    for a,b,t in G:
        V.append(gate(t,V[a],V[b]))
    return V


def replay(n,G,o,S,i,B,cut,signature,x):
    V=dict(zip(cut,signature))
    V.update((j,x>>j&1) for j in range(n) if B>>j&1)
    # Only gates in the output ancestor cone are needed.
    live={o}
    for j in reversed(range(len(G))):
        if n+j in live:
            live.update(G[j][:2])
    for j,(a,b,t) in enumerate(G):
        if n+j in live and S[n+j]>>i&1:
            require(a in V and b in V,'missing boundary value')
            V[n+j]=gate(t,V[a],V[b])
    return V[o]


def restrictions():
    rows=[]
    for n,E,blocks in ((3,((0,1),(3,2),(3,4)),(1,2,4)),
                       (4,((0,1),(2,3),(4,5)),(3,12))):
        st=[n,0,0,0,0,0,0,0,0,0]
        o=n+len(E)-1
        for ts in product(range(16),repeat=3):
            G=tuple((a,b,t) for (a,b),t in zip(E,ts))
            S,cuts,J=support(n,G,o,blocks)
            st[8]=sum(map(len,cuts))
            st[9]=J
            st[1]+=1
            V=[evaluate(n,G,x) for x in range(1<<n)]
            for i,B in enumerate(blocks):
                R=set()
                sig={}
                for z in range(1<<n):
                    if z&B:
                        continue
                    key=tuple(V[z][v] for v in cuts[i])
                    f=[]
                    for x in range(1<<n):
                        if x&~B:
                            continue
                        y=V[x|z][o]
                        require(replay(n,G,o,S,i,B,cuts[i],key,x)==y,
                                'cut replay mismatch')
                        f.append(y)
                        st[4]+=1
                    f=tuple(f)
                    require(key not in sig or sig[key]==f,'signature collision')
                    sig[key]=f
                    R.add(f)
                    st[3]+=1
                require(len(R)<=len(sig)<=1<<len(cuts[i]),'restriction bound failed')
                st[2]+=1
                st[5]+=len(R)
                st[6]+=len(sig)
                st[7]=max(st[7],len(R))
        rows.append(st)
    return rows


def build_isa(l):
    require(type(l) is int and l>=1,'invalid address length')
    k=1<<l
    n=l+k*l+k
    G=[]
    def add(a,b,t):
        G.append((a,b,t))
        return n+len(G)-1
    def mux(a,b,x):
        return add(add(x,a,2),add(x,b,8),14)
    def choose(A,I):
        for x in I:
            A=[mux(A[j],A[j+1],x) for j in range(0,len(A),2)]
        require(len(A)==1,'bad mux tree')
        return A[0]
    addr=tuple(range(l))
    ptr=tuple(choose([l+j*l+i for j in range(k)],addr) for i in range(l))
    o=choose(list(range(l+k*l,n)),ptr)
    blocks=tuple(((1<<l)-1)<<(l+j*l) for j in range(k))
    return n,tuple(G),o,blocks


def isa():
    rows=[]
    for l in (1,2,3):
        k=1<<l
        n,G,o,blocks=build_isa(l)
        S,cuts,J=support(n,G,o,blocks)
        require(len(G)==3*(l+1)*(k-1),'mux gate count failed')
        checks=0
        sumlog=0
        for a in range(k):
            R=set()
            for T in range(1<<k):
                word=0
                for w in range(k):
                    x=a|(w<<(l+a*l))|(T<<(l+k*l))
                    y=evaluate(n,G,x)[o]
                    require(y==T>>w&1,'ISA output mismatch')
                    word|=y<<w
                    checks+=1
                R.add(word)
            require(len(R)==1<<k and len(cuts[a])>=k,'ISA residual count failed')
            sumlog+=k
        require(sumlog==k*k<=sum(map(len,cuts))<=J,'ISA charge failed')
        rows.append([l,k,n,len(G),sumlog,sum(map(len,cuts)),J,checks])
    return rows


def controls():
    # Repeated references do not create an entering wire for their own block.
    require(support(1,((0,0,8),),1,(1,))[1:]==(((),),0),'repeated wire control failed')
    # Output-irrelevant gates must not inflate the charge.
    require(support(2,((0,1,8),(0,0,8)),3,(1,))[1:]==(((),),0),'dead gate charged')
    try:
        support(2,((0,2,8),),2,(1,2))
    except ValueError:
        pass
    else:
        raise ValueError('forward reference accepted')
    try:
        support(2,((0,1,8),),2,(1,1))
    except ValueError:
        pass
    else:
        raise ValueError('overlapping blocks accepted')
    return 4


def audit():
    result={'restrictions':restrictions(),'isa':isa(),'controls':controls()}
    print('F038_MRAX_DIRECT_DAG_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
