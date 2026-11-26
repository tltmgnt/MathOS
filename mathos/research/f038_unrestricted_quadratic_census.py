"""Exact quadratic residual census amplification; finite semantic checks."""
import json
from collections import defaultdict
from fractions import Fraction
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_unrestricted_quadratic_stage import (
    weight_bound,dimensions,encoding,machines,pack,length)
from mathos.research.f038_unrestricted_crossing_adversary import trace,tiny,reason,true
from mathos.research.f038_unrestricted_universal_search import encode_tm,decode_tm

PLAN='docs/research/tga-universal/f038-unrestricted-quadratic-census.json'


def traces():
    rows=[]
    for q in (1,2,3):
        st=[q,0,0,0,0,0,0,0,0]
        for T in machines(q):
            d=encode_tm(T,q)
            require(len(d)==length(q) and decode_tm(d)==(q,list(T)),'syntax')
            st[1]+=1
            for t in (1,4,8):
                for c in (2,3,4):
                    G=defaultdict(list)
                    K=[]
                    for a in range(4):
                        v=trace(T,q,tiny(a,a^3),t,c,2)
                        k=pack(v,a,a^3,q)
                        K.append(k)
                        G[(a.bit_count(),k)].append(a)
                        st[2]+=1
                    mass=sum(len(A)**2 for A in G.values())
                    require(mass*len(G)>=16,'square bound')
                    st[3]+=len(G)
                    st[4]+=mass
                    st[5]+=mass-4
                    for A in G.values():
                        for a in A:
                            for b in A:
                                if a==b:
                                    continue
                                v=trace(T,q,tiny(a,b^3),t,c,2)
                                require(pack(v,a,b^3,q)==K[a] and reason(v,a,b^3)!=-2,
                                        'cross rejection')
                                d=(a^b).bit_count()
                                j=(b&~a).bit_count()
                                require(d==2*j and j>0,'equal-weight cross')
                                st[6]+=1
                                st[7]+=j
                                st[8]+=d
        rows.append(st)
    return rows


def partitions():
    rows=[]
    for M in (4,6,8,10,12):
        N=1<<M
        G=defaultdict(list)
        for a in range(N):
            G[(a.bit_count(),a&((1<<(M//2))-1))].append(a)
        all_pairs=near=far=models=0
        for A in G.values():
            for a in A:
                for b in A:
                    all_pairs+=1
                    d=(a^b).bit_count()
                    if d<=M//4:
                        near+=1
                    else:
                        far+=1
                        j=(b&~a).bit_count()
                        require(d==2*j,'distance identity')
                        models+=j
        ball=sum(comb(M,i) for i in range(M//4+1))
        require(all_pairs*len(G)>=N*N and near<=N*ball and near+far==all_pairs,
                'partition inequalities')
        rows.append([M,N,len(G),all_pairs,near,far,ball,models])
    return rows


def controls():
    require(weight_bound()<Fraction(1,5000) and
            Fraction(1995,4*1331**2)>Fraction(1,4000) and
            Fraction(3,4*11**3)>Fraction(1,2000),'parent constants')
    require(65**32<2*64**32 and Fraction(23,20)>Fraction(57,50)>Fraction(9,8),
            'ball and exponent slack')
    for m in (3,4):
        C,A,B,W=encoding(m,1)
        n,M,*_=dimensions(m)
        # Guards are irrelevant to the complete lifted-pin conjunction,
        # despite occurring syntactically. All non-guard unused bits are absent.
        used={abs(l) for c in C+A+B for l in c}
        free=(set(range(1,n+1))-used)|{n-1,n}
        require(len(free)==m+5 and all(not w>>(v-1)&1 for w in W for v in free),
                'free count')
        for j in (0,M//2,M-1):
            F=C+tuple(c for i,c in enumerate(A) if i!=j)+tuple(c for i,c in enumerate(B) if i!=j)
            for v in free:
                require(all(true(c,W[j]^(1<<(v-1))) for c in F),'free bit')
    return 3


def audit():
    result={'controls':controls(),'partitions':partitions(),'traces':traces()}
    print('F038_UNRESTRICTED_QUADRATIC_CENSUS_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
