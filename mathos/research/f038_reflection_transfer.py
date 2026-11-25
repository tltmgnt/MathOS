"""Finite guarded rejection reflection and checked ordinary resolution transfers."""
import json
from itertools import product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax

PLAN='docs/research/tga-universal/f038-mrax-reflection-transfer.json'


def norm(c):
    s=set(c)
    return None if any(-l in s for l in s) else tuple(sorted(s))


def sat(F,w):
    return all(any(bool(w>>(abs(l)-1)&1)==(l>0) for l in c) for c in F)


def carrier(n,w):
    return tuple(((i+1) if w>>i&1 else -(i+1),) for i in range(n))


def reject(G,n,F):
    if len(F)!=n or any(len(c)!=1 or abs(c[0])!=i+1 for i,c in enumerate(F)):
        return 'UNKNOWN'
    w=sum(1<<i for i,c in enumerate(F) if c[0]>0)
    return 'REJECT' if sat(G,w) else 'UNKNOWN'


def reflection(G,n):
    R=[]
    for i,c in enumerate(G):
        require(norm(c)==c and all(0<abs(l)<=n for l in c),'invalid source clause')
        z=n+i+1
        R.extend(((z,),norm((-z,)+c)))
        R.extend(norm((z,-l)) for l in c)
    return tuple(R)


def resolve(a,b,p):
    require(p in a and -p in b,'invalid pivot')
    c=norm(tuple(l for l in a if l!=p)+tuple(l for l in b if l!=-p))
    require(c is not None,'tautological resolvent')
    return c


def replay(F,proof):
    seen=[]
    for step in proof:
        c,reason=step
        require(norm(c)==c and all(l!=0 for l in c),'invalid clause')
        if reason[0]=='ax':
            _,j=reason
            require(type(j) is int and 0<=j<len(F) and c==F[j],'invalid axiom')
        elif reason[0]=='res':
            _,i,j,p=reason
            require(type(i) is int and type(j) is int and 0<=i<len(seen)
                    and 0<=j<len(seen) and type(p) is int,'invalid reference')
            require(c==resolve(seen[i],seen[j],p),'wrong resolvent')
        else:
            raise ValueError('invalid rule')
        seen.append(c)
    return tuple(seen)


def verify(F,proof):
    try:
        lines=replay(F,proof)
        return bool(lines) and lines[-1]==()
    except (ValueError,TypeError,IndexError,KeyError):
        return False


def produce(F):
    proof=[]
    index={}
    def add(c,r):
        index[c]=len(proof)
        proof.append((c,r))
    for i,c in enumerate(F):
        if c not in index:
            add(c,('ax',i))
            if not c:
                return tuple(proof)
    i=0
    while i<len(proof):
        a=proof[i][0]
        for j in range(i):
            b=proof[j][0]
            for p in a:
                if -p not in b:
                    continue
                c=norm(tuple(l for l in a if l!=p)+tuple(l for l in b if l!=-p))
                if c is None or c in index:
                    continue
                add(c,('res',i,j,p))
                if not c:
                    return tuple(proof)
        i+=1
    return None


def lift(G,n,proof):
    require(verify(G,proof),'invalid source proof')
    R=reflection(G,n)
    out=[]
    axioms={}
    def add(c,r):
        out.append((c,r))
        return len(out)-1
    # Derive only axioms used by the source proof, lazily.
    offsets=[]
    offset=0
    for c in G:
        offsets.append(offset)
        offset+=2+len(c)
    mapping=[]
    for c,reason in proof:
        if reason[0]=='ax':
            _,i=reason
            if i not in axioms:
                z=n+i+1
                j=offsets[i]
                a=add(R[j],('ax',j))
                b=add(R[j+1],('ax',j+1))
                axioms[i]=add(c,('res',a,b,z))
            q=axioms[i]
        else:
            _,i,j,p=reason
            q=add(c,('res',mapping[i],mapping[j],p))
        mapping.append(q)
    # A refutation may end by repeating an already-used empty axiom.
    # Truncate to the mapped final empty clause; every earlier reference remains valid.
    out=tuple(out[:mapping[-1]+1])
    require(verify(R,out),'invalid lifted proof')
    return out


def restricted(c,pins):
    if any(l in pins for l in c):
        return None
    return tuple(l for l in c if -l not in pins)


