"""Same-U quasilinear-size CNF via batched sparse tape traces and rejection certificates."""
import json
from itertools import product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import (
    encoded,valid,stage,encode_tm,decode_tm,tape_run)
from mathos.research.f038_unrestricted_prefix_adversary import tape_codes
from mathos.research.f038_unrestricted_symbolic_counterexamples import (
    Circuit,lit,verify,stage_circuit,fixture)

PLAN='docs/research/tga-universal/f038-unrestricted-trace-cnf.json'


def width(n):
    return max(1,(n-1).bit_length())


def bits(x,b):
    return [(x>>i)&1 for i in range(b)]


class Build:
    def __init__(self,G,start):
        self.G=G
        self.next=start
        self.checks=[]
    def const(self,x,b):
        return tuple(self.G.one if v else -self.G.one for v in bits(x,b))
    def free(self,b):
        out=tuple(range(self.next,self.next+b))
        self.next+=b
        require(self.next<=self.G.inputs+1,'free input overflow')
        return out
    def xor(self,a,b):
        G=self.G
        return G.OR(G.AND(a,-b),G.AND(-a,b))
    def eq(self,A,B):
        require(len(A)==len(B),'equality width')
        return self.G.all(-self.xor(a,b) for a,b in zip(A,B))
    def lt(self,A,B):
        require(len(A)==len(B),'comparison width')
        G=self.G
        v=-G.one
        for a,b in zip(A,B):
            v=G.OR(G.AND(-a,b),G.AND(-self.xor(a,b),v))
        return v
    def mux(self,c,A,B):
        require(len(A)==len(B),'mux width')
        G=self.G
        return tuple(G.OR(G.AND(c,a),G.AND(-c,b)) for a,b in zip(A,B))
    def add(self,A,B):
        require(len(A)==len(B),'addition width')
        G=self.G
        c=-G.one
        V=[]
        for a,b in zip(A,B):
            ab=self.xor(a,b)
            V.append(self.xor(ab,c))
            c=G.OR(G.AND(a,b),G.AND(ab,c))
        return tuple(V)
    def sort(self,rows):
        """Bitonic sorting, strict comparison; a high padding bit separates dummies."""
        if not rows:
            return []
        c=self.G.one
        k=len(rows[0][0])
        d=len(rows[0][1])
        R=[K+(-c,)+V for K,V in rows]
        N=1<<(len(R)-1).bit_length()
        R.extend([(c,)*(k+1)+(-c,)*d]*(N-len(R)))
        step=2
        while step<=N:
            j=step//2
            while j:
                for i in range(N):
                    z=i^j
                    if z<=i:
                        continue
                    a,b=R[i],R[z]
                    swap=self.lt(b[:k+1],a[:k+1]) if (i&step)==0 else self.lt(a[:k+1],b[:k+1])
                    R[i]=self.mux(swap,b,a)
                    R[z]=self.mux(swap,a,b)
                j//=2
            step*=2
        return [(r[:k],r[k+1:]) for r in R[:len(rows)]]
    def lookup(self,table,queries):
        """Table keys are distinct; every query must have an equal table payload."""
        G=self.G
        if not queries:
            return
        R=self.sort([((-G.one,)+k,v) for k,v in table]+
                    [((G.one,)+k,v) for k,v in queries])
        prev=None
        for k,v in R:
            ok=-G.one if prev is None else G.AND(self.eq(k[1:],prev[0][1:]),self.eq(v,prev[1]))
            self.checks.append(G.OR(-k[0],ok))
            prev=k,v
    def memory(self,rows,timebits):
        R=self.sort(rows)
        prev=None
        for k,v in R:
            rd,wr,init=v[:2],v[2:4],v[4:6]
            same=-self.G.one if prev is None else self.eq(k[timebits:],prev[0][timebits:])
            prior=init if prev is None else prev[1][2:4]
            self.checks.append(self.eq(rd,self.mux(same,prior,init)))
            prev=k,v


def clause_data(c,n):
    V=list(c)+[c[-1]]*(3-len(c))
    return [z for l in V for z in bits(abs(l)-1,width(n))+[int(l<0)]]


