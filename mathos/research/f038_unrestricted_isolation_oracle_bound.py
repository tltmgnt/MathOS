"""Finite shattering and black-box isolation controls; not an original U solver."""
import json
from itertools import combinations, product
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_unrestricted_crossing_adversary import norm, true
from mathos.research.f038_unrestricted_universal_search import encoded, valid
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import fixed, witness


def structural(m):
    G=[]
    for h in range(3):
        g=3*h
        G.append(tuple(-(a*m+1) for a in range(g,g+3)))
        for a,b in combinations(range(g,g+3),2):
            for i,j in product(range(1,m),repeat=2):
                G.append((-(a*m+i+1),-(b*m+j+1)))
    D=3*(m-1)
    A=[tuple(-((3*h+v//(m-1))*m+v%(m-1)+2)
             for h,v in enumerate(d))
       for d in product(range(D),repeat=3)]
    return tuple(G),tuple(A)


def violation(c,z,m):
    return all(z[(-x-1)//m]==(-x-1)%m for x in c)


def index(z,m):
    D=3*(m-1)
    i=0
    for h in range(3):
        g=3*h
        k=next(k for k in range(3) if z[g+k])
        i=i*D+k*(m-1)+z[g+k]-1
    return i


def allowed(mode,i,N):
    return (mode==0 or (mode==2 and i==0) or
            (mode==3 and i%2==0) or (mode==4 and i%3==0) or
            (mode==5 and (i*17+3)%31<7) or
            (mode==6 and i!=0) or (mode==7 and i==N-1))


def layout(m):
    r=9
    n=19*m-7
    C=pool(n)
    L=n+1+len(C)
    pos={c:i for i,c in enumerate(C)}
    require(L==n+1+2*n*n+8*comb(n,3),'normalized length')
    F=fixed(r,m,n,(0,)*m)
    G,A=structural(m)
    N=len(A)
    require(len(G)==9*(m-1)**2+3 and N==27*(m-1)**3,'structural counts')
    require(len(set(F+G+A))==len(F)+len(G)+N and
            all(c in pos for c in F+G+A),'distinct pool slots')
    survivors=[]
    structural_checks=private_checks=0
    for z in product(range(m),repeat=9):
        expected=all(sum(v!=0 for v in z[3*h:3*h+3])==1 for h in range(3))
        ok=not any(violation(c,z,m) for c in G)
        require(ok==expected,'structural predicate')
        structural_checks+=1
        if ok:
            survivors.append(z)
    require(len(survivors)==N,'universe size')
    seen=set()
    for z in survivors:
        w=witness(r,m,n,(0,)*m,z)
        require(all(true(c,w) for c in F+G),'full fixed witness')
        hits=[i for i,c in enumerate(A) if violation(c,z,m)]
        private_checks+=N
        require(hits==[index(z,m)] and hits[0] not in seen,'private clause bijection')
        seen.add(hits[0])
    fixtures=mask_checks=models=0
    slots=[pos[c] for c in A]
    for mode in range(8):
        flags=[allowed(mode,i,N) for i in range(N)]
        B=tuple(c for i,c in enumerate(A) if not flags[i])
        raw=bytearray(len(C))
        for c in F+G+B:
            raw[pos[c]]=1
        count=0
        first=None
        for z in survivors:
            ok=not any(raw[j] and violation(c,z,m) for c,j in zip(A,slots))
            require(ok==flags[index(z,m)],'realized subset')
            mask_checks+=1
            if ok:
                count+=1
                if first is None:
                    first=z
        require(count==sum(flags),'subset cardinality')
        # Selected controls use the actual normalized encoder and verifier.
        if m<=3 and mode in (0,1,2,7):
            p=sum(1<<pos[c] for c in F+G+B)
            require(encoded(n,p,C)=='1'*n+'0'+''.join(map(str,raw)),
                    'actual normalized selector')
            if first is not None:
                require(valid(C,n,p,witness(r,m,n,(0,)*m,first)),'original verifier')
        fixtures+=1
        models+=count
    return [m,n,L,len(G),N,structural_checks,private_checks,
            fixtures,mask_checks,models]


def peeling(N):
    full=(1<<N)-1
    lists=removals=0
    minimum,maximum=N,0
    for k in range(N):
        for R in combinations(range(full+1),k):
            V=full
            while True:
                S=next((S for S in R if (S&V).bit_count()==1),None)
                if S is None:
                    break
                V&=~S
                removals+=1
            require(V!=0 and all((S&V).bit_count()!=1 for S in R),'all-NO adversary')
            lists+=1
            minimum=min(minimum,V.bit_count())
            maximum=max(maximum,V.bit_count())
    for V in range(1,full+1):
        require(any((V&(1<<i)).bit_count()==1 for i in range(N)),'singleton upper')
    return [N,lists,removals,minimum,maximum]


def telescoping():
    checks=0
    for m in (2,3,4,8,16,32,64):
        K=m.bit_length()
        for a in range(m+1):
            total=0
            for j in range(K):
                b=1<<j
                # Common denominator (2b)^a for the inequality.
                lhs=a*(b-1)**(a-1)*2**a if a else 0
                rhs=2*((2*b-1)**a-(2*(b-1))**a)
                require(lhs<=rhs,'dyadic integral bound')
                # Sum singleton probabilities with denominator (2^(K-1))^a.
                if a:
                    total+=a*(b-1)**(a-1)*(1<<(a*(K-1-j)))
                checks+=1
            require(total<=2*(1<<(a*(K-1))),'telescoping sum')
    return checks


def audit():
    layouts=[layout(m) for m in (2,3,4)]
    require(layouts==[[2,31,37914,12,27,512,729,8,216,84],
                      [3,50,161851,39,216,19683,46656,8,1728,662],
                      [4,69,428744,84,729,262144,531441,8,5832,2232]],
            'independent JS structural totals')
    peels=[peeling(N) for N in range(1,5)]
    require(peels==[[1,1,0,1,1],[2,5,2,1,2],[3,37,30,1,3],[4,697,712,1,4]],
            'independent JS peeling totals')
    inequalities=telescoping()
    require(inequalities==803,'dyadic count')
    result={'layouts':layouts,'peels':peels,'inequalities':inequalities}
    print('F038_UNRESTRICTED_ISOLATION_ORACLE_BOUND_OK '+
          json.dumps(result,separators=(',',':'),sort_keys=True))
    return result


if __name__=='__main__':
    audit()
