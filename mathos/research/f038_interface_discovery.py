"""Certified bounded private-scope interface discovery and guarded block recovery."""
import json
from itertools import combinations
from mathos.research.f038_bounded_inference import block_project,lift_blocks,require
from mathos.research.f038_affine_recovery import cycle_source
from mathos.research.f038_resolution_certificate import split_cube,encode
from mathos.research import f038_hybrid_affine as H
from mathos.research import f038_guarded_affine as G
from mathos.research.f038_guarded_learning import base_db,canonical,mode
from mathos.research.f038_mrax_cycle import run_mrax

PLAN='docs/research/tga-universal/f038-mrax-interface-discovery.json'


def bits(mask):
    while mask:
        b=mask&-mask
        yield b.bit_length()-1
        mask^=b


def graph(n,edges):
    a=[0]*n
    for u,v in edges:
        a[u]|=1<<v
        a[v]|=1<<u
    return tuple(a)


def primal(f,n):
    return graph(n,((u-1,v-1) for c in f for u,v in combinations(
        sorted(set(map(abs,c))),2)))


def neighborhood(a,C):
    out=C
    for u in bits(C):
        out|=a[u]
    return out


def component(a,remaining):
    C=remaining&-remaining
    while True:
        D=neighborhood(a,C)&remaining
        if D==C:
            return C
        C=D


def admissible(a,I,h):
    remaining=((1<<len(a))-1)&~I
    while remaining:
        C=component(a,remaining)
        if neighborhood(a,C).bit_count()>h:
            return False
        remaining^=C
    return True


def core(a,I,h):
    remaining=((1<<len(a))-1)&~I
    while remaining:
        C=component(a,remaining)
        if neighborhood(a,C).bit_count()>h:
            if C.bit_count()<=h:
                return C
            S=C&-C
            while S.bit_count()<h+1:
                b=neighborhood(a,S)&C&~S
                require(bool(b),'disconnected core')
                S|=b&-b
            return S
        remaining^=C
    return 0


def valid_core(a,S,h):
    return (type(S) is int and 0<S<1<<len(a) and S.bit_count()<=h+1
            and component(a,S)==S and neighborhood(a,S).bit_count()>h)


def exact(a,h,k):
    require(h>=3 and k>=0)
    def visit(I,left):
        S=core(a,I,h)
        if not S:
            return I
        if not left:
            return None
        for v in bits(S):
            r=visit(I|1<<v,left-1)
            if r is not None:
                return r
        return None
    return visit(0,min(k,len(a)))


def greedy(a,h):
    require(h>=3)
    I=0
    pack=[]
    while True:
        S=core(a,I,h)
        if not S:
            return I,tuple(pack)
        pack.append(S)
        I|=S


def verify_pack(a,h,I,pack):
    try:
        if h<3 or type(I) is not int or not 0<=I<1<<len(a):
            return False
        seen=0
        for S in pack:
            if not valid_core(a,S,h) or seen&S:
                return False
            seen|=S
        return seen==I and admissible(a,I,h)
    except (TypeError,ValueError,IndexError):
        return False


def graph_audit():
    graphs=cases=interfaces=valid=monotonic=obstructions=budgets=packs=vertices=optima=0
    edges=tuple(combinations(range(5),2))
    for mask in range(1<<len(edges)):
        a=graph(5,(e for i,e in enumerate(edges) if mask>>i&1))
        graphs+=1
        for h in (3,4):
            vs=tuple(admissible(a,I,h) for I in range(32))
            opt=min(I.bit_count() for I in range(32) if vs[I])
            cases+=1
            optima+=opt
            for I in range(32):
                S=core(a,I,h)
                require(bool(S)==(not vs[I]))
                interfaces+=1
                valid+=vs[I]
                if S:
                    require(valid_core(a,S,h) and not S&I)
                for J in range(32):
                    if I&J!=I:
                        continue
                    if vs[I]:
                        require(vs[J])
                        monotonic+=1
                    if S and vs[J]:
                        require(bool(S&J))
                        obstructions+=1
            for k in range(6):
                I=exact(a,h,k)
                require((I is not None)==(opt<=k))
                if I is not None:
                    require(vs[I] and I.bit_count()<=k)
                budgets+=1
            I,P=greedy(a,h)
            require(verify_pack(a,h,I,P) and len(P)<=opt and I.bit_count()<=(h+1)*opt)
            packs+=len(P)
            vertices+=I.bit_count()
    return [graphs,cases,interfaces,valid,monotonic,obstructions,budgets,packs,vertices,optima]