def compile_batch(n,programs,s=None,source=False):
    """Programs are explicit (description,clock) pairs. All are required to fail.

    If s is supplied, also check the exact short built-ins at that stage.
    source=True additionally verifies the independent proposed source witness.
    """
    C=pool(n)
    N=len(C)
    L=n+1+N
    vb,cb=width(n),width(N)
    # Read/init bits per access; one blank offset, clause ID and full clause payload.
    extra=sum(4*(t+4)+vb+cb+1+3*(vb+1) for d,t in programs)
    G=Circuit(N+n+extra)
    P=tuple(range(1,N+1))
    X=tuple(range(N+1,N+n+1))
    B=Build(G,N+n+1)
    c=G.one
    if source:
        B.checks.append(verify(G,C,P,X))
    if s is not None:
        require(s<n+3,'active exhaustive fallback must be handled by wrapper')
        # All short built-ins saturate by stage 4 except exhaustive, inactive here.
        B.checks.append(-stage_circuit(G,C,n,P,min(s,19)))
    if not programs:
        return G,G.all(B.checks)
    M=max(t for d,t in programs)
    require(M>=1,'invalid clock')
    ab=max(2*M+n+1,M+L+1).bit_length()
    tb=(M+4).bit_length()
    db=width(len(programs))
    zero=B.const(0,ab)
    initial=[B.const(1,2)]*n+[B.const(0,2)]+[(p,-c) for p in P]
    initial_table=[(B.const(M+i,ab),v) for i,v in enumerate(initial)]
    initial_table.append((B.const(M+L,ab),B.const(2,2)))
    clause_table=[(B.const(j,cb),(P[j],)+tuple(c if v else -c for v in clause_data(cl,n)))
                  for j,cl in enumerate(C)]
    mem,init_queries,clause_queries=[],[],[]
    for pid,(d,t) in enumerate(programs):
        parsed=decode_tm(d)
        require(parsed is not None and type(t) is int and t>=1,'invalid trace program')
        q,T=parsed
        state=(c,)+(-c,)*q
        head=B.const(M,ab)
        def read():
            rd,ini=B.free(2),B.free(2)
            B.checks.append(-G.AND(rd[0],rd[1]))
            return rd,ini
        def record(i,addr,rd,wr,ini):
            mem.append((B.const(i,tb)+addr+B.const(pid,db),rd+wr+ini))
            inside=G.AND(-B.lt(addr,B.const(M,ab)),B.lt(addr,B.const(M+L,ab)))
            key=B.mux(inside,addr,B.const(M+L,ab))
            init_queries.append((key,ini))
        for i in range(t):
            rd,ini=read()
            ev=[(G.AND(state[a],B.eq(rd,B.const(u,2))),T[3*a+u])
                for a in range(q) for u in range(3)]
            hold=state[q]
            wr=tuple(G.OR(G.AND(hold,rd[j]),G.any(v for v,(_,w,_) in ev if w>>j&1))
                     for j in range(2))
            record(i,head,rd,wr,ini)
            left=G.any(v for v,(_,_,m) in ev if m==-1)
            right=G.any(v for v,(_,_,m) in ev if m==1)
            head=B.mux(left,B.add(head,B.const((1<<ab)-1,ab)),
                       B.mux(right,B.add(head,B.const(1,ab)),head))
            state=tuple(G.OR(hold if a==q else -c,G.any(v for v,(b,_,_) in ev if a==b))
                        for a in range(q+1))
        blank=B.free(vb)
        if n<1<<vb:
            B.checks.append(B.lt(blank,B.const(n,vb)))
        idx=B.free(cb)
        data=B.free(1+3*(vb+1))
        clause_queries.append((idx,data))
        offsets=[blank]+[data[1+j*(vb+1):1+j*(vb+1)+vb] for j in range(3)]
        reads=[]
        for j,off in enumerate(offsets):
            addr=B.add(head,off+(-c,)*(ab-vb))
            rd,ini=read()
            record(t+j,addr,rd,rd,ini)
            reads.append(rd)
        blank_bad=B.eq(reads[0],B.const(2,2))
        clause_bad=G.all([data[0]]+[B.eq(reads[j+1],(data[1+j*(vb+1)+vb],-c))
                                      for j in range(3)])
        B.checks.append(G.any((-state[q],blank_bad,clause_bad)))
    B.memory(mem,tb)
    B.lookup(initial_table,init_queries)
    B.lookup(clause_table,clause_queries)
    require(B.next==G.inputs+1,'unused certificate inputs')
    return G,G.all(B.checks)


def compile_bad(n,s):
    require(type(n) is int and n>=1 and type(s) is int and s>=0,'invalid dimensions')
    if s>=n+3:
        # On every satisfiable input the actual exhaustive built-in succeeds.
        G=Circuit(len(pool(n))+n)
        return G,-G.one
    programs=[(d,1<<(s-len(d))) for d in tape_codes(s)]
    return compile_batch(n,programs,s,True)


def certificate(n,C,p,x,programs):
    """Concrete certificate constructor for bounded fixtures, not a bad-instance finder."""
    S=list(map(int,encoded(n,p,C)))
    W=bits(p,len(C))+bits(x,n)
    kinds=[]
    for d,t in programs:
        q,T=decode_tm(d)
        V=dict(enumerate(S))
        state=head=0
        def read(h):
            return V.get(h,2)
        def add_read(h):
            W.extend(bits(read(h),2)+bits(S[h] if 0<=h<len(S) else 2,2))
        for _ in range(t):
            add_read(head)
            if state!=q:
                state,w,m=T[3*state+read(head)]
                V[head]=w
                head+=m
        X=[read(head+i) for i in range(n)]
        blank=next((i for i,v in enumerate(X) if v==2),0)
        idx=0
        if state!=q:
            kind=0
        elif 2 in X:
            kind=1
        else:
            w=sum(v<<i for i,v in enumerate(X))
            bad=[j for j,c in enumerate(C) if p>>j&1 and
                 all(bool(w>>(abs(l)-1)&1)!=(l>0) for l in c)]
            kind=2 if bad else 3
            idx=bad[0] if bad else 0
        kinds.append(kind)
        W.extend(bits(blank,width(n))+bits(idx,width(len(C)))+
                 [int(bool(p>>idx&1))]+clause_data(C[idx],n))
        add_read(head+blank)
        for l in list(C[idx])+[C[idx][-1]]*(3-len(C[idx])):
            add_read(head+abs(l)-1)
    return W,kinds