def restrict(F,proof,pins):
    require(verify(F,proof),'invalid proof before restriction')
    pins=set(pins)
    require(all(l!=0 and -l not in pins for l in pins),'inconsistent pins')
    reduced=tuple(c for c in (restricted(c,pins) for c in F) if c is not None)
    axmap={}
    k=0
    for j,c in enumerate(F):
        if restricted(c,pins) is not None:
            axmap[j]=k
            k+=1
    out=[]
    mapping=[]
    def add(c,r):
        out.append((c,r))
        return len(out)-1
    for c,reason in proof:
        d=restricted(c,pins)
        if d is None:
            mapping.append(None)
            continue
        if reason[0]=='ax':
            q=add(d,('ax',axmap[reason[1]]))
        else:
            _,i,j,p=reason
            a,b=mapping[i],mapping[j]
            if p in pins:
                require(b is not None,'missing surviving parent')
                q=b
            elif -p in pins:
                require(a is not None,'missing surviving parent')
                q=a
            else:
                require(a is not None and b is not None,'missing parents')
                A,B=out[a][0],out[b][0]
                if p not in A:
                    q=a
                elif -p not in B:
                    q=b
                else:
                    q=add(resolve(A,B,p),('res',a,b,p))
        require(set(out[q][0])<=set(d),'restriction subclause invariant')
        mapping.append(q)
    require(mapping[-1] is not None,'empty clause disappeared')
    out=tuple(out[:mapping[-1]+1])
    require(verify(reduced,out),'restricted proof rejected')
    return reduced,out


def width(proof):
    return max((len(c) for c,r in proof),default=0)


def fixture(R):
    n=3
    stats=[0]*8
    transfers=0
    for mask in range(256):
        G=tuple(norm(c) for i,c in enumerate(R) if mask>>i&1)
        H=reflection(G,n)
        m=len(G)
        ms=[]
        for w in range(1<<n):
            good=sat(G,w)
            require((reject(G,n,carrier(n,w))=='REJECT')==good,'guard mismatch')
            require(sat(carrier(n,w),w),'carrier not satisfiable')
            stats[1]+=1
            if good:
                ms.append(w)
            for z in range(1<<m):
                require(sat(H,w|(z<<n))==(good and z==(1<<m)-1),'reflection mismatch')
                stats[2]+=1
        proof=produce(G)
        require((proof is None)==bool(ms),'source completeness regression')
        if proof is not None:
            require(verify(G,proof),'bad source proof')
            p=lift(G,n,proof)
            require(len(p)<=len(proof)+3*m and width(p)<=max(2,width(proof),1+max(map(len,G),default=0)),
                    'lift cost exceeded')
            F,q=restrict(H,p,tuple(n+i+1 for i in range(m)))
            require(F==G and verify(G,q) and len(q)<=len(p) and width(q)<=width(p),'bad restriction')
            transfers+=1
        stats[0]+=1
        stats[3]+=len(ms)
        stats[4]+=bool(ms)
        stats[5]+=not ms
        stats[6]+=len(H)
        stats[7]+=m
    return stats,transfers


def controls():
    G=((-1,),(1,))
    p=produce(G)
    require(verify(G,p),'valid proof rejected')
    require(not verify(G,p[:-1]),'unfinished proof accepted')
    require(not verify(G,p[:-1]+(((),('res',0,99,-1)),)),'forward reference accepted')
    require(reject(((1,),),1,((1,2),))=='UNKNOWN','noncarrier rejected')
    require(reject(((1,),),1,((1,),))=='REJECT' and sat(((1,),),1),'counterexample missing')
    # A restriction with an unfixed pivot exercises the general transfer rule.
    G2=((-2,-1),(-2,1),(2,))
    q=produce(G2)
    F,r=restrict(G2,q,(2,))
    require(F==((-1,),(1,)) and verify(F,r) and len(r)<=len(q),'general restriction failed')
    return 5


def audit():
    primary=((-1,),(1,),(-2,),(2,),(-3,),(3,),(-1,-2),(2,3))
    full=tuple(tuple(-(i+1) if w>>i&1 else i+1 for i in range(3)) for w in range(8))
    a,p=fixture(primary)
    b,q=fixture(full)
    result={'primary':a,'full':b,'transfers':p+q,'controls':controls()}
    print('F038_MRAX_REFLECTION_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
