"""Finite nondeterministic ranges and bit-witness/advice projection audit."""
import json
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research import f038_circuit_range_avoidance as A

PLAN='docs/research/tga-universal/f038-mrax-bit-witness-consistency.json'


def project(word,h,m):
    block=1<<h
    mask=(1<<block)-1
    return sum(int(bool((word>>(i*block))&mask))<<i for i in range(m))


def nd_range(n,h,s,m):
    require(n>=1 and h>=0 and s>=0 and 1<=m<=1<<n,'invalid dimensions')
    # Witness bits are the low h bits of the binary ordered input.
    R=A.available(n+h,s,m<<h)
    return {project(v,h,m) for v in R}


def ranges():
    out=[]
    for n,h,s,m in ((2,0,1,4),(3,0,2,8),(3,1,1,8),(3,1,2,8),(3,2,2,8),(4,1,1,10)):
        R=nd_range(n,h,s,m)
        count,outputs=A.syntax_counts(n+h,s)
        gap=A.first_missing(R,m)
        require(A.greedy(R,m)==gap,'wrong missing word')
        require(A.available(n,s,m)<=R,'deterministic range not contained')
        M,B=A.count_bound(n+h,s)
        require(len(R)<=outputs<=B<1<<M,'counting bound failed')
        out.append([n,h,s,m,count,outputs,len(R),gap])
    return out


def labels(v,a,x):
    # Each witness has two possible labels. OR the two label masks.
    k=8*a+4*x
    return ((v>>k)&3)|((v>>(k+2))&3)


def relations():
    st=[0]*9
    for v in range(1<<16):
        A0=tuple(labels(v,0,x) for x in (0,1))
        A1=tuple(labels(v,1,x) for x in (0,1))
        U=tuple(a|b for a,b in zip(A0,A1))
        total=all(U)
        consistent=all(z!=3 for z in U)
        good0=all(z in (1,2) for z in A0)
        good1=all(z in (1,2) for z in A1)
        # Check projection against a separate tuple semantics.
        for x in (0,1):
            bits={b for a in (0,1) for w in (0,1) for b in (0,1)
                  if v>>(8*a+4*x+2*w+b)&1}
            require(U[x]==sum(1<<b for b in bits),'label union mismatch')
        st[0]+=1
        st[1]+=total
        st[2]+=consistent
        st[3]+=total and consistent
        st[4]+=good0 and good1
        st[5]+=good0 or good1
        st[6]+=good0 and good1 and A0!=A1
        st[7]+=(good0 or good1) and not consistent
        st[8]+=all(z!=3 for z in A0+A1) and not consistent
    return st


def controls():
    # Exhaust all predicates on two witness bits: always-0 plus optional 1.
    for mask in range(16):
        S={0}|{1 for w in range(4) if mask>>w&1}
        require((len(S)==1)==(mask==0),'consistency reduction failed')
    # Exhaust all predicates on one x bit and two witness bits.
    for mask in range(256):
        S=[{1 for w in range(4) if mask>>(4*x+w)&1} for x in (0,1)]
        require(all(len(z)<=1 for z in S),'totality fixture inconsistent')
        require(all(S)==all((mask>>(4*x))&15 for x in (0,1)),'totality reduction failed')
    # Different individually total advice functions need not agree.
    v=sum(1<<(8*a+4*x+a) for a in (0,1) for x in (0,1))
    require(all(labels(v,a,x)==1<<a for a in (0,1) for x in (0,1)),
            'advice counterexample failed')
    require(all(labels(v,0,x)|labels(v,1,x)==3 for x in (0,1)),
            'cross-advice conflict missing')
    # existential witness projection: x AND w with witness low bit.
    require(project(8,1,2)==2 and project(0,1,2)==0 and project(15,1,2)==3,
            'witness projection failed')
    return 4


def audit():
    result={'ranges':ranges(),'relations':relations(),'controls':controls()}
    print('F038_MRAX_BIT_WITNESS_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
