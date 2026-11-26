"""Fixed selector-dependent witness programs and exact small layout/residual audits."""
import json
from itertools import combinations,product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_witness_pass_frontier import schedule

PLAN='docs/research/tga-universal/f038-mrax-universal-witness-layout.json'


def pool(n):
    return tuple(tuple(i*b for i,b in zip(I,B))
                 for k in range(1,min(3,n)+1)
                 for I in combinations(range(1,n+1),k)
                 for B in product((-1,1),repeat=k))


def program(n,C):
    require(type(n) is int and n>=1 and all(1<=len(c)<=3 and
            len({abs(l) for l in c})==len(c) and all(0<abs(l)<=n for l in c)
            for c in C),'invalid pool')
    lits=tuple(l for c in C for l in c)
    h=len(lits)
    T=[]
    Q=[]
    for i,c in enumerate(C):
        for j,l in enumerate(c):
            def delta(a,b,p):
                if a==2:
                    return 2
                ok=bool(a) or not p or (bool(b)==(l>0))
                return (0 if ok else 2) if j==len(c)-1 else int(ok)
            T.append(tuple(tuple(delta(a,b,p) for a in range(3) for b in (0,1))
                           for p in (0,1)))
            Q.append(i)
    A=tuple(range(h))
    B=tuple(sorted(A,key=lambda j:(abs(lits[j]),j)))
    prev=None
    for j in B:
        first=abs(lits[j])!=prev
        t=tuple(2 if a==2 else b if first else a if a==b else 2
                for a in range(3) for b in (0,1))
        T.append((t,t))
        Q.append(-1)
        prev=abs(lits[j])
    return A+B,tuple(T),tuple(Q),lits


def run(O,T,Q,p,w):
    a=0
    for j,v in enumerate(O):
        q=Q[j]
        a=T[j][0 if q<0 else p>>q&1][2*a+(w>>v&1)]
    return a!=2


class Circuit:
    def __init__(self,m):
        self.m=m
        self.gates=[]
        self.memo={}
    def literal(self,i,b):
        require(0<=i<self.m,'bad selector')
        return 2+2*i+int(not b)
    def add(self,op,a,b):
        if a>b:
            a,b=b,a
        if a==b:
            return a
        if op=='and':
            if a==0:
                return 0
            if a==1:
                return b
        else:
            if a==0:
                return b
            if a==1:
                return 1
        key=op,a,b
        if key not in self.memo:
            self.memo[key]=2+2*self.m+len(self.gates)
            self.gates.append(key)
        return self.memo[key]
    def eval(self,o,p):
        v=[0,1]
        for i in range(self.m):
            b=p>>i&1
            v.extend((b,1-b))
        for op,a,b in self.gates:
            require(0<=a<len(v) and 0<=b<len(v),'bad gate reference')
            v.append(v[a]&v[b] if op=='and' else v[a]|v[b])
        return bool(v[o])


def compile_pool(n,C,layout):
    O,T,Q,lits=program(n,C)
    steps=schedule(O,len(lits),layout)
    G=Circuit(len(C))
    D={():1}
    for v,F,new,J,occ in steps:
        N={}
        for key,old in D.items():
            for vals in product(range(3),repeat=len(new)):
                S=dict(zip(F,key))
                S.update(zip(new,vals))
                local=0
                for b in (0,1):
                    a=1
                    for j in occ:
                        before=0 if j==0 else S[j-1]
                        ok=[]
                        for p in (0,1):
                            z=T[j][p][2*before+b]
                            ok.append(z!=2 if j==len(O)-1 else z==S[j])
                        if not any(ok):
                            a=0
                            break
                        if ok[0]!=ok[1]:
                            a=G.add('and',a,G.literal(Q[j],ok[1]))
                    local=G.add('or',local,a)
                q=G.add('and',old,local)
                if q:
                    boundary=tuple(S[e] for e in J)
                    N[boundary]=G.add('or',N.get(boundary,0),q)
        D=N
    return G,D.get((),0),max((len(J) for v,F,new,J,occ in steps),default=0)


def sat(C,p,x):
    return all(not(p>>i&1) or any(bool(x>>(abs(l)-1)&1)==(l>0) for l in c)
               for i,c in enumerate(C))


