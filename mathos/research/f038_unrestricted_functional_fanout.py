"""Finite plan and bounded-buffer join reference, not a compiled U solver."""
import json
from itertools import product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_unrestricted_universal_search import encoded, valid
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import (
    group, digit, cross, fixed, witness, fixture)
from mathos.research.f038_unrestricted_context_fixedpoint import (
    R, H, XOR_H, local_tables)


def pick(c,j,mode,m):
    g=tuple(group(-x,m) for x in c)
    d=tuple(digit(-x,m) for x in c)
    if mode<7:
        return fixture(c,j,mode,m,tuple(i%m for i in range(R)))
    if mode==7:
        return True
    if mode==11:
        return g==(0,1,2) and (d[0]+d[1])%m!=d[2]
    if g not in XOR_H:
        return False
    if mode==10:
        d=tuple((a+i)%m for i,a in zip(g,d))
    x=d[0]^d[1]^d[2]
    return x>1 if mode==9 else x!=0


def plan(tables):
    if any(not any(ok for _,ok in entries) for _,entries in tables):
        return 0,[]
    options=[[] for _ in range(R)]
    for h,entries in tables:
        for i,g in enumerate(h):
            P=h[:i]+h[i+1:]
            pm=sum(1<<p for p in P)
            rows=sorted((z[:i]+z[i+1:],z[i]) for z,ok in entries if ok)
            counts={}
            for key,a in rows:
                counts[key]=counts.get(key,0)+1
            b=max(counts.values())
            require(1<=b and len(rows)==len(set(rows)),'distinct local extensions')
            options[g].append((g,P,pm,b,rows))
    dp=[None]*(1<<R)
    prev=[None]*(1<<R)
    dp[0]=1
    for s in range(1<<R):
        require(dp[s] is not None,'reachable subset')
        for g in range(R):
            if s>>g&1:
                continue
            for opt in options[g]:
                _,P,pm,b,rows=opt
                if pm&s!=pm:
                    continue
                t=s|(1<<g)
                v=dp[s]*b
                if dp[t] is None or v<dp[t]:
                    dp[t]=v
                    prev[t]=opt
    order=[]
    s=(1<<R)-1
    while s:
        opt=prev[s]
        require(opt is not None,'plan predecessor')
        order.append(opt)
        s^=1<<opt[0]
    order.reverse()
    seen=set()
    W=1
    for g,P,pm,b,rows in order:
        require(g not in seen and set(P)<=seen,'parent order')
        seen.add(g)
        W*=b
    require(W==dp[-1],'plan product')
    return W,order


def join_batch(batch,opt):
    """Sequential merge reference on sorted keys, with reusable digit run."""
    g,P,_,b,rows=opt
    def key(z):
        return tuple(z[p] for p in P)
    j=0
    previous=None
    values=[]
    for z in sorted(batch,key=key):
        k=key(z)
        if k!=previous:
            while j<len(rows) and rows[j][0]<k:
                j+=1
            values=[]
            while j<len(rows) and rows[j][0]==k:
                values.append(rows[j][1])
                j+=1
            previous=k
        require(len(values)<=b,'fanout bound')
        for a in values:
            require(z[g]==-1,'fresh group')
            yield z[:g]+(a,)+z[g+1:]


