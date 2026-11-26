"""Repeated witness passes: exact symbolic frontier compilation and SAT reduction."""
import json
from itertools import permutations,product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax

PLAN='docs/research/tga-universal/f038-mrax-witness-pass-frontier.json'


def run(O,T,W,initial,accept,x,w):
    a=initial
    for j,v in enumerate(O):
        a=T[j][x][2*a+((w>>v)&1)]
    return a in accept


def schedule(O,h,layout):
    require(tuple(sorted(layout))==tuple(range(h)),'bad layout')
    require(all(0<=v<h for v in O),'bad occurrence')
    E=tuple(zip(O,O[1:]))
    done=set()
    F=()
    steps=[]
    for v in layout:
        J=tuple(i for i,(a,b) in enumerate(E) if v in (a,b))
        new=tuple(i for i in J if i not in F)
        done.add(v)
        G=tuple(i for i,(a,b) in enumerate(E) if (a in done)!=(b in done))
        occ=tuple(j for j,a in enumerate(O) if a==v)
        steps.append((v,F,new,G,occ))
        F=G
    require(not F,'nonempty final frontier')
    return tuple(steps)


def local(O,T,W,initial,accept,occ,states,b,x):
    for j in occ:
        a=initial if j==0 else states[j-1]
        z=T[j][x][2*a+b]
        if j==len(O)-1:
            if z not in accept:
                return False
        elif states[j]!=z:
            return False
    return True


class Circuit:
    # Wires 0=false, 1=true, 2=x, 3=not x.
    def __init__(self):
        self.gates=[]
        self.memo={}
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
        k=op,a,b
        if k not in self.memo:
            self.memo[k]=4+len(self.gates)
            self.gates.append(k)
        return self.memo[k]
    def evaluate(self,o,x):
        V=[0,1,x,1-x]
        for op,a,b in self.gates:
            require(0<=a<len(V) and 0<=b<len(V),'bad circuit reference')
            V.append(V[a]&V[b] if op=='and' else V[a]|V[b])
        return bool(V[o])


def validate(O,T,W,initial,accept,h,layout):
    require(type(W) is int and W>=1 and 0<=initial<W and all(0<=a<W for a in accept),
            'bad state dimensions')
    require(len(O)==len(T) and all(len(t)==2 and all(len(u)==2*W and
            all(type(v) is int and 0<=v<W for v in u) for u in t) for t in T),'bad transitions')
    if h:
        require(len(O)%h==0 and all(sorted(O[j:j+h])==list(range(h))
                for j in range(0,len(O),h)) and bool(O),'not full passes')
    else:
        require(not O,'unexpected occurrence')
    return schedule(O,h,layout)


def compile_program(O,T,W,initial,accept,h,layout):
    steps=validate(O,T,W,initial,accept,h,layout)
    C=Circuit()
    D={():1}
    for v,F,new,G,occ in steps:
        N={}
        for key,old in D.items():
            for vals in product(range(W),repeat=len(new)):
                S=dict(zip(F,key))
                S.update(zip(new,vals))
                ok=tuple(any(local(O,T,W,initial,accept,occ,S,b,x)
                        for b in (0,1)) for x in (0,1))
                pred={(False,False):0,(True,True):1,(False,True):2,(True,False):3}[ok]
                q=C.add('and',old,pred)
                if q:
                    key2=tuple(S[i] for i in G)
                    N[key2]=C.add('or',N.get(key2,0),q)
        D=N
    return C,(D.get((),0) if h else int(initial in accept)),max((len(G) for v,F,new,G,occ in steps),default=0)


def witness(O,T,W,initial,accept,h,layout,x):
    steps=validate(O,T,W,initial,accept,h,layout)
    if not h:
        return 0 if initial in accept else None
    D={():0}
    for v,F,new,G,occ in steps:
        N={}
        for key,w in D.items():
            for vals in product(range(W),repeat=len(new)):
                S=dict(zip(F,key))
                S.update(zip(new,vals))
                b=next((b for b in (0,1) if local(O,T,W,initial,accept,occ,S,b,x)),None)
                if b is not None:
                    N.setdefault(tuple(S[i] for i in G),w|(b<<v))
        D=N
    w=D.get(())
    require(w is None or run(O,T,W,initial,accept,x,w),'invalid reconstructed witness')
    return w


