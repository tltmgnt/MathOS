"""Reference for nine-group clustering and sparse exact-stage output verification."""
import json
from itertools import combinations, product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_unrestricted_universal_search import encoded, valid, encode_tm, decode_tm
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import (
    group, digit, cross, fixed, witness, fixture)
from mathos.research.f038_unrestricted_recursive_tiling import digit_masks, forbidden

TRIPLES=tuple(combinations(range(4),3))


def support_tables(B,m):
    tables={}
    for c in B:
        G=tuple(group(-x,m) for x in c)
        D=tuple(digit(-x,m) for x in c)
        tables.setdefault(G,set()).add(D)
    return tables


def cluster(tables,m,d):
    N=m*m
    pairs=tuple(product(range(m),repeat=2))
    rules=[[] for H in TRIPLES]
    retained=0
    for G,D in tables.items():
        j=next(i for i,H in enumerate(TRIPLES)
               if all(g==8 or g//2 in H for g in G))
        rules[j].append((G,D))
        retained+=sum(8 not in G or z[G.index(8)]==d for z in D)
    out=[]
    for H,R in zip(TRIPLES,rules):
        bits=[]
        for z in product(range(N),repeat=3):
            blocked=any(tuple(d if g==8 else pairs[z[H.index(g//2)]][g%2]
                              for g in G) in D for G,D in R)
            bits.append(not blocked)
        out.append(bits)
    return out,retained


def precompute(raw,pins):
    ones=[0]
    moment=[0]
    L=len(raw)
    m=len(pins)
    for i,v in enumerate(raw):
        ones.append(ones[-1]+(v==1))
        moment.append(moment[-1]+(i if v==1 else 0))
    def base(i):
        return raw[i] if 0<=i<L else 2
    mismatch={p:sum(base(p+i)!=b for i,b in enumerate(pins))
              for p in range(1-m,L)}
    return raw,ones,moment,mismatch


def sparse_accept(r,m,pins,tables,pre,head,edits):
    raw,ones,moment,mismatch=pre
    L=len(raw)
    n=(2*r+1)*m-r+2
    def base(i):
        return raw[i] if 0<=i<L else 2
    def counts(l,h):
        lo=max(0,min(L,l))
        hi=max(lo,min(L,h))
        o=ones[hi]-ones[lo]
        z=hi-lo-o
        b=h-l-(hi-lo)
        v=moment[hi]-moment[lo]
        for i,w in edits.items():
            if l<=i<h:
                old=base(i)
                o+=(w==1)-(old==1)
                z+=(w==0)-(old==0)
                b+=(w==2)-(old==2)
                v+=i*((w==1)-(old==1))
        return o,z,b,v
    a=[]
    for g in range(r):
        l=head+g*m
        o,z,b,v=counts(l,l+m)
        if o!=1 or b!=0:
            return False
        a.append(v-l)
    for g,j in enumerate(a):
        l=head+r*m+g*(m-1)
        k=max(0,j-1)
        if counts(l,l+k)[1]!=k or counts(l+k,l+m-1)[0]!=m-1-k:
            return False
    p=head+n-m-2
    e=mismatch.get(p,m)
    for i,w in edits.items():
        if p<=i<p+m:
            e+=(w!=pins[i-p])-(base(i)!=pins[i-p])
    if e or counts(head+n-2,head+n)[1]!=2:
        return False
    return not any(tuple(a[g] for g in G) in D for G,D in tables.items())


def audit():
    seed=1234567
    def rand(n):
        nonlocal seed
        seed=(1664525*seed+1013904223)&0xffffffff
        return seed%n
    rows=[]
    checks=accepts=trace_checks=trace_accepts=0
    r=9
    for m in (2,3):
        n=19*m-7
        N=m*m
        C=pool(n)
        loc={c:i for i,c in enumerate(C)}
        A=tuple(c for c in C if cross(c,r,m))
        all_tuples=tuple(product(range(m),repeat=r))
        full=(1<<len(all_tuples))-1
        masks=digit_masks(r,m,all_tuples)
        row=[m,0,0,0,0,0,0,0,0]
        for mode in range(8):
            pins=tuple((i+mode)%2 for i in range(m))
            planted=tuple((i+mode)%m for i in range(r))
            F=fixed(r,m,n,pins)
            B=tuple(c for j,c in enumerate(A) if mode==7 or fixture(c,j,mode,m,planted))
            require(len(set(F+B))==len(F)+len(B),'clause overlap')
            selector=sum(1<<loc[c] for c in F+B)
            raw=tuple(map(int,encoded(n,selector,C)))
            selected=tuple(c for c,v in zip(C,raw[n+1:]) if v and cross(c,r,m))
            recovered=tuple(v for c,v in zip(C,raw[n+1:]) if len(c)==3
                            and n-m-1<=c[0]<=n-2 and c[1:]==(1-n,-n))
            require(selected==B and recovered==pins,'normalized extraction')
            tables=support_tables(selected,m)
            blocked=0
            for c in B:
                blocked|=forbidden(c,m,masks,full)
            expected=full^blocked
            first=None
            count=0
            for d in range(m):
                T,k=cluster(tables,m,d)
                row[2]+=4*N**3
                row[3]+=k
                for i in range(d,len(all_tuples),m):
                    a=all_tuples[i]
                    u=tuple(a[2*g]*m+a[2*g+1] for g in range(4))
                    ok=all(t[(u[H[0]]*N+u[H[1]])*N+u[H[2]]]
                           for H,t in zip(TRIPLES,T))
                    require(ok==bool(expected>>i&1),'cluster equivalence')
                    row[4]+=1
                    if ok:
                        count+=1
                        if first is None:
                            first=a
            require(count==expected.bit_count(),'model count')
            row[1]+=1
            row[5]+=count
            row[6]+=bool(count)
            row[7]+=count==1
            pre=precompute(raw,pins)
            def base(i):
                return raw[i] if 0<=i<len(raw) else 2
            def bits(a):
                w=witness(r,m,n,pins,a)
                return tuple(w>>i&1 for i in range(n))
            def reference(h,ed):
                w=tuple(ed.get(h+i,base(h+i)) for i in range(n))
                return all(x in (0,1) for x in w) and all(
                    any(w[abs(x)-1]==int(x>0) for x in c) for c in F+B)
            for h in (-n-3,-1,0,1,n,len(raw)-1,len(raw)+4):
                for k in range(24):
                    a=first if first is not None and k%3==0 else all_tuples[rand(len(all_tuples))]
                    w=bits(a)
                    ed={h+i:v for i,v in enumerate(w) if v!=base(h+i)} if k%4 else {}
                    if k%4==2:
                        i=rand(n)
                        ed[h+i]=rand(3)
                    if k%4==3:
                        ed[h+rand(n)]=2
                    ok=sparse_accept(r,m,pins,tables,pre,h,ed)
                    require(ok==reference(h,ed),'sparse image')
                    checks+=1
                    accepts+=ok
            for _ in range(256):
                T=[(rand(2),rand(3),rand(3)-1) for j in range(3)]
                require(decode_tm(encode_tm(T,1))==(1,T),'original table encoding')
                h=0
                ed={}
                for j in range(16):
                    q,w,v=T[ed.get(h,base(h))]
                    ed[h]=w
                    h+=v
                    if q==1:
                        ok=sparse_accept(r,m,pins,tables,pre,h,ed)
                        require(ok==reference(h,ed),'halted trace')
                        trace_checks+=1
                        trace_accepts+=ok
                        break
            if first is not None:
                require(valid(C,n,selector,witness(r,m,n,pins,first)),'original verifier')
                h=len(raw)+3
                ed={h+i:v for i,v in enumerate(bits(first))}
                require(sparse_accept(r,m,pins,tables,pre,h,ed),'successful output image')
                row[8]+=1
        rows.append(row)
    result={'rows':rows,'checks':checks,'accepts':accepts,
            'traceChecks':trace_checks,'traceAccepts':trace_accepts}
    require(result=={'rows':[[2,8,4096,2923,4096,516,4,2,4],
                             [3,8,69984,13698,157464,19688,4,2,4]],
                     'checks':2688,'accepts':235,'traceChecks':3223,'traceAccepts':0},
            'independent JS totals')
    print('F038_UNRESTRICTED_ALGEBRAIC_TRANSFER_OK '+json.dumps(result,separators=(',',':'),sort_keys=True))
    return result


if __name__=='__main__':
    audit()