def pools():
    out=[]
    for n,C in ((1,((-1,),(1,))),
                (2,pool(2)),
                (3,((1,),(-2,),(1,2),(-1,3),(-2,-3))),
                (3,((1,2),(1,3),(2,3)))):
        O,T,Q,lits=program(n,C)
        h=len(lits)
        G,o,c=compile_pool(n,C,tuple(range(h)))
        require(c<=2*n+1,'natural layout too wide')
        st=[n,len(C),h,0,0,0,0,0,0,0]
        for p in range(1<<len(C)):
            models=[x for x in range(1<<n) if sat(C,p,x)]
            images={sum(((x>>(abs(l)-1))&1)<<i for i,l in enumerate(lits)) for x in models}
            good={w for w in range(1<<h) if run(O,T,Q,p,w)}
            require(images==good and G.eval(o,p)==bool(good),'universal compiler mismatch')
            st[3]+=1
            st[4]+=1<<n
            st[5]+=1<<h
            st[6]+=bool(good)
            st[7]+=not good
            st[8]+=len(models)
            st[9]+=len(good)
        out.append(st)
    return out


def cut(E,S):
    return sum((S>>u^S>>v)&1 for u,v in E)


def optimal(O,h):
    E=tuple(zip(O,O[1:]))
    D=[0]*(1<<h)
    last=[-1]*(1<<h)
    for S in range(1,1<<h):
        d,v=min((D[S^(1<<v)],v) for v in range(h) if S>>v&1)
        D[S]=max(d,cut(E,S))
        last[S]=v
    S=(1<<h)-1
    order=[]
    while S:
        v=last[S]
        order.append(v)
        S^=1<<v
    order=tuple(reversed(order))
    require(max((len(J) for v,F,new,J,occ in schedule(O,h,order)),default=0)==D[-1],
            'optimal layout reconstruction mismatch')
    return D[-1],order


def layouts():
    out=[]
    for n in (2,3,4):
        C=tuple(combinations(range(1,n+1),2))
        O,T,Q,lits=program(n,C)
        h=len(lits)
        d,L=optimal(O,h)
        natural=max(len(J) for v,F,new,J,occ in schedule(O,h,tuple(range(h))))
        require(n-1<=d<=natural<=2*n+1,'layout bound failed')
        # Check the critical cut of the optimal permutation itself.
        seen=set()
        S=0
        for v in L:
            if len(seen)==n-1 and abs(lits[v]) not in seen:
                require(cut(tuple(zip(O,O[1:])),S)>=n-1,'critical cut failed')
                break
            seen.add(abs(lits[v]))
            S|=1<<v
        else:
            raise ValueError('missing critical cut')
        out.append([n,h,len(O)-1,1<<h,d,natural])
    return out


def residuals():
    out=[]
    for n in (2,3,4):
        B=tuple(c for c in pool(n) if len(c)==2)
        R=[tuple(sat((c,),1,x) for c in B) for x in range(1<<n)]
        require(len(set(R))==1<<n,'residual collision')
        pairs=0
        for a,b in combinations(R,2):
            require(any(x!=y for x,y in zip(a,b)),'undistinguished residuals')
            pairs+=1
        out.append([n,len(B),len(set(R)),len(B)*(1<<n),pairs])
    return out


def controls():
    # A contradictory pair of units may be independently switched off.
    C=((1,),(-1,))
    G,o,c=compile_pool(1,C,(0,1))
    require([G.eval(o,p) for p in range(4)]==[True,True,True,False],
            'selector gating failed')
    try:
        compile_pool(1,C,(0,0))
    except ValueError:
        pass
    else:
        raise ValueError('malformed layout accepted')
    G,o,c=compile_pool(1,(),())
    require(G.eval(o,0) and c==0,'empty pool failed')
    for n in range(1,6):
        U=pool(n)
        require(len(set(U))==len(U) and all(1<=len(c)<=3 for c in U)
                and all(any(abs(l)==i for c in U for l in c) for i in range(1,n+1)),
                'invalid universal pool')
    return 4


def audit():
    result={'pools':pools(),'layouts':layouts(),'residuals':residuals(),'controls':controls()}
    print('F038_MRAX_UNIVERSAL_LAYOUT_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
