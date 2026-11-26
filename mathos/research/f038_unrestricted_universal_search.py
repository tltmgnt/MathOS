"""Direct unrestricted SAT universal search target; bounded interpreter and failure fixtures."""
import json
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool

PLAN='docs/research/tga-universal/f038-unrestricted-universal-search.json'
BUILTINS=('', '0','1','00','01','10','11','000')


def valid(C,n,p,x):
    return type(x) is int and 0<=x<1<<n and all(
        not(p>>j&1) or any(bool(x>>(abs(l)-1)&1)==(l>0) for l in c)
        for j,c in enumerate(C))


def encoded(n,p,C):
    return '1'*n+'0'+''.join(str(p>>j&1) for j in range(len(C)))


def decode_tm(d):
    # 111, unary state count q followed by zero; q*3 transitions.
    # New state in q.bit_length bits (q is halt), write 00/01/10
    # for zero/one/blank, move 00/01/10 for left/stay/right.
    if not d.startswith('111'):
        return None
    j=3
    while j<len(d) and d[j]=='1':
        j+=1
    q=j-3
    if q<1 or j==len(d):
        return None
    j+=1
    b=q.bit_length()
    if len(d)-j!=3*q*(b+4):
        return None
    T=[]
    for _ in range(3*q):
        a=int(d[j:j+b],2)
        w=int(d[j+b:j+b+2],2)
        m=int(d[j+b+2:j+b+4],2)
        if a>q or w>2 or m>2:
            return None
        T.append((a,w,m-1))
        j+=b+4
    return q,T


def tape_run(C,n,p,d,t):
    a=decode_tm(d)
    if a is None:
        return None
    q,T=a
    tape={i:int(v) for i,v in enumerate(encoded(n,p,C))}
    state=head=0
    for _ in range(t):
        state,w,m=T[3*state+tape.get(head,2)]
        if w==2:
            tape.pop(head,None)
        else:
            tape[head]=w
        head+=m
        if state==q:
            bits=[tape.get(head+i,2) for i in range(n)]
            return sum(v<<i for i,v in enumerate(bits)) if all(v<2 for v in bits) else None
    return None


def run_program(C,n,p,d,t):
    if d not in BUILTINS:
        return tape_run(C,n,p,d,t)
    if d=='':
        return None
    if d=='000':
        if t<1<<n:
            return None
        # Charged exhaustive built-in. The allotted budget covers all assignments.
        models=[x for x in range(1<<n) if valid(C,n,p,x)]
        return models[0] if models else None
    x,cost={'0':(0,1),'1':(1,2),'00':(2,3),'01':(3,1),
            '10':(1<<n,1),'11':(p%4,2+p%3)}[d]
    return x if t>=cost else None


def descriptions(s):
    for ell in range(s+1):
        for i in range(1<<ell):
            yield (format(i,'0'+str(ell)+'b') if ell else ''),1<<(s-ell)


def stage(C,n,p,s):
    require(type(n) is int and n>=1 and type(s) is int and s>=0
            and type(p) is int and 0<=p<1<<len(C),'invalid stage input')
    w=None
    count=native=0
    for d,t in descriptions(s):
        x=run_program(C,n,p,d,t)
        count+=1
        native+=d in BUILTINS
        if valid(C,n,p,x) and w is None:
            w=x
    require(count==(1<<(s+1))-1,'description count failed')
    return w,count,native


def universal(n,p):
    C=pool(n)
    s=0
    while True:
        w,_,_=stage(C,n,p,s)
        if w is not None:
            return w,s
        s+=1


def first_bad(n,s):
    C=pool(n)
    for p in range(1<<len(C)):
        if stage(C,n,p,s)[0] is None:
            for x in range(1<<n):
                if valid(C,n,p,x):
                    return p,x
    return None


