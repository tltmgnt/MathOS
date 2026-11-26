"""Finite recursive message reference; not a compiled original tape machine."""
import json
import sys
from fractions import Fraction
from itertools import combinations, product

G9=tuple(range(9))
H=tuple(h for k in (1,2,3) for h in combinations(G9,k))
BIG=tuple(range(8))
SMALL=tuple(range(4,9))
FIVE={tuple(sorted(4+(i+j)%5 for j in range(3))) for i in range(5)}
PATH=((0,1,2,3,4,5),(2,3,4,5,6,7),(4,5,6,7,8))


def require(ok,msg):
    if not ok:
        raise AssertionError(msg)


def project(G,z,h):
    return tuple(z[G.index(g)] for g in h)


def forbidden(m,mode,h,z):
    if mode==0: return False
    if mode==1: return h==(0,)
    if mode==2: return len(h)==1 and z[0]!=h[0]%m
    if mode==3: return len(h)==2 and h[1]==h[0]+1 and z[0]!=z[1]
    if mode==4: return len(h)==3 and (sum((i+2)*v for i,v in enumerate(z))+sum(h))%5==0
    if mode==5: return len(h)==3 and any(v!=(g+1)%m for g,v in zip(h,z))
    if mode==6: return len(h)==3 and not any(z)
    if len(h)==2: return z==(1,1)
    if mode==8 and len(h)==3 and (max(h)<4 or h in FIVE):
        nz=[v for v in z if v]
        return len(nz)%2==1 or len(nz)==2 and nz[0]==nz[1]
    return False


def predicate(G,rel):
    indexed=[(tuple(G.index(g) for g in h),allowed,set(rows)) for h,allowed,rows in rel]
    return lambda z: all((tuple(z[i] for i in ix) in rows)==allowed for ix,allowed,rows in indexed)


def solve(G,S,m,rel,depth,b,stats):
    stats[0]+=1
    out={}
    if depth==0:
        passes=predicate(G,rel)
        for z in product(range(m),repeat=len(G)):
            stats[2]+=1
            if passes(z):
                out.setdefault(project(G,z,S),z)
        stats[4]+=len(out)
        return out
    order=S+tuple(g for g in G if g not in S)
    k=(m+b-1)//b
    for a in product(range(k),repeat=len(S)):
        acc={}
        for c in product(range(k),repeat=len(G)-len(S)):
            stats[1]+=1
            base=tuple(b*(a+c)[order.index(g)] for g in G)
            local=[]
            for h,allowed,rows in rel:
                offsets=project(G,base,h)
                restricted=[tuple(v-o for v,o in zip(z,offsets)) for z in rows
                            if all(0<=v-o<b for v,o in zip(z,offsets))]
                local.append((h,allowed,restricted))
            for g,o in zip(G,base):
                pad=[(v,) for v in range(b) if o+v>=m]
                if pad: local.append(((g,),False,pad))
            stats[3]+=sum(len(rows) for _,_,rows in local)
            child=solve(G,S,b,local,depth-1,2,stats)
            require(len(child)<=b**len(S),'local key capacity')
            for z in child.values():
                q=tuple(v+o for v,o in zip(z,base))
                require(all(v<m for v in q),'padding')
                key=project(G,q,S)
                stats[5]+=key in acc
                acc.setdefault(key,q)
            require(len(acc)<=b**len(S),'accumulator capacity')
        require(not (out.keys() & acc.keys()),'disjoint separator blocks')
        out.update(acc)
    stats[4]+=len(out)
    return out


