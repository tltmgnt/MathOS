"""Fixed-variable Gaussian / integer-cut proofs and exact redundant parity cut discovery."""
import json
from itertools import product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax

PLAN='docs/research/tga-universal/f038-mrax-parity-cut-discovery.json'


def parity(x):
    return x.bit_count()&1


def bits(x):
    while x:
        b=x&-x
        yield b.bit_length()-1
        x^=b


def submasks(x):
    a=x
    while True:
        yield a
        if not a:
            break
        a=(a-1)&x


def norm(c):
    s=set(c)
    return None if any(-l in s for l in s) else tuple(sorted(s))


def clause_cut(c,n):
    out=[0]*n
    for l in c:
        out[abs(l)-1]=-1 if l>0 else 1
    return tuple(out),sum(l<0 for l in c)-1


def combine_rows(A,mask):
    a=b=0
    for i in bits(mask):
        u,v=A[i]
        a^=u
        b^=v
    return a,b


def forbid(a,f):
    return tuple(sorted(-(i+1) if f>>i&1 else i+1 for i in bits(a)))


def replay(A,C,n,trace):
    require(all(type(a) is int and 0<=a<1<<n and b in (0,1) for a,b in A),'bad source rows')
    require(all(norm(c)==c and all(0<abs(l)<=n for l in c) for c in C),'bad source clauses')
    lines=[]
    for step in trace:
        kind=step[0]
        if kind=='bound':
            _,l=step
            require(type(l) is int and 0<abs(l)<=n,'bad bound')
            v=[0]*n
            v[abs(l)-1]=-1 if l>0 else 1
            line=tuple(v),int(l<0)
        elif kind=='clause':
            _,j=step
            require(type(j) is int and 0<=j<len(C),'bad source clause')
            line=clause_cut(C[j],n)
        elif kind=='cut':
            _,p,f=step
            require(type(p) is int and 0<=p<1<<len(A) and type(f) is int and f>=0,'bad cut encoding')
            a,b=combine_rows(A,p)
            require(f&~a==0 and parity(f)!=b,'not a forbidden pattern')
            line=clause_cut(forbid(a,f),n)
        elif kind=='sum':
            _,terms=step
            require(bool(terms),'empty sum')
            v=[0]*n
            rhs=0
            for j,k in terms:
                require(type(j) is int and 0<=j<len(lines) and type(k) is int and k>=0,'bad reference')
                c,d=lines[j]
                for i,a in enumerate(c):
                    v[i]+=k*a
                rhs+=k*d
            line=tuple(v),rhs
        elif kind=='div':
            _,j,k=step
            require(type(j) is int and 0<=j<len(lines) and type(k) is int and k>0,'bad divisor')
            c,d=lines[j]
            require(all(a%k==0 for a in c),'nondivisible coefficient')
            line=tuple(a//k for a in c),d//k
        else:
            raise ValueError('unknown inference')
        lines.append(line)
    return tuple(lines)


def verify(A,C,n,trace):
    try:
        lines=replay(A,C,n,trace)
        return bool(lines) and not any(lines[-1][0]) and lines[-1][1]<0
    except (ValueError,TypeError,IndexError,KeyError):
        return False


def produce(A,C,n):
    trace=[]
    def add(step):
        trace.append(step)
        return len(trace)-1
    bounds={l:add(('bound',l)) for i in range(1,n+1) for l in (-i,i)}
    db={}
    for j,c in enumerate(C):
        if c not in db:
            db[c]=add(('clause',j))
            if not c:
                return tuple(trace)
    for i,(a,b) in enumerate(A):
        for f in submasks(a):
            if parity(f)!=b:
                c=forbid(a,f)
                if c not in db:
                    db[c]=add(('cut',1<<i,f))
                    if not c:
                        return tuple(trace)
    queue=list(db)
    i=0
    while i<len(queue):
        a=queue[i]
        for b in queue[:i]:
            for l in a:
                if -l not in b:
                    continue
                U=set(a)-{l}
                V=set(b)-{-l}
                c=norm(U|V)
                if c is None or c in db:
                    continue
                terms=((db[a],1),(db[b],1))+tuple((bounds[v],1) for v in sorted(U^V))
                k=add(('sum',terms))
                if not c:
                    return tuple(trace)
                db[c]=add(('div',k,2))
                queue.append(c)
        i+=1
    return None


def basis(A,n):
    B={}
    for i,(a,b) in enumerate(A):
        v=a|(b<<n)
        p=1<<i
        while v:
            j=v.bit_length()-1
            if j not in B:
                B[j]=(v,p)
                break
            u,q=B[j]
            v^=u
            p^=q
    return tuple(B[j] for j in sorted(B))


def span_rows(A,n):
    B=basis(A,n)
    out=[(0,0)]
    for v,p in B:
        out.extend((u^v,q^p) for u,q in tuple(out))
    return tuple((v&((1<<n)-1),v>>n,p) for v,p in out)


def nearest(a,b,X,D):
    if not a:
        return (0,0) if b else None
    f=sum(1<<i for i in bits(a) if 2*X[i]>D)
    if parity(f)==b:
        i=min(bits(a),key=lambda i:(abs(D-2*X[i]),i))
        f^=1<<i
    d=sum(D-X[i] if f>>i&1 else X[i] for i in bits(a))
    return d,f


def separate(A,n,X,D):
    require(type(D) is int and D>0 and len(X)==n and all(type(x) is int and 0<=x<=D for x in X),'bad point')
    best=None
    for a,b,p in span_rows(A,n):
        r=nearest(a,b,X,D)
        if r is not None:
            d,f=r
            candidate=d,p,f
            if best is None or candidate<best:
                best=candidate
    return best


def check_cut(A,n,X,D,result):
    try:
        d,p,f=result
        if not (type(p) is int and 0<=p<1<<len(A) and type(f) is int and f>=0):
            return False
        a,b=combine_rows(A,p)
        return f&~a==0 and parity(f)!=b and d==sum(
            D-X[i] if f>>i&1 else X[i] for i in bits(a)) and d<D
    except (ValueError,TypeError,IndexError):
        return False


def satisfies(A,C,w):
    return all(parity(a&w)==b for a,b in A) and all(
        any(bool(w>>(abs(l)-1)&1)==(l>0) for l in c) for c in C)


def mixed_audit():
    R=((1,0),(3,1),(6,0),(7,1))
    F=tuple(map(norm,((-1,),(2,),(-3,),(1,2),(-2,3),(-1,-2,-3))))
    cases=checks=yes=no=models=0
    for mask in range(1024):
        A=tuple(r for i,r in enumerate(R) if mask>>i&1)
        C=tuple(c for i,c in enumerate(F) if mask>>(4+i)&1)
        ms=tuple(w for w in range(8) if satisfies(A,C,w))
        proof=produce(A,C,3)
        require((proof is None)==bool(ms),'completeness regression')
        if proof is not None:
            require(verify(A,C,3,proof),'bad produced proof')
        else:
            require(satisfies(A,C,ms[0]),'bad witness')
        cases+=1
        checks+=8
        yes+=bool(ms)
        no+=not ms
        models+=len(ms)
    return [cases,checks,yes,no,models]


def separation_audit():
    R=((1,0),(1,1),(2,0),(3,1),(4,0),(5,1),(6,0),(7,1))
    systems=points=violated=checks=rows=0
    for mask in range(256):
        A=tuple(r for i,r in enumerate(R) if mask>>i&1)
        brute={combine_rows(A,p) for p in range(1<<len(A))}
        require({(a,b) for a,b,p in span_rows(A,3)}==brute,'span mismatch')
        systems+=1
        rows+=len(brute)
        for X in product(range(5),repeat=3):
            best=None
            for a,b in brute:
                for f in submasks(a):
                    if parity(f)==b:
                        continue
                    d=sum(4-X[i] if f>>i&1 else X[i] for i in bits(a))
                    best=d if best is None else min(best,d)
                    checks+=1
            got=separate(A,3,X,4)
            require((None if got is None else got[0])==best,'minimum distance mismatch')
            if best is not None and best<4:
                require(check_cut(A,3,X,4,got),'bad cut witness')
                violated+=1
            points+=1
    return [systems,points,violated,checks,rows]


def incidence_reduce(C,q):
    # RREF of the element equations B y = 1.
    n=len(C)
    eq=[sum(1<<j for j,c in enumerate(C) if c>>i&1)|(1<<n)
        for i in range(3*q)]
    top=0
    piv=[]
    for j in range(n):
        r=next((i for i in range(top,len(eq)) if eq[i]>>j&1),None)
        if r is None:
            continue
        eq[top],eq[r]=eq[r],eq[top]
        for i in range(len(eq)):
            if i!=top and eq[i]>>j&1:
                eq[i]^=eq[top]
        piv.append(j)
        top+=1
    if any(e==1<<n for e in eq):
        return None
    y=sum(((eq[i]>>n)&1)<<j for i,j in enumerate(piv))
    K=[]
    for j in range(n):
        if j not in piv:
            K.append((1<<j)|sum(((eq[i]>>j)&1)<<k for i,k in enumerate(piv)))
    return tuple((k,0) for k in K)+((y,1),)


def x3c_audit():
    U=(7,11,21,38,56,52,42,25)
    cases=consistent=cover=cut=checks=0
    for mask in range(256):
        C=tuple(c for i,c in enumerate(U) if mask>>i&1)
        solutions=set()
        for y in range(1<<len(C)):
            z=0
            for i in bits(y):
                z^=C[i]
            if z==63:
                solutions.add(y)
            checks+=1
        want=any(y.bit_count()<=2 for y in solutions)
        A=incidence_reduce(C,2)
        require((A is not None)==bool(solutions),'incidence consistency mismatch')
        if A is None:
            got=separate((),1,(1,),2)
            yes=got is not None and got[0]<2
        else:
            n=len(C)
            require({a for a,b,p in span_rows(A,n) if b}==solutions,'coset mismatch')
            require(len(basis(A,n))==len(A),'dependent reduced rows')
            got=separate(A,n,(1,)*n,3)
            yes=got is not None and got[0]<3
            if yes:
                require(check_cut(A,n,(1,)*n,3,got),'invalid separation witness')
        require(yes==want,'reduction mismatch')
        cases+=1
        consistent+=bool(solutions)
        cover+=want
        cut+=yes
    return [cases,consistent,cover,cut,checks]


def controls():
    A=((3,1),)
    C=((-1,),(-2,))
    proof=produce(A,C,2)
    require(verify(A,C,2,proof),'valid proof rejected')
    require(not verify(A,C,2,(('cut',1,1),)),'satisfying pattern accepted')
    require(not verify(A,C,2,(('cut',2,0),)),'bad provenance accepted')
    require(not verify(A,C,2,(('bound',1),('div',0,2))),'nondivisible rounding accepted')
    require(not verify(A,C,2,proof[:-1]),'unfinished proof accepted')
    result=separate(A,2,(0,0),2)
    require(check_cut(A,2,(0,0),2,result) and not check_cut(A,2,(0,0),2,(1,result[1],result[2])),'forged distance accepted')
    return 5


def audit():
    result={'mixed':mixed_audit(),'separation':separation_audit(),'x3c':x3c_audit(),'controls':controls()}
    print('F038_MRAX_PARITY_CUT_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
