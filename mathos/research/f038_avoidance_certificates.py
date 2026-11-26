"""Finite circuit interpolation and exact local hard-word certificate complexity."""
import json
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research import f038_circuit_range_avoidance as A

PLAN='docs/research/tga-universal/f038-mrax-avoidance-certificates.json'


def interpolate(n,P):
    require(type(n) is int and n>=1,'invalid input dimension')
    P=tuple(P)
    require(all(type(x) is int and 0<=x<1<<n and type(y) is int and y in (0,1)
                for x,y in P) and len({x for x,y in P})==len(P),'invalid samples')
    gates=[]
    def add(a,b,t):
        gates.append((a,b,t))
        return n+1+len(gates)
    def rec(S):
        if not S:
            return 0
        if all(y==S[0][1] for x,y in S):
            return S[0][1]
        j=next(j for j in range(n) if any(x>>j&1 for x,y in S)
               and any(not(x>>j&1) for x,y in S))
        a=rec(tuple((x,y) for x,y in S if not(x>>j&1)))
        b=rec(tuple((x,y) for x,y in S if x>>j&1))
        x=j+2
        if a<2 and b<2:
            return a if a==b else add(x,x,1 if a else 8)
        if a<2 or b<2:
            v=b if a<2 else a
            t=sum(( (b if b<2 else z) if i else (a if a<2 else z) )<<(2*i+z)
                  for i in (0,1) for z in (0,1))
            return add(x,v,t)
        return add(add(x,a,2),add(x,b,8),14)
    o=rec(P)
    require(len(gates)<=max(0,2*len(P)-3),'gate bound exceeded')
    return tuple(gates),o


def evaluate(n,c,x):
    gates,o=c
    v=[0,1]+[(x>>j)&1 for j in range(n)]
    for a,b,t in gates:
        require(0<=a<len(v) and 0<=b<len(v) and 0<=t<16,'invalid gate')
        v.append(t>>(2*v[a]+v[b])&1)
    require(0<=o<len(v),'invalid output')
    return v[o]


def interpolation_audit():
    out=[]
    for n in (1,2,3):
        N=1<<n
        cases=checks=maxg=total=0
        for p in range(1,3**N):
            a=p
            P=[]
            for i in range(N):
                a,b=divmod(a,3)
                if b:
                    P.append((i,b-1))
            c=interpolate(n,P)
            for x,y in P:
                require(evaluate(n,c,x)==y,'interpolation mismatch')
                checks+=1
            cases+=1
            g=len(c[0])
            maxg=max(maxg,g)
            total+=g
        out.append([n,cases,checks,maxg,total])
    return out


def certificate_audit():
    out=[]
    for n,s,m in ((2,0,4),(3,1,8),(3,2,8),(4,2,10),(3,2,5)):
        R=A.available(n,s,m)
        proj=[{v&p for v in R} for p in range(1<<m)]
        K=(s+3)//2
        tests=lower=0
        hist=[0]*(m+1)
        for y in range(1<<m):
            if y in R:
                continue
            best=m
            for p,S in enumerate(proj):
                q=p.bit_count()
                ok=y&p in S
                if q<=K:
                    require(ok,'small projection obstruction')
                    lower+=1
                if not ok:
                    best=min(best,q)
                tests+=1
            require(best>K,'bad certificate threshold')
            hist[best]+=1
        out.append([n,s,m,len(R),tests,lower,hist])
    return out


def tape_threshold(s,r,b_num,b_den,q):
    require(s>=0 and r>=0 and b_den>0 and 0<=b_num<b_den and q>=0,
            'invalid randomness parameters')
    t=(b_num*(1<<r))//b_den+1
    return q*t>(s+3)//2


def controls():
    require(interpolate(2,())==((),0),'empty sample failed')
    try:
        interpolate(2,((0,0),(0,1)))
    except ValueError:
        pass
    else:
        raise ValueError('inconsistent sample accepted')
    require(not tape_threshold(30,3,1,3,5) and tape_threshold(30,3,1,3,6),
            'random tape bound mismatch')
    require(not tape_threshold(30,9,0,1,16) and tape_threshold(30,9,0,1,17),
            'perfect soundness threshold mismatch')
    return 4


def audit():
    result={'interpolation':interpolation_audit(),'certificates':certificate_audit(),'controls':controls()}
    print('F038_MRAX_AVOIDANCE_CERTIFICATES_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