def enumerate_plan(W,order,cap,accept):
    if W==0:
        return [],[0,0,0,0]
    limits=[cap//opt[3] for opt in order]+[cap]
    require(all(v>=1 for v in limits),'buffer size')
    buffers=[[] for _ in limits]
    # final candidates, chunks, short chunks, emitted child records
    counts=[0,0,0,0]
    found=[]
    def push(i,z):
        buffers[i].append(z)
        require(len(buffers[i])<=limits[i],'capacity')
        if len(buffers[i])==limits[i]:
            flush(i)
    def flush(i):
        batch=buffers[i]
        buffers[i]=[]
        if not batch:
            return
        counts[1]+=1
        counts[2]+=len(batch)<limits[i]
        if i==R:
            for z in batch:
                counts[0]+=1
                if accept(z):
                    found.append(z)
            return
        emitted=0
        for child in join_batch(batch,order[i]):
            push(i+1,child)
            emitted+=1
            counts[3]+=1
        require(emitted<=cap,'output chunk bound')
    push(0,(-1,)*R)
    for i in range(R+1):
        flush(i)
    require(counts[0]<=W and len(set(found))==len(found),'candidate cap and no duplicates')
    require(not any(buffers),'all buffers drained')
    return found,counts


def layout(m,modes):
    n=19*m-7
    C=pool(n)
    loc={c:i for i,c in enumerate(C)}
    A=tuple(c for c in C if cross(c,R,m))
    out=[]
    for mode in modes:
        pins=tuple((i+mode)%2 for i in range(m))
        F=fixed(R,m,n,pins)
        B=tuple(c for j,c in enumerate(A) if pick(c,j,mode,m))
        require(len(set(F+B))==len(F)+len(B),'fixed overlap')
        p=sum(1<<loc[c] for c in F+B)
        raw=encoded(n,p,C)
        require(raw[:n+1]=='1'*n+'0' and len(raw)==n+1+len(C),'normalized header')
        selected=tuple(c for c in A if raw[n+1+loc[c]]=='1')
        require(selected==B,'actual pool extraction')
        bad={}
        for c in selected:
            g=tuple(group(-x,m) for x in c)
            d=tuple(digit(-x,m) for x in c)
            bad.setdefault(g,set()).add(d)
        tables=local_tables(m,bad)
        W,order=plan(tables)
        def direct(z):
            return not any(tuple(z[g] for g in h) in v for h,v in bad.items())
        expected={z for z in product(range(m),repeat=R) if direct(z)}
        # Reference final membership via local tables, separate from direct predicate.
        local=[(h,{z for z,ok in entries if ok}) for h,entries in tables]
        def accept(z):
            return all(tuple(z[g] for g in h) in vals for h,vals in local)
        found,counts=enumerate_plan(W,order,m**3,accept)
        require(set(found)==expected,'complete filtered model set')
        if found:
            require(valid(C,n,p,witness(R,m,n,pins,found[0])),'original verifier')
        if mode in (8,10):
            require(W==m**3 and len(found)==1,'functional XOR control')
        out.append([mode,W,len(expected)]+counts+
                   [sum(opt[3]==1 for opt in order),len(found)])
        if m<=3 and mode in (0,2,3,8,9,11):
            small,_=enumerate_plan(W,order,m,accept)
            require(set(small)==expected,'small-buffer model set')
    return [m,out]


EXPECTED=[
[2,[[0,512,512,512,193,2,1022,0,512],[1,0,0,0,0,0,0,0,0],[2,1,1,1,10,10,9,9,1],[3,2,2,2,10,10,18,8,2],[4,0,0,0,0,0,0,0,0],[5,8,0,6,10,10,39,6,0],[6,4,1,1,10,10,13,7,1],[7,0,0,0,0,0,0,0,0],[8,8,1,8,10,2,62,6,1],[9,512,512,512,193,2,1022,0,512],[10,8,1,8,10,2,62,6,1],[11,256,256,256,98,3,514,1,256]]],
[3,[[0,19683,19683,19683,1824,2,29523,0,19683],[1,0,0,0,0,0,0,0,0],[2,1,1,1,10,10,9,9,1],[3,3,3,3,10,10,27,8,3],[4,288,0,48,15,10,178,2,0],[5,1728,0,658,99,10,1507,0,0],[6,9,1,1,10,10,19,7,1],[7,0,0,0,0,0,0,0,0],[11,6561,6561,6561,610,3,9849,1,6561]]],
[4,[[8,64,1,64,10,2,468,6,1],[9,4096,512,4096,193,2,8148,0,512],[10,64,1,64,10,2,468,6,1],[11,65536,65536,65536,2392,3,87396,1,65536]]]]


def audit():
    rows=[layout(2,range(12)),layout(3,(0,1,2,3,4,5,6,7,11)),
          layout(4,(8,9,10,11))]
    require(rows==EXPECTED,'independent JS rows')
    flat=[row for _,v in rows for row in v]
    sums=[sum(row[i] for row in flat) for i in range(1,9)]
    require(len(flat)==25 and sums==[99344,93585,98021,5727,115,140353,83,93585],
            'aggregate')
    result={'fixtures':len(flat),'sums':sums}
    print('F038_UNRESTRICTED_FUNCTIONAL_FANOUT_OK '+
          json.dumps(result,separators=(',',':'),sort_keys=True))
    return result


if __name__=='__main__':
    audit()