def batches():
    rows=[]
    for n in (1,2):
        C=pool(n)
        N=len(C)
        for t in (1,4):
            st=[n,t,0,0,0,0,0,0,0,0]
            for seed in range(8):
                D=[(encode_tm(fixture(q,seed),q),t) for q in (1,2,3)]
                G,out=compile_batch(n,D)
                v,F=G.cnf(out)
                require(all(1<=len(c)<=3 for c in F),'CNF width failed')
                W=[0]*G.inputs
                mask=(1<<(1<<N))-1
                wanted=0
                st[2]+=1
                for p in range(1<<N):
                    a,K=certificate(n,C,p,0,D)
                    require(len(a)==G.inputs,'certificate width')
                    for i,b in enumerate(a):
                        W[i]|=b<<p
                    for (d,t0),k in zip(D,K):
                        got=valid(C,n,p,tape_run(C,n,p,d,t0))
                        require(got==(k==3),'concrete rejection classification')
                        st[4]+=1
                        st[5+k]+=1
                    ok=3 not in K
                    wanted|=int(ok)<<p
                    st[3]+=1
                    st[9]+=ok
                V=G.evaluate(W,mask)
                require(lit(V,out,mask)==wanted,'batched trace circuit mismatch')
                # Definitional clauses hold on every gate extension; forced output
                # holds exactly for the selectors whose whole batch fails.
                got=mask
                for cl in F:
                    z=0
                    for l in cl:
                        z|=lit(V,l,mask)
                    got&=z
                require(got==wanted,'batched trace CNF mismatch')
            rows.append(st)
    return rows


def stages():
    rows=[]
    for n in (1,2):
        C=pool(n)
        N=len(C)
        for s in range(7):
            G,out=compile_bad(n,s)
            st=[n,s,0,0,0]
            for p in range(1<<N):
                success=stage(C,n,p,s)[0] is not None
                for x in range(1<<n):
                    a=bits(p,N)+bits(x,n)
                    got=bool(lit(G.evaluate(a),out))
                    want=valid(C,n,p,x) and not success
                    require(got==want,'full small-stage mismatch')
                    st[2]+=1
                    st[3]+=want
                    st[4]+=got
            rows.append(st)
    return rows


def controls():
    # Arbitrary keys (ties included) and attached row payloads.
    G=Circuit(6)
    B=Build(G,7)
    R=B.sort([((1,2),B.const(0,2)),((3,4),B.const(1,2)),((5,6),B.const(2,2))])
    for keys in product(range(4),repeat=3):
        V=G.evaluate([b for k in keys for b in bits(k,2)])
        rows=[(sum(lit(V,a)<<i for i,a in enumerate(k)),
               sum(lit(V,a)<<i for i,a in enumerate(v))) for k,v in R]
        require([k for k,_ in rows]==sorted(keys) and
                sorted(rows)==sorted((k,i) for i,k in enumerate(keys)),'sort payload lost')
    C=pool(1)
    D=[(encode_tm([(0,1,0)]*3,1),2)]
    G,out=compile_batch(1,D)
    W,K=certificate(1,C,0,0,D)
    require(K==[0] and lit(G.evaluate(W),out),'timeout not certified')
    for j in (len(C)+1,len(C)+1+2):
        Z=W.copy()
        Z[j]^=1
        require(not lit(G.evaluate(Z),out),'forged read/initial symbol accepted')
    D=[(encode_tm([(1,1,0)]*3,1),1)]
    G,out=compile_batch(1,D)
    W,K=certificate(1,C,0,0,D)
    require(K==[3] and not lit(G.evaluate(W),out),'valid output falsely rejected')
    # Try every legitimate clause index and blank offset, with honest reads,
    # on a successful one-bit output. None can certify rejection.
    vb,cb=width(1),width(len(C))
    pos=len(C)+1+4
    for idx in range(len(C)):
        Z=W.copy()
        Z[pos:pos+vb+cb+1+3*(vb+1)]=[0]+bits(idx,cb)+[0]+clause_data(C[idx],1)
        require(not lit(G.evaluate(Z),out),'unselected clause accepted as rejection')
    G,out=compile_bad(1,20)
    require(out==-G.one,'active fallback not rejected')
    return 5


def audit():
    result={'batches':batches(),'stages':stages(),'controls':controls()}
    print('F038_UNRESTRICTED_TRACE_CNF_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
