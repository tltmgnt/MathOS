"""Finite streamed separator semantics; not a physical tape implementation."""
import json
import sys
from fractions import Fraction
from itertools import combinations, product

G9=tuple(range(9))
H=tuple(h for k in (1,2,3) for h in combinations(G9,k))
FIVE={tuple(sorted(4+(i+j)%5 for j in range(3))) for i in range(5)}


def require(ok,msg):
    if not ok: raise AssertionError(msg)


def project(G,z,S):
    return tuple(z[G.index(g)] for g in S)


def predicate(G,rel):
    indexed=[(tuple(G.index(g) for g in h),set(rows)) for h,rows in rel]
    return lambda z: not any(tuple(z[i] for i in ix) in rows for ix,rows in indexed)


def restrict(G,m,b,offset,rel):
    out=[]
    for h,rows in rel:
        o=project(G,offset,h)
        out.append((h,[tuple(v-a for v,a in zip(z,o)) for z in rows
                       if all(0<=v-a<b for v,a in zip(z,o))]))
    for g,a in zip(G,offset):
        pad=[(v,) for v in range(b) if a+v>=m]
        if pad: out.append(((g,),pad))
    return out


def base(G,S,m,rel,stats):
    passes=predicate(G,rel)
    msg={}
    for z in product(range(m),repeat=len(G)):
        stats[3]+=1
        if passes(z): msg.setdefault(project(G,z,S),z)
    stats[4]+=len(msg)
    return msg


def block(G,S,m,b,s,rel,stats,local_solver=base):
    N=tuple(g for g in G if g not in S)
    k=(m+b-1)//b
    acc={}
    for t in product(range(k),repeat=len(N)):
        stats[1]+=1
        off=tuple(b*(s[S.index(g)] if g in S else t[N.index(g)]) for g in G)
        local=restrict(G,m,b,off,rel)
        stats[2]+=sum(len(rows) for _,rows in local)
        msg=local_solver(G,S,b,local,stats)
        for z in msg.values():
            q=tuple(v+a for v,a in zip(z,off))
            require(all(v<m for v in q),'padding exclusion')
            x=project(G,q,S)
            stats[5]+=x in acc
            acc.setdefault(x,q)
        require(len(acc)<=b**len(S),'stationary accumulator bound')
    return acc


