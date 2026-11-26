"""Finite exact circuit range avoidance; not a general efficient minimizer."""
import json
from itertools import product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax

PLAN='docs/research/tga-universal/f038-mrax-circuit-range-avoidance.json'


def count_bound(n,s):
    require(type(n) is int and n>=1 and type(s) is int and s>=0,'invalid dimensions')
    b=(n+s+1).bit_length()
    m=s.bit_length()+(2*s+1)*b+4*s+1
    B=(s+1)*(n+s+2)*(16*(n+s+2)**2)**s
    return m,B


def syntax_counts(n,s):
    paths=1
    sequences=1
    outputs=n+2
    for j in range(s):
        paths*=16*(n+2+j)**2
        sequences+=paths
        outputs+=paths*(n+3+j)
    return sequences,outputs


def initial(n,m):
    require(type(n) is int and type(m) is int and 1<=m<=1<<n,'invalid prefix')
    return frozenset((0,(1<<m)-1,*(sum(((i>>j)&1)<<i for i in range(m)) for j in range(n))))


def gate(a,b,t,mask):
    A=(mask^a,a)
    B=(mask^b,b)
    z=0
    for i,j in product((0,1),repeat=2):
        if t>>(2*i+j)&1:
            z|=A[i]&B[j]
    return z


def available(n,s,m):
    require(type(s) is int and s>=0,'invalid budget')
    mask=(1<<m)-1
    init=initial(n,m)
    frontier={init}
    outputs=set(init)
    for _ in range(s):
        next_states=set()
        for state in frontier:
            for a,b in product(state,repeat=2):
                for t in range(16):
                    z=gate(a,b,t,mask)
                    if z not in state:
                        next_states.add(state|{z})
                        outputs.add(z)
        frontier=next_states
    return outputs


def first_missing(R,m):
    for i,v in enumerate(sorted(R)):
        if i!=v:
            return i
    return len(R) if len(R)<1<<m else -1


def missing_completion(R,m,u,k):
    # k fixed most significant bits, represented by u.
    require(0<=k<=m and 0<=u<1<<k,'invalid completion prefix')
    left=u<<(m-k)
    right=(u+1)<<(m-k)
    return sum(left<=v<right for v in R)<right-left


def greedy(R,m):
    if not missing_completion(R,m,0,0):
        return -1
    u=0
    for k in range(1,m+1):
        u*=2
        if not missing_completion(R,m,u,k):
            u+=1
        require(missing_completion(R,m,u,k),'missing-prefix invariant failed')
    require(u not in R,'greedy returned represented word')
    return u


def audit():
    fixtures=((2,0,4),(2,1,4),(3,1,8),(3,2,8),(4,1,16),(4,2,10),(3,2,5))
    rows=[]
    ranges={}
    for n,s,m in fixtures:
        R=available(n,s,m)
        ranges[n,s,m]=R
        count,out=syntax_counts(n,s)
        gap=first_missing(R,m)
        require(greedy(R,m)==gap,'prefix search mismatch')
        require(all(v in R for v in range(gap)) if gap>=0 else len(R)==1<<m,
                'wrong least missing word')
        M,B=count_bound(n,s)
        require(len(R)<=out<=B<1<<M,'counting bound mismatch')
        rows.append([n,s,m,count,out,len(R),gap])
    require({v&31 for v in ranges[3,2,8]}==ranges[3,2,5],'prefix restriction mismatch')
    require(ranges[3,2,5]==set(range(32)),'short prefix not full')
    for n,s in ((1,0),(2,1),(16,16),(32,32),(64,64**2),(256,256**2)):
        M,B=count_bound(n,s)
        require(B.bit_length()<=M and B<1<<M,'symbolic counting bound failed')
    # Explicit malformed completion and gate semantics.
    try:
        missing_completion({0},2,4,2)
    except ValueError:
        pass
    else:
        raise ValueError('bad prefix accepted')
    require(all(gate(a,b,t,1)==((t>>(2*a+b))&1)
                for a,b,t in product((0,1),(0,1),range(16))),'gate semantics mismatch')
    result={'ranges':rows,'controls':4}
    print('F038_MRAX_CIRCUIT_AVOIDANCE_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
