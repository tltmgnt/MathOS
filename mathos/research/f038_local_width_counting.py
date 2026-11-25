"""Mixed pigeonhole local-width barrier and checked integer counting proofs."""
import json
from itertools import combinations,permutations
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax

PLAN='docs/research/tga-universal/f038-mrax-local-width-counting.json'


def source(p,m):
    require(p>=1 and m>=1,'positive dimensions required')
    A=tuple((sum(1<<(i*m+j) for j in range(m)),1) for i in range(p))
    B=tuple((i*m+j,i*m+k) for i in range(p) for j,k in combinations(range(m),2))
    B+=tuple((i*m+j,k*m+j) for j in range(m) for i,k in combinations(range(p),2))
    return A,B,p*m


def holds(A,B,n,x):
    return (0<=x<1<<n and all((a&x).bit_count()%2==b for a,b in A)
            and all(not (x>>i&1 and x>>j&1) for i,j in B))


def replay(A,B,n,trace):
    """Check row lower, complemented-clause pair, integer sum, exact divisor."""
    lines=[]
    refs=0
    for step in trace:
        kind=step[0]
        if kind=='row':
            _,j=step
            require(type(j) is int and 0<=j<len(A),'bad row index')
            a,b=A[j]
            require(type(a) is int and 0<=a<1<<n and b==1,'not odd Boolean parity')
            c=tuple(-int(a>>i&1) for i in range(n))
            rhs=-1
        elif kind=='pair':
            _,j=step
            require(type(j) is int and 0<=j<len(B),'bad pair index')
            u,v=B[j]
            require(0<=u<n and 0<=v<n and u!=v,'bad pair')
            c=tuple(int(i==u or i==v) for i in range(n))
            rhs=1
        elif kind=='sum':
            _,terms=step
            require(bool(terms),'empty sum')
            out=[0]*n
            rhs=0
            for j,w in terms:
                require(type(j) is int and 0<=j<len(lines) and type(w) is int and w>=0,'bad weighted reference')
                a,b=lines[j]
                for i,v in enumerate(a):
                    out[i]+=w*v
                rhs+=w*b
                refs+=1
            c=tuple(out)
        elif kind=='div':
            _,j,k=step
            require(type(j) is int and 0<=j<len(lines) and type(k) is int and k>0,'bad division reference')
            a,b=lines[j]
            require(all(v%k==0 for v in a),'nondivisible coefficient')
            c=tuple(v//k for v in a)
            rhs=b//k
            refs+=1
        else:
            raise ValueError('unknown proof step')
        lines.append((c,rhs))
    return tuple(lines),refs


def verify(A,B,n,trace):
    try:
        lines,_=replay(A,B,n,trace)
        return bool(lines) and not any(lines[-1][0]) and lines[-1][1]<0
    except (ValueError,TypeError,IndexError,KeyError):
        return False


def produce(p,m):
    require(p>=2,'two pigeons required for this producer')
    A,B,n=source(p,m)
    trace=[]
    def add(step):
        trace.append(step)
        return len(trace)-1
    rows=[add(('row',i)) for i in range(p)]
    ix={pair:j for j,pair in enumerate(B)}
    pairs={(j,i,k):add(('pair',ix[i*m+j,k*m+j]))
           for j in range(m) for i,k in combinations(range(p),2)}
    columns=[]
    for j in range(m):
        last=pairs[j,0,1]
        for k in range(2,p):
            q=add(('sum',((last,k-1),)+tuple((pairs[j,i,k],1) for i in range(k))))
            last=add(('div',q,k))
        columns.append(last)
    add(('sum',tuple((i,1) for i in rows+columns)))
    return tuple(trace)


def local_audit():
    out=[]
    for m in range(2,7):
        p=m+1
        scopes=tuple(tuple(i for i in range(p) if mask>>i&1)
                     for mask in range(1<<p) if mask.bit_count()<=m)
        tables={S:tuple(permutations(range(m),len(S))) for S in scopes}
        rows=sum(map(len,tables.values()))
        # Cache each projection once, including the empty scope.
        projections={}
        def proj(S,I):
            key=S,I
            if key not in projections:
                J=tuple(S.index(i) for i in I)
                projections[key]={tuple(r[j] for j in J) for r in tables[S]}
            return projections[key]
        ext=pairs=projs=0
        for S in scopes:
            if len(S)==m:
                continue
            for j in range(p):
                if j in S:
                    continue
                T=tuple(sorted(S+(j,)))
                Q=proj(T,S)
                for r in tables[S]:
                    require(r in Q,'extension failed')
                    ext+=1
        for S in scopes:
            for T in scopes:
                I=tuple(i for i in S if i in T)
                U,V=proj(S,I),proj(T,I)
                require(U==V,'projection mismatch')
                pairs+=1
                projs+=len(U)
        out.append([m,p,len(scopes),rows,ext,pairs,projs,len(tables[tuple(range(m))])])
    return out


def source_audit():
    cases=checks=sat=unsat=models=0
    for m in (2,3):
        for p in range(1,m+2):
            A,B,n=source(p,m)
            yes=0
            for x in range(1<<n):
                good=holds(A,B,n,x)
                rows=[tuple(j for j in range(m) if x>>(i*m+j)&1) for i in range(p)]
                want=all(len(r)==1 for r in rows) and len(set(rows))==p
                require(good==want,'source equivalence mismatch')
                yes+=good
                checks+=1
            require(yes==len(tuple(permutations(range(m),p))),'source count mismatch')
            if p<=m:
                x=sum(1<<(i*m+i) for i in range(p))
                require(holds(A,B,n,x),'bad positive witness')
                if p>=2:
                    require(not verify(A,B,n,produce(p,m)),'false negative proof')
            else:
                require(verify(A,B,n,produce(p,m)),'missing negative proof')
            cases+=1
            sat+=bool(yes)
            unsat+=not yes
            models+=yes
    return [cases,checks,sat,unsat,models]


def counting_audit():
    out=[]
    for m in range(2,7):
        p=m+1
        A,B,n=source(p,m)
        proof=produce(p,m)
        lines,refs=replay(A,B,n,proof)
        require(verify(A,B,n,proof) and lines[-1]==((0,)*n,m-p),'invalid proof')
        checks=0
        for k in range(2,p):
            for w in range(1<<(k+1)):
                a=(w&((1<<k)-1)).bit_count()
                b=w>>k&1
                if a<=1 and all((w>>i&1)+b<=1 for i in range(k)):
                    require(a+b<=1,'invalid counting implication')
                checks+=1
        out.append([m,len(lines),refs,checks])
    return out


def controls():
    A,B,n=source(4,3)
    trace=produce(4,3)
    require(verify(A,B,n,trace),'valid proof rejected')
    require(not verify(A,B,n,trace[:-1]),'unfinished proof accepted')
    require(not verify(A,B,n,(('row',len(A)),)+trace[1:]),'bad row accepted')
    q=next(i for i,s in enumerate(trace) if s[0]=='div')
    bad=trace[:q]+(('div',trace[q][1],trace[q][2]+1),)+trace[q+1:]
    require(not verify(A,B,n,bad),'bad division accepted')
    bad=trace[:-1]+(('sum',((len(trace),1),)),)
    require(not verify(A,B,n,bad),'forward reference accepted')
    return 4


def audit():
    result={'local':local_audit(),'source':source_audit(),'counting':counting_audit(),'controls':controls()}
    print('F038_MRAX_LOCAL_WIDTH_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