def fixture(m,mode,repo=False):
    bags=(BIG,SMALL) if mode==8 else (SMALL,BIG) if mode==7 else PATH
    sep=[()]+[tuple(g for g in bags[i] if g in bags[i-1]) for i in range(1,len(bags))]
    rel=[]
    owned=[[] for _ in bags]
    for h in H:
        owner=next((i for i,B in enumerate(bags) if set(h)<=set(B)),None)
        if owner is None: continue
        rows=[z for z in product(range(m),repeat=len(h)) if forbidden(m,mode,h,z)]
        if rows:
            r=(h,False,rows)
            rel.append(r)
            owned[owner].append(r)
    msg=[{} for _ in bags]
    stats=[0]*6
    keys=0
    for i in reversed(range(len(bags))):
        local=owned[i][:]
        if i+1<len(bags):
            local.append((sep[i+1],True,list(msg[i+1])))
        depth=2 if m==2 and mode==2 else 1
        msg[i]=solve(bags[i],sep[i],m,local,depth,3 if m==4 else 2,stats)
        passes=predicate(bags[i],local)
        ref={project(bags[i],z,sep[i]) for z in product(range(m),repeat=len(bags[i])) if passes(z)}
        require(ref==set(msg[i]),'exact local message')
        require(all(passes(z) and project(bags[i],z,sep[i])==k for k,z in msg[i].items()),'valid representative')
        keys+=len(ref)
    passes=predicate(G9,rel)
    count=sum(passes(z) for z in product(range(m),repeat=9))
    require(bool(count)==bool(msg[0]),'root SAT')
    z=None
    if count:
        z=[-1]*9
        for i,B in enumerate(bags):
            rep=msg[i][project(G9,z,sep[i])]
            for g,v in zip(B,rep):
                require(z[g] in (-1,v),'running intersection')
                z[g]=v
        require(passes(z),'outer witness')
    if mode==8: require(count==1 and z==[0]*9,'dense unique')
    if repo:
        from mathos.research.f038_unrestricted_distributed_hyperclique import fixed,witness
        from mathos.research.f038_unrestricted_universal_search import encoded,valid
        from mathos.research.f038_universal_witness_layout import pool
        n=19*m-7
        C=pool(n)
        pos={c:i for i,c in enumerate(C)}
        pins=tuple((i+mode)%2 for i in range(m))
        F=fixed(9,m,n,pins)
        B=tuple(tuple(-(g*m+v+1) for g,v in zip(h,t)) for h,_,rows in rel for t in rows)
        require(len(set(F+B))==len(F)+len(B),'fixed/cross disjoint')
        p=sum(1<<pos[c] for c in F+B)
        raw=encoded(n,p,C)
        require(raw[:n+1]=='1'*n+'0' and len(raw)==n+1+len(C),'normalized layout')
        require(all((raw[n+1+pos[tuple(-(g*m+v+1) for g,v in zip(h,t))]]=='1')==
                    (any(h==hh and t in rows for hh,_,rows in rel))
                    for h in H for t in product(range(m),repeat=len(h))), 'selector bits')
        if z is not None: require(valid(C,n,p,witness(9,m,n,pins,z)),'original verifier')
    return [m,mode,sum(len(rows) for _,_,rows in rel),count,keys]+stats


def dense(m):
    rel=[(h,False,[z for z in product(range(m),repeat=len(h)) if forbidden(m,8,h,z)])
         for h in H if set(h)<=set(BIG) or set(h)<=set(SMALL)]
    rel=[r for r in rel if r[2]]
    dirs=support=anti=0
    minimum=m
    for g in G9:
        tables=[]
        for h in H:
            if g not in h: continue
            p=predicate(h,[r for r in rel if set(r[0])<=set(h)])
            vals={z for z in product(range(m),repeat=len(h)) if p(z)}
            i=h.index(g)
            require({z[i] for z in vals}==set(range(m)),'full support')
            support+=m
            counts={}
            for z in vals:
                k=z[:i]+z[i+1:]
                counts[k]=counts.get(k,0)+1
            minimum=min(minimum,max(counts.values()))
            dirs+=1
            tables.append((i,vals))
        for a,b in product(range(m),repeat=2):
            if a==b: continue
            require(any(z[i]==b and z[:i]+(a,)+z[i+1:] not in V for i,V in tables for z in V),'antichain')
            anti+=1
    require(minimum>=m-2,'fanout')
    return [m,sum(len(h)==2 for h,_,_ in rel),dirs,support,anti,minimum]


def audit(repo=False):
    rows=[fixture(m,mode,repo) for m,modes in ((2,range(8)),(3,range(9)),(4,(8,))) for mode in modes]
    sums=[sum(r[i] for r in rows) for i in range(2,11)]
    require(len(rows)==18 and sums==[2572,34111,1197,2060,2010,1886432,42648,4781,2354],'independent JS totals')
    controls=[dense(m) for m in (3,4,5,8)]
    require(controls==[[3,32,333,999,54,1],[4,32,333,1332,108,2],[5,32,333,1665,180,3],[8,32,333,2664,504,6]],'dense controls')
    e=Fraction(12)
    exponents=[str(e)]
    for i in range(4):
        a=4/(e-4)
        e_new=12-4*a
        require(e_new==8+a*(e-8),'balanced cost')
        e=e_new
        exponents.append(str(e))
    require(exponents==['12','10','28/3','9','44/5'] and e/3<Fraction(3),'strict cubic slack')
    result={'fixtures':len(rows),'sums':sums,'dense':controls,'exponents':exponents}
    print('F038_UNRESTRICTED_RECURSIVE_SEPARATORS_OK '+json.dumps(result,separators=(',',':'),sort_keys=True))
    return result


if __name__=='__main__':
    audit('--repo' in sys.argv)