def finite_cnf(C,n,solved):
    # Deliberately truth-table-based finite fixture, NOT a polytime compiler.
    N=len(C)
    h=N+n
    G=[tuple([-j-1]+[N+abs(l) if l>0 else -(N+abs(l)) for l in c])
       for j,c in enumerate(C)]
    require(all(len(c)<=3 for c in G),'fixture requires width-two source clauses')
    gates=[]
    for p in solved:
        L=[-(j+1) if p>>j&1 else j+1 for j in range(N)]
        a=L[0]
        for b in L[1:]:
            h+=1
            y=h
            G.extend(((-a,y),(-b,y),(a,b,-y)))
            gates.append((a,b,y))
            a=y
        G.append((a,))
    return h,tuple(G),tuple(gates)


def extend(p,N,n,x,G):
    w=p|(x<<N)
    def lit(l):
        return bool(w>>(abs(l)-1)&1)==(l>0)
    for a,b,y in G:
        if lit(a) or lit(b):
            w|=1<<(y-1)
    return w


def sat_cnf(F,w):
    return all(any(bool(w>>(abs(l)-1)&1)==(l>0) for l in c) for c in F)


def audit_schedule():
    n=2
    C=pool(n)
    N=len(C)
    require(N==8,'unexpected fixture pool')
    st=[0]*7
    first=[0]*7
    solved=[set() for _ in range(7)]
    models=[]
    for p in range(1<<N):
        W=tuple(x for x in range(1<<n) if valid(C,n,p,x))
        models.append(W)
        f=None
        for s in range(7):
            w,count,native=stage(C,n,p,s)
            st[2]+=1
            st[3]+=native
            direct=any(valid(C,n,p,run_program(C,n,p,d,1<<(s-len(d))))
                       for d in BUILTINS if len(d)<=s)
            require((w is not None)==direct,'bounded reference mismatch')
            if w is not None:
                solved[s].add(p)
                require(w in W,'unverified acceptance')
                if f is None:
                    f=s
            st[4]+=w is not None
            st[5]+=bool(W) and w is None
        require((f is not None)==bool(W),'missing SAT fixture')
        if f is not None:
            first[f]+=1
            require(universal(n,p)[1]==f,'universal stage mismatch')
        st[0]+=1
        st[1]+=bool(W)
        st[6]+=len(W)
    rows=[]
    for s,S in enumerate(solved):
        h,F,G=finite_cnf(C,n,sorted(S))
        bad=pairs=checks=0
        for p,W in enumerate(models):
            bad+=bool(W) and p not in S
            pairs+=len(W) if p not in S else 0
            for x in range(1<<n):
                w=extend(p,N,n,x,G)
                require(sat_cnf(F,w)==(x in W and p not in S),
                        'failure CNF mismatch')
                checks+=1
        b=first_bad(n,s)
        require((b is not None)==bool(bad),'counterexample search mismatch')
        if b is not None:
            p,x=b
            require(x in models[p] and p not in S,'bad witness replay failed')
        rows.append([s,(1<<(s+1))-1,len(S),bad,pairs,h,len(F),checks])
    return st,first,rows


def encode_tm(T,q):
    b=q.bit_length()
    return '111'+'1'*q+'0'+''.join(format(a,'0'+str(b)+'b')+format(w,'02b')+
                                 format(m+1,'02b') for a,w,m in T)


def controls():
    C=pool(2)
    # General tape machine writes two zeros and halts at their first bit.
    T=[(1,0,1)]*3+[(2,0,-1)]*3+[(3,0,0)]*3
    d=encode_tm(T,3)
    require(decode_tm(d)==(3,T) and tape_run(C,2,0,d,2) is None
            and tape_run(C,2,0,d,3)==0,'generic tape simulation or clock failed')
    # A generic one-state machine can loop; timeout must not accept.
    d=encode_tm([(0,1,0)]*3,1)
    require(tape_run(C,2,0,d,100) is None,'loop did not time out')
    require(decode_tm('111') is None and decode_tm(d+'0') is None,'invalid code accepted')
    require(not valid(C,2,0,run_program(C,2,0,'10',1)) and
            stage(C,2,3,6)[0] is None,'invalid witness or UNSAT accepted')
    require(first_bad(2,0) is not None and first_bad(2,4) is None,'failure set control')
    return 5


def audit():
    st,hist,rows=audit_schedule()
    result={'schedule':st,'first':hist,'failures':rows,'controls':controls()}
    print('F038_UNRESTRICTED_SEARCH_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
