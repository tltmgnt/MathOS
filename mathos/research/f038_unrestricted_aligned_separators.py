"""Reference for aligned dense messages, not a physical tape implementation."""
import json
from fractions import Fraction
from itertools import combinations, product


def require(ok, msg):
    if not ok:
        raise AssertionError(msg)


def tuples(m, k):
    return product(range(m), repeat=k)


def restrict(G, m, b, off, rel):
    result = []
    for H, rows in rel:
        o = tuple(off[G.index(g)] for g in H)
        result.append((H, {tuple(x-y for x,y in zip(z,o)) for z in rows
                           if all(0 <= x-y < b for x,y in zip(z,o))}))
    for g,o in zip(G,off):
        result.append(((g,), {(x,) for x in range(b) if o+x >= m}))
    return result


def predicate(G, rel):
    indexed = [(tuple(G.index(g) for g in H), rows) for H,rows in rel]
    return lambda z: not any(tuple(z[i] for i in ix) in rows for ix,rows in indexed)


def key(G,S,z):
    return tuple(z[G.index(g)] for g in S)


def dense_keys(t,d,k):
    return [tuple(d*j+x for j,x in zip(J,X))
            for J in tuples((t+d-1)//d,k) for X in tuples(d,k)]


def merge(dst, src, off, stats):
    require(len(dst)==len(src), 'aligned size')
    for i,z in enumerate(src):
        if z is not None:
            if dst[i] is None:
                dst[i] = tuple(x+y for x,y in zip(z,off))
            else:
                stats[2] += 1
        stats[3] += 1


def local(G,S,t,rel,d,stats):
    """Dense padded block order, every slot present even when invalid."""
    private = tuple(g for g in G if g not in S)
    k = (t+d-1)//d
    out = []
    for J in tuples(k,len(S)):
        acc = [None]*(d**len(S))
        for P in tuples(k,len(private)):
            off = tuple(d*(J[S.index(g)] if g in S else P[private.index(g)]) for g in G)
            passes = predicate(G,restrict(G,t,d,off,rel))
            src = [None]*len(acc)
            for z in tuples(d,len(G)):
                stats[0] += 1
                if passes(z):
                    i = 0
                    for a in key(G,S,z): i = i*d+a
                    if src[i] is None: src[i] = z
            stats[1] += 1
            merge(acc,src,off,stats)
        out.extend(acc)
    keys = dense_keys(t,d,len(S))
    require(len(out)==len(keys), 'dense output extent')
    passes = predicate(G,rel)
    ref = {key(G,S,z) for z in tuples(t,len(G)) if passes(z)}
    got = set()
    for k,z in zip(keys,out):
        if z is not None:
            require(all(0<=a<t for a in z) and key(G,S,z)==k and passes(z),'slot representative')
            got.add(k)
    require(got==ref,'complete local message')
    stats[4] += len(out)
    return out


def fixture(m,mode):
    G=tuple(range(9)); u,v=((0,8) if mode%2 else (7,8))
    S=tuple(g for g in G if g not in (u,v))
    bags=tuple(tuple(g for g in G if g!=h) for h in (v,u))
    rel=[]; owned=[[],[]]
    for k in (1,2,3):
        for H in combinations(G,k):
            if u in H and v in H: continue
            def bad(z):
                if mode==0: return False
                if mode==1: return H==(v,)
                if mode==2: return len(H)==1 and z[0]!=H[0]%m
                if mode==3: return len(H)==2 and z==(1,1)
                if mode==4: return len(H)==3 and (sum(H)+sum((i+2)*a for i,a in enumerate(z)))%5==0
                return len(H)==3 and any(a!=0 for a in z)
            rows={z for z in tuples(m,k) if bad(z)}
            if rows:
                r=(H,rows); rel.append(r)
                owned[next(i for i,B in enumerate(bags) if set(H)<=set(B))].append(r)
    b=2; d=2
    stats=[0]*5; blocks=0; tiles=0; actual=set(); first=None
    slots=dense_keys(b,d,len(S))
    for J in tuples((m+b-1)//b,len(S)):
        accs=[]; blocks+=1
        for B,R in zip(bags,owned):
            p=next(g for g in B if g not in S)
            acc=[None]*len(slots)
            for j in range((m+b-1)//b):
                off=tuple(b*(J[S.index(g)] if g in S else j) for g in B)
                out=local(B,S,b,restrict(B,m,b,off,R),d,stats)
                merge(acc,out,off,stats); tiles+=1
            accs.append(acc)
        for i,(x,y) in enumerate(zip(*accs)):
            if x is None or y is None: continue
            k=tuple(b*j+a for j,a in zip(J,slots[i]))
            require(key(bags[0],S,x)==key(bags[1],S,y)==k,'aligned intersection')
            z=dict(zip(bags[0],x)); z.update(zip(bags[1],y))
            z=tuple(z[g] for g in G)
            require(predicate(G,rel)(z) and all(a<m for a in z),'global witness')
            require(k not in actual,'disjoint blocks'); actual.add(k)
            if first is None: first=z
    passes=predicate(G,rel)
    models=[z for z in tuples(m,9) if passes(z)]
    require(actual=={key(G,S,z) for z in models},'exact global projection')
    return [m,mode,sum(len(r) for _,r in rel),len(models),len(actual),blocks,tiles,*stats]


def carry_checks():
    count=0
    for N in range(1,6):
        for work in tuples(2,N):
            for start in (1,2,3):
                for step in (-1,1):
                    stationary=tuple((i*3+start)%7 for i in range(N+6))
                    a=[[v,None] for v in stationary]
                    for i,v in enumerate(work,start): a[i][1]=v
                    carry=None
                    scan=range(start,start+N+1) if step==1 else range(start+N-1,start-2,-1)
                    for i in scan: carry,a[i][1]=a[i][1],carry
                    require(carry is None,'blank fringe')
                    require(tuple(x[0] for x in a)==stationary,'stationary preserved')
                    require([x[1] for x in a]==[None]*(start+step)+list(work)+[None]*(len(a)-start-step-N),'shift')
                    count+=1
    return count


def audit():
    rows=[fixture(m,mode) for m in (2,3) for mode in range(6)]
    G=tuple(range(8)); S=tuple(range(1,8)); stats=[0]*5
    out=local(G,S,3,[((0,1,2),{(1,1,1)}),((3,),{(2,)})],2,stats)
    require(len(out)==4**7,'nested padding extent')
    nested=[sum(z is not None for z in out),len(out),*stats]
    e=max(Fraction(10),11-5*Fraction(1,4),8+7*Fraction(1,4))
    outer=max(Fraction(6),11-5*Fraction(3,7),8+(e-8)*Fraction(3,7))
    require(e==10 and outer==Fraction(62,7) and outer/3<3,'clock exponent')
    result={'fixtures':len(rows),'sums':[sum(r[i] for r in rows) for i in range(2,12)],'nested':nested,'shifts':carry_checks(),'exponents':[str(e),str(outer),str(outer/3)]}
    print('F038_UNRESTRICTED_ALIGNED_SEPARATORS_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    audit()