def passes():
    out=[]
    for h in (3,4):
        st=[h,0,0,0,0,0,0,0,0,0]
        layout=tuple(range(h))
        for P in permutations(layout):
            O=layout+P
            for seed in range(64):
                T=tuple(tuple(tuple((((seed*(2*j+1)+7*j+x*(j+3))^
                       (seed>>(j%6)))&15)>>i&1 for i in range(4))
                       for x in (0,1)) for j in range(len(O)))
                C,o,c=compile_program(O,T,2,0,{1},h,layout)
                st[1]+=1
                st[8]+=c
                st[9]=max(st[9],c)
                for x in (0,1):
                    good=[w for w in range(1<<h) if run(O,T,2,0,{1},x,w)]
                    w=witness(O,T,2,0,{1},h,layout,x)
                    require(C.evaluate(o,x)==bool(good) and ((w is not None)==bool(good))
                            and (w is None or w in good),'frontier compilation mismatch')
                    st[2]+=1
                    st[3]+=1<<h
                    st[4]+=bool(good)
                    st[5]+=not good
                    st[6]+=len(good)
                    st[7]+=len(good)==1
        out.append(st)
    return out


def from_cnf(F):
    require(all(c and all(l!=0 for l in c) for c in F),'nonempty clauses required')
    lits=tuple(l for c in F for l in c)
    h=len(lits)
    ends=set()
    i=0
    for c in F:
        i+=len(c)
        ends.add(i-1)
    T=[]
    for j,l in enumerate(lits):
        def delta(a,b):
            if a==2:
                return 2
            good=bool(a) or (bool(b)==(l>0))
            return (0 if good else 2) if j in ends else int(good)
        t=tuple(delta(a,b) for a in range(3) for b in (0,1))
        T.append((t,t))
    P=tuple(sorted(range(h),key=lambda i:(abs(lits[i]),i)))
    prev=None
    for j in P:
        first=abs(lits[j])!=prev
        t=tuple(2 if a==2 else b if first else a if a==b else 2
                for a in range(3) for b in (0,1))
        T.append((t,t))
        prev=abs(lits[j])
    return tuple(range(h))+P,tuple(T),h


def source_sat(F,x):
    return all(any(bool(x>>(abs(l)-1)&1)==(l>0) for l in c) for c in F)


def cnf():
    pool=((-1,),(1,),(-2,),(2,),(-1,2),(1,-2),(-1,-2,3),(1,2,-3))
    st=[0]*9
    for mask in range(256):
        F=tuple(c for i,c in enumerate(pool) if mask>>i&1)
        O,T,h=from_cnf(F)
        good=[x for x in range(8) if source_sat(F,x)]
        lits=tuple(l for c in F for l in c)
        images={sum(((x>>(abs(l)-1))&1)<<i for i,l in enumerate(lits)) for x in good}
        found={w for w in range(1<<h) if run(O,T,3,0,{0,1},0,w)}
        require(images==found,'occurrence witness mismatch')
        if h<=5:
            C,o,c=compile_program(O,T,3,0,{0,1},h,tuple(range(h)))
            w=witness(O,T,3,0,{0,1},h,tuple(range(h)),0)
            require(C.evaluate(o,0)==bool(found) and C.evaluate(o,1)==bool(found)
                    and ((w is not None)==bool(found)) and (w is None or w in found),
                    'CNF projection mismatch')
            st[7]+=1
        st[0]+=1
        st[1]+=8
        st[2]+=1<<h
        st[3]+=len(good)
        st[4]+=len(found)
        st[5]+=bool(found)
        st[6]+=not found
        st[8]=max(st[8],h)
    return st


def controls():
    # One witness read twice: the intermediate edge is a self-loop.
    O=(0,0)
    T=(((0,1,0,1),)*2,((0,1,1,0),)*2)
    C,o,c=compile_program(O,T,2,0,{1},1,(0,))
    require(not C.evaluate(o,0) and c==0 and witness(O,T,2,0,{1},1,(0,),0) is None,
            'inconsistent repeated-bit witness accepted')
    # A common order with r=3 has at most 2r-1 crossing edges.
    O=tuple(range(7))*3
    require(max(len(G) for v,F,new,G,occ in schedule(O,7,tuple(range(7))))<=5,
            'common-order bound failed')
    try:
        schedule((0,1),2,(0,0))
    except ValueError:
        pass
    else:
        raise ValueError('invalid layout accepted')
    C,o,c=compile_program((),(),3,0,{0},0,())
    require(C.evaluate(o,0) and witness((),(),3,0,{0},0,(),0)==0,
            'empty witness case failed')
    return 4


def audit():
    result={'passes':passes(),'cnf':cnf(),'controls':controls()}
    print('F038_MRAX_WITNESS_FRONTIER_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