def tiled(G,S,m,rel,stats):
    b=2
    out={}
    for s in product(range((m+b-1)//b),repeat=len(S)):
        acc=block(G,S,m,b,s,rel,stats)
        require(not (acc.keys() & out.keys()),'disjoint local blocks')
        out.update(acc)
    return out


def forbidden(m,mode,h,z):
    if mode==0: return False
    if mode==1: return h==(8,)
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


def fixture(m,mode,repo=False):
    S=(3,4,5,6,7) if mode==8 else (2,3,4,5,6)
    A=(0,1,2) if mode==8 else (0,1)
    B=tuple(g for g in G9 if g not in S+A)
    bags=(tuple(sorted(S+A)),tuple(sorted(S+B)))
    rel=[]
    owned=[[],[]]
    for h in H:
        owner=next((i for i,G in enumerate(bags) if set(h)<=set(G)),None)
        if owner is None: continue
        rows=[z for z in product(range(m),repeat=len(h)) if forbidden(m,mode,h,z)]
        if rows:
            rel.append((h,rows))
            owned[owner].append((h,rows))
    refs=[]
    for G,R in zip(bags,owned):
        passes=predicate(G,R)
        refs.append({project(G,z,S) for z in product(range(m),repeat=len(G)) if passes(z)})
    b=3 if m==4 else 2
    stats=[0]*8
    actual=set()
    first=None
    passes=predicate(G9,rel)
    for s in product(range((m+b-1)//b),repeat=len(S)):
        stats[0]+=1
        msgs=[block(G,S,m,b,s,R,stats) for G,R in zip(bags,owned)]
        for i in range(2):
            expect={x for x in refs[i] if tuple(v//b for v in x)==s}
            require(expect==set(msgs[i]),'exact block keys')
            stats[6]+=len(expect)
            side_pass=predicate(bags[i],owned[i])
            require(all(side_pass(z) and project(bags[i],z,S)==x for x,z in msgs[i].items()),'representatives')
        for x in msgs[0].keys() & msgs[1].keys():
            require(x not in actual,'disjoint outer blocks')
            actual.add(x)
            d=dict(zip(bags[0],msgs[0][x]))
            for g,v in zip(bags[1],msgs[1][x]):
                require(g not in d or d[g]==v,'separator agreement')
                d[g]=v
            z=tuple(d[g] for g in G9)
            require(passes(z),'joined witness')
            if first is None: first=z
        stats[7]=max(stats[7],*(len(M) for M in msgs))
    expected=set()
    count=0
    for z in product(range(m),repeat=9):
        if passes(z):
            count+=1
            expected.add(project(G9,z,S))
    require(actual==expected,'global projected keys')
    if mode==8: require(count==1 and first==(0,)*9,'dense unique')
    if repo:
        from mathos.research.f038_unrestricted_distributed_hyperclique import fixed,witness
        from mathos.research.f038_unrestricted_universal_search import encoded,valid
        from mathos.research.f038_universal_witness_layout import pool
        n=19*m-7
        C=pool(n)
        pos={c:i for i,c in enumerate(C)}
        pins=tuple((i+mode)%2 for i in range(m))
        F=fixed(9,m,n,pins)
        clauses=tuple(tuple(-(g*m+v+1) for g,v in zip(h,z)) for h,rows in rel for z in rows)
        require(len(set(F+clauses))==len(F)+len(clauses),'distinct positions')
        p=sum(1<<pos[c] for c in F+clauses)
        raw=encoded(n,p,C)
        require(raw[:n+1]=='1'*n+'0' and len(raw)==n+1+len(C),'normalized header')
        selected=set(clauses)
        for h in H:
            for z in product(range(m),repeat=len(h)):
                c=tuple(-(g*m+v+1) for g,v in zip(h,z))
                require((raw[n+1+pos[c]]=='1')==(c in selected),'normalized cross bits')
        if first is not None: require(valid(C,n,p,witness(9,m,n,pins,first)),'original verifier')
    return [m,mode,sum(len(rows) for _,rows in rel),count,len(actual)]+stats


def nested_control():
    G=tuple(range(8)); S=tuple(range(3,8)); m=3
    rel=[((0,3),[(1,1),(2,0)]),((1,4,7),[(0,0,0),(2,1,2)]),((2,),[(2,)])]
    stats=[0]*8
    actual=tiled(G,S,m,rel,stats)
    ref=base(G,S,m,rel,[0]*8)
    passes=predicate(G,rel)
    require(set(actual)==set(ref) and all(passes(z) and project(G,z,S)==x for x,z in actual.items()),'nested local exactness')
    # Exercise the nested routine as the outer tile solver as well.
    stats2=[0]*8
    got=block(G,S,m,3,(0,)*5,rel,stats2,tiled)
    require(set(got)==set(ref),'nested composition')
    return [len(ref),stats,stats2]


def audit(repo=False):
    rows=[fixture(m,mode,repo) for m,modes in ((2,range(8)),(3,range(9)),(4,(8,))) for mode in modes]
    sums=[sum(row[i] for row in rows) for i in range(2,13)]
    inner=Fraction(3,10)
    inner_exp=max(10,11-5*inner,8+5*inner)
    outer=Fraction(3,7)
    outer_exp=max(6,11-5*outer,8+outer*(inner_exp-8))
    require(inner_exp==10 and outer_exp==Fraction(62,7) and outer_exp/3<3,'exponent accounting')
    result={'fixtures':len(rows),'sums':sums,'nested':nested_control(),'exponents':[str(inner_exp),str(outer_exp),str(outer_exp/3)]}
    print('F038_UNRESTRICTED_STREAMED_SEPARATORS_OK '+json.dumps(result,separators=(',',':'),sort_keys=True))
    return result


if __name__=='__main__':
    audit('--repo' in sys.argv)
