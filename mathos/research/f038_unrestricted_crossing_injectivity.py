"""A fixed original-U tape machine that makes full crossing records injective."""
import json
from itertools import product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import (
    encoded,encode_tm,decode_tm,tape_run)
from mathos.research.f038_unrestricted_quadratic_stage import length

PLAN='docs/research/tga-universal/f038-unrestricted-crossing-injectivity.json'
HALT='halt'
CODES=tuple(tuple((v>>i)&1 for i in (2,1,0)) if v<5 else (2,2,2)
            for v in range(6))


def compiler():
    Q={}
    def put(a,s,b,w,m):
        R=Q.setdefault(a,[None]*3)
        z=(b,s if w is None else w,m)
        require(R[s] is None or R[s]==z,'conflicting transition')
        R[s]=z

    def allsym(a,b,w,m):
        for s in range(3):
            put(a,s,b,w,m)

    def walk(a,b,k):
        if not k:
            allsym(a,b,None,0)
        for i in range(abs(k)):
            allsym(a if i==0 else a+'.'+str(i),
                   b if i==abs(k)-1 else a+'.'+str(i+1),
                   None,1 if k>0 else -1)

    def write(a,b,W):
        for i,w in enumerate(W):
            allsym(a if i==0 else a+'.'+str(i),
                   b if i==len(W)-1 else a+'.'+str(i+1),w,1)

    # A raw prefix, a blank separator, and a contiguous binary coded suffix.
    for s in range(2):
        put('scan',s,'scan',None,1)
    put('scan',2,'take',None,-1)
    put('take',2,'align',None,1)
    allsym('align','M:start',None,1)
    for b in range(2):
        k=':'+str(b)
        put('take',b,'skip'+k,2,1)
        allsym('skip'+k,'seek'+k,None,1)
        for s in range(2):
            put('seek'+k,s,'seek'+k,None,1)
        put('seek'+k,2,'shift'+k,None,-1)
        for v in range(2):
            j=k+':'+str(v)
            put('shift'+k,v,'push'+j,2,1)
            walk('push'+j,'deposit'+j,1)
            allsym('deposit'+j,'return'+j,v,-1)
            walk('return'+j,'shift'+k,-2)
        put('shift'+k,2,'fill'+k,CODES[b][0],1)
        write('fill'+k,'rewind'+k,CODES[b][1:])
        walk('rewind'+k,'take',-5)

    # Logical alphabet: bits 0,1; marked bits 2,3; delimiter 4; blank 5.
    E={}
    def e(a,s,b,w,m):
        E.setdefault(a,[None]*6)[s]=(b,s if w is None else w,m)

    def ea(a,b,w,m):
        for s in range(6):
            e(a,s,b,w,m)

    ea('start','markL',None,-1)
    ea('markL','seekR',4,1)
    for s in range(5):
        e('seekR',s,'seekR',None,1)
    e('seekR',5,'back',4,-1)
    for s in range(6):
        e('back',s,'find' if s==4 else 'back',None,1 if s==4 else -1)
    for b in range(2):
        k=str(b)
        e('find',b,'left'+k,b+2,-1)
        e('find',b+2,'find',None,1)
        for s in range(6):
            e('left'+k,s,'appendL'+k if s==4 else 'left'+k,None,-1)
            e('appendL'+k,s,'returnL'+k if s==5 else 'appendL'+k,
              b if s==5 else None,1 if s==5 else -1)
            e('returnL'+k,s,'right'+k if s==4 else 'returnL'+k,None,1)
            e('right'+k,s,'appendR'+k if s==4 else 'right'+k,None,1)
            e('appendR'+k,s,'returnR' if s==5 else 'appendR'+k,
              b if s==5 else None,-1 if s==5 else 1)
    e('find',4,'finish',None,1)
    for s in range(6):
        e('returnR',s,'back' if s==4 else 'returnR',None,-1)
        e('finish',s,HALT if s==5 else 'finish',None,0 if s==5 else 1)

    # Read an aligned 3-cell block, rewind, rewrite, move to the next block.
    for a,R in E.items():
        for s,z in enumerate(R):
            if z is None:
                continue
            b,w,m=z
            W=CODES[s]
            start='M:'+a
            base=start+'!'+str(s)
            for i in range(3):
                put(start+''.join(map(str,W[:i])),W[i],
                    base if i==2 else start+''.join(map(str,W[:i+1])),None,1)
            walk(base,base+'w',-3)
            target=HALT if b==HALT else 'M:'+b
            write(base+'w',target if m==1 else base+'m',CODES[w])
            if m!=1:
                walk(base+'m',target,3*(m-1))
    ids={a:i for i,a in enumerate(Q)}
    q=len(ids)
    ids[HALT]=q
    require(ids['scan']==0,'initial state')
    T=[(q,s,0) if z is None else (ids[z[0]],z[1],z[2])
       for R in Q.values() for s,z in enumerate(R)]
    d=encode_tm(T,q)
    require(len(d)==length(q) and decode_tm(d)==(q,T),'actual original code')
    return q,T,d


def replay(S,q,T):
    L=len(S)
    V=dict(enumerate(S))
    h=a=t=0
    E=[[] for _ in S]
    while a!=q:
        old=h
        a,w,m=T[3*a+V.get(h,2)]
        V[h]=w
        h+=m
        t+=1
        require(t<=1000*(L+1)**2,'clock envelope')
        c=max(old,h)
        if m and 1<=c<=L:
            E[c-1].append(a)
    require(h==1+3*(2*L+1) and V.get(h,2)==2,'malformed terminal output')
    def read(i):
        p=1+3*i
        return tuple(V.get(p+j,2) for j in range(3))
    require(all(read(-2-j)==CODES[b] and read(L+1+j)==CODES[b]
                for j,b in enumerate(S)),'two exterior copies')
    return t,tuple(map(tuple,E))


def rows(q,T):
    R=[]
    for L in range(1,9):
        st=[L,1<<L,0,0,0,0]
        G=[set() for _ in range(L)]
        for x in range(1<<L):
            S=tuple((x>>j)&1 for j in range(L))
            t,E=replay(S,q,T)
            st[2]+=t
            st[3]=max(st[3],t)
            for c,e in enumerate(E):
                st[4]+=1
                st[5]+=e in G[c]
                require(e not in G[c],'crossing record collision')
                G[c].add(e)
        R.append(st)
    return R


def controls(q,T,d):
    require(q==1046 and len(d)==48120,'fixed description geometry')
    for n in (1,2,3):
        C=pool(n)
        for p in (0,1,(1<<len(C))-1):
            S=tuple(map(int,encoded(n,p,C)))
            t,E=replay(S,q,T)
            require(tape_run(C,n,p,d,t) is None,'original output must be malformed')
    # An interior cut may be inside a physical 3-cell code block.
    # The tested cut set includes all positions 1..L, not only aligned ones.
    t,E=replay((1,0,1,1,0),q,T)
    require(len(E)==5 and all(E),'all interior cut records')
    return 3


def audit():
    q,T,d=compiler()
    result={'controls':controls(q,T,d),'ell':len(d),'q':q,'rows':rows(q,T)}
    print('F038_UNRESTRICTED_CROSSING_INJECTIVITY_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