def padded(n,edges):
    K=[]
    r=n
    for u,v in edges:
        K.extend(((u,r),(r,r+1),(r+1,v)))
        r+=2
    deg=[0]*r
    for u,v in K:
        deg[u]+=1
        deg[v]+=1
    require(max(deg,default=0)<=3)
    E=list(K)
    N=r
    for u,d in enumerate(deg):
        for _ in range(3-d):
            E.append((u,N))
            N+=1
    return graph(N,E),tuple(K),r


def cover(E,I):
    return all(I&((1<<u)|(1<<v)) for u,v in E)


def reduction_audit():
    graphs=tests=extensions=minimum=0
    edges=tuple(combinations(range(3),2))
    for mask in range(8):
        E=tuple(e for i,e in enumerate(edges) if mask>>i&1)
        a,K,r=padded(3,E)
        tau=min(I.bit_count() for I in range(8) if cover(E,I))
        opt=len(a)
        for I in range(1<<len(a)):
            if admissible(a,I,4):
                require(cover(K,I))
                opt=min(opt,I.bit_count())
            tests+=1
        for I in range(1<<r):
            if cover(K,I):
                require(admissible(a,I,4))
            extensions+=1
        require(opt==tau+len(E))
        minimum+=opt
        graphs+=1
    return [graphs,tests,extensions,minimum]


def occurrence_interface(f,n,threshold=4):
    counts=[0]*n
    for c in f:
        for l in c:
            counts[abs(l)-1]+=1
    return tuple(i+1 for i,c in enumerate(counts) if c>threshold)


def projected(f,n,I,h,blocks):
    if blocks is None or blocks!=block_project(f,n,I,h):
        return None
    out=[]
    supports=[]
    for ids,B,table in blocks:
        allowed=dict(table)
        if len(B)>3:
            return None
        for z in range(1<<len(B)):
            if z not in allowed:
                out.append(tuple(-v if z>>j&1 else v for j,v in enumerate(B)))
                supports.append(ids)
    return tuple(out),tuple(supports)


def affine_projection(f,n,I,h,blocks):
    result=projected(f,n,I,h,blocks)
    if result is None:
        return None
    p,supports=result
    rows,rest=H.extract(p)
    require(H.verify_partition(p,rows,rest))
    if rest:
        return None
    g=tuple(sorted((a,b,tuple(sorted({n+j+1 for i in ids for j in supports[i]})))
                   for a,b,ids in rows))
    return p,g


def family_audit():
    out=[]
    for d in (2,3,4):
        nv,edges=split_cube(d)
        z=len(edges)+1
        f=encode(nv,edges,1)
        hard,n=cycle_source(f,z)
        I=occurrence_interface(hard,n)
        require(I==tuple(range(1,z+1)))
        a=primal(hard,n)
        mask=sum(1<<(v-1) for v in I)
        require(admissible(a,mask,6))
        blocks=block_project(hard,n,I,6)
        require(blocks is not None and len(blocks)==len(f))
        p,g=affine_projection(hard,n,I,6,blocks)
        require(sorted(map(canonical,p))==sorted(map(canonical,f)))
        require(len(g)==nv)
        base,N=base_db(hard,n)
        A=mode(hard,n,-1)
        wrong=A+(-z,)
        state,trace=G.conflict(base,N,g,wrong)
        require(state is None and trace[-1][0]=='x')
        c=canonical(-l for l in wrong)
        # Recompute with the exact pin order used by the certificate verifier.
        state,trace=G.conflict(base,N,g,tuple(-l for l in c))
        require(state is None)
        checked=list(base)
        require(G.check_step(checked,N,g,wrong,(((c,trace),),None,len(base))))
        basis,bad=H.reduce(tuple((a,b,()) for a,b,_ in g),1<<(z-1),1<<(z-1))
        require(basis is not None)
        w=1<<(z-1)
        for bit,(a,b,_) in basis.items():
            if b:
                w|=bit
        w=lift_blocks(hard,n,I,w,blocks,6)
        require(w is not None)
        w|=((1<<len(hard))-1)<<n
        require(G.check_step(checked,N,g,A+(z,),((),w,None)))
        out.append([d,len(I),len(blocks),len(g)])
    return out


def controls():
    a=graph(5,tuple(combinations(range(5),2)))
    I,P=greedy(a,3)
    require(verify_pack(a,3,I,P))
    require(not verify_pack(a,3,I,P+P))
    require(not verify_pack(a,3,0,P))
    f=((1,2),(1,3))
    blocks=block_project(f,3,(1,),3)
    require(blocks is not None)
    ids,B,T=blocks[0]
    altered=((ids,B,T[:-1]),)+blocks[1:]
    require(projected(f,3,(1,),3,altered) is None)
    require(block_project(f,3,(),2) is None)
    return 4


def audit():
    result={'graphs':graph_audit(),'reduction':reduction_audit(),
            'families':family_audit(),'controls':controls()}
    print('F038_MRAX_INTERFACE_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
